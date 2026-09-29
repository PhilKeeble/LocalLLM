"""Repeatable retrieval quality checks; generated distractors never enter the live KB."""
import json
from pathlib import Path
import shutil
import tempfile
import time
from server import Index, CHUNK_CHARS

CASES = [
    ("cpp", "Write a C++17 utility that reads integer records and rejects malformed input.", ["cpp-coding-standard"], "input-error:"),
    ("parser", "Review a C++ binary parser for hostile lengths, huge counts and truncated headers.", ["cpp-coding-standard"], "remaining / element_size"),
    ("ownership", "Does a string_view extend the lifetime of its storage? How should exception cleanup work?", ["cpp-coding-standard"], "does not extend"),
    ("rva", "Map RVA 0x2120 using VirtualAddress 0x2000 PointerToRawData 0x600 SizeOfRawData 0x400. What about 0x2500?", ["pe-headers-sections"], "0x720"),
    ("imports", "An export address points inside the export directory. Is it code or a forwarder string?", ["pe-headers-sections"], "forwarder"),
    ("permissions", "Decode section Characteristics 0xC0000040 and VirtualProtect 0x40.", ["pe-headers-sections"], "PAGE_EXECUTE_READWRITE"),
    ("ambiguous", "An analyst recorded permission 0x20 beside a region. Can I conclude it is writable?", ["pe-headers-sections"], "UNKNOWN"),
    ("triage", "Plan static triage of an unknown PE without executing the specimen. Keep an evidence ledger.", ["pe-static-triage"], "Do not execute"),
]
NOISE = [
    ("cpp-build", "C++ compiler build configuration", "C++ compiler flags build caches include paths and linker settings. This note does not cover input parsing or resource ownership."),
    ("pe-history", "PE training course schedule", "Windows PE reverse-engineering classroom schedule and exercise logistics. Imports exports sections and memory are lecture names, not technical findings."),
    ("memory-hardware", "Memory hardware inventory", "Read write execute benchmark labels on a Windows workstation inventory. Page size and permissions were not measured."),
    ("project-admin", "Project notes archive", "Binary parser project planning and code review meeting attendance. Length of meeting and count of participants are administrative data."),
    ("unrelated", "Garden irrigation", "Soil watering seed trays and seasonal planting."),
]

def run():
    reports = []
    with tempfile.TemporaryDirectory(prefix="kb-growth-") as tmp:
        root = Path(tmp)
        docs = root / "documents"
        shutil.copytree(Path(__file__).resolve().parent.parent / "knowledge", docs)
        for count in (0, 100, 1000):
            noise = docs / "notes" / "scale-fixtures"
            noise.mkdir(parents=True, exist_ok=True)
            for n in range(count):
                topic, title, body = NOISE[n % len(NOISE)]
                (noise / f"noise-{n:04}.md").write_text(
                    f"---\nid: noise-{n:04}\ntitle: {title}\nkind: note\ntopics: [{topic}]\n---\n# {title}\n{body}\nFixture {n}.\n", encoding="utf8")
            start = time.perf_counter()
            index = Index(docs, root / f"index-{count}.sqlite3")
            assert index.error is None, index.error
            rows = []
            for name, query, expected, phrase in CASES:
                start_query = time.perf_counter()
                result = index.search({"query": query, "limit": 1, "context_limit": 8})
                selected = result["context_matches"]
                ids = list(dict.fromkeys(m["source_id"] for m in sorted(selected, key=lambda m: m["rank"])))
                text = "\n".join(m["text"] for m in selected)
                distraction = sum(m["source_id"].startswith("noise-") for m in selected)
                rows.append(dict(case=name, passed=all(s in ids for s in expected) and phrase.lower() in text.lower() and distraction <= 3,
                                 expected=expected, selected=ids, evidence_present=phrase.lower() in text.lower(),
                                 passages=len(selected), distractor_passages=distraction, characters=len(text), matches=result["total"],
                                 scores=[dict(source=m["source_id"], score=m["score"]) for m in sorted(selected, key=lambda m: m["rank"])],
                                 latency_ms=round((time.perf_counter()-start_query)*1000, 2)))
                assert len(selected) <= 8
                assert all(len(m["text"]) <= CHUNK_CHARS for m in selected)
            reports.append(dict(distractors=count, documents=index.status()["documents"],
                                elapsed_seconds=round(time.perf_counter()-start, 3), cases=rows))
            index.close()
    print(json.dumps(reports, indent=2))
    return all(row["passed"] for report in reports for row in report["cases"])

if __name__ == "__main__":
    raise SystemExit(0 if run() else 1)
