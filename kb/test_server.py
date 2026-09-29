import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from server import CHUNK_CHARS, Index, RequestError, chunks, serve


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.docs = root / "documents"
        shutil.copytree(Path(__file__).resolve().parent.parent / "knowledge", self.docs)
        self.index = Index(self.docs, root / "index.sqlite3")

    def tearDown(self):
        self.index.close()
        self.temp.cleanup()

    def test_both_unprompted_topics_and_no_match(self):
        cpp = self.index.search({"query": "Write a C++17 command-line program that reads integer records and reports malformed input", "limit": 20})
        content = "\n".join(m["text"] for m in cpp["matches"])
        self.assertIn("RAII", content)
        self.assertIn("input-error:", content)
        self.assertIn("Do not wrap every individual call", content)
        pe = self.index.search({"query": "PE section Characteristics 0x20 and VirtualProtect 0x40", "limit": 20})
        content = "\n".join(m["text"] for m in pe["matches"])
        self.assertIn("IMAGE_SCN_CNT_CODE", content)
        self.assertIn("PAGE_EXECUTE_READWRITE", content)
        self.assertEqual(self.index.search({"query": "weather Reykjavik tomorrow"})["total"], 0)

    def test_complete_stable_pagination_and_coordinates(self):
        first = self.index.search({"query": "PE windows permissions", "limit": 1})
        page, hits = first, []
        while True:
            hits.extend(page["matches"])
            if page["next_offset"] is None:
                break
            page = self.index.search({"query": first["query"], "limit": 1,
                                      "offset": page["next_offset"], "index_revision": first["index_revision"]})
        self.assertEqual(len(hits), first["total"])
        self.assertEqual(len({m["citation"] for m in hits}), len(hits))
        self.assertEqual([(m["source_id"], m["start"]) for m in hits], sorted((m["source_id"], m["start"]) for m in hits))
        for match in hits:
            read = self.index.read({"source_id": match["source_id"], "revision": match["revision"],
                                    "offset": match["start"], "limit": match["end"] - match["start"]})
            self.assertEqual(read["text"], match["text"])
            self.assertEqual(read["citation"], match["citation"])

    def test_changed_index_rejects_old_page_but_preserves_source(self):
        first = self.index.search({"query": "cpp", "limit": 1})
        hit = first["matches"][0]
        (self.docs / hit["metadata"]["path"]).write_text("# Replacement cpp\nNew contents\n", encoding="utf8")
        self.index.refresh(force=True)
        with self.assertRaises(RequestError) as caught:
            self.index.search({"query": "cpp", "offset": 1, "index_revision": first["index_revision"]})
        self.assertEqual(caught.exception.status, 409)
        self.assertIn(hit["text"], self.index.read({"source_id": hit["source_id"], "revision": hit["revision"]})["text"])
        (self.docs / hit["metadata"]["path"]).unlink()
        self.index.refresh(force=True)
        self.assertFalse(self.index.search({"query": "cpp", "source_id": hit["source_id"]})["matches"])

    def test_unicode_and_oversized_lines_have_no_gaps(self):
        text = "# Heading\n" + "A\U0001f600" * (CHUNK_CHARS * 2) + "\n## End\nfinal\n"
        parts = list(chunks(text))
        self.assertEqual("".join(text[start:end] for start, end, _ in parts), text)
        self.assertTrue(all(end - start <= CHUNK_CHARS for start, end, _ in parts))
        (self.docs / "unicode.md").write_text(text, encoding="utf8")
        self.index.refresh(force=True)
        rev = self.index.db.execute("SELECT revision FROM current WHERE source_id='unicode.md'").fetchone()[0]
        offset, output = 0, ""
        while True:
            page = self.index.read({"source_id": "unicode.md", "revision": rev, "offset": offset, "limit": 17})
            output += page["text"]
            if page["next_offset"] is None:
                break
            offset = page["next_offset"]
        self.assertEqual(output, text)

    def test_bad_document_retains_index_and_reports_failure(self):
        old = self.index.revision()
        (self.docs / "invalid.md").write_bytes(b"\xff\xfe\x00")
        self.index.refresh(force=True)
        self.assertEqual(self.index.status()["status"], "stale")
        self.assertEqual(self.index.revision(), old)
        with self.assertRaises(RequestError):
            self.index.search({"query": "cpp"})
        (self.docs / "invalid.md").unlink()
        self.index.refresh(force=True)
        self.assertTrue(self.index.status()["ok"])

    def test_validation_and_no_arbitrary_path_reads(self):
        for data in ({"query": "cpp", "limit": True}, {"query": "cpp", "offset": 1}, {"query": "cpp", "limit": 21}):
            with self.assertRaises(RequestError):
                self.index.search(data)
        with self.assertRaises(RequestError):
            self.index.read({"source_id": "../../etc/passwd", "revision": "x"})
        self.assertTrue(self.index.search({"query": 'cpp " OR * NOT ) --'})["ok"])

    def test_metadata_filters_and_stable_id_after_rename(self):
        result = self.index.search({"query": "windows", "filters": {"kind": "reference", "topic": "pe", "platform": "windows", "architecture": "x64"}})
        self.assertGreater(result["total"], 0)
        self.assertTrue(all(m["metadata"]["kind"] == "reference" and "pe" in m["metadata"]["topics"] for m in result["matches"]))
        (self.docs / "references/windows/pe/pe-headers-sections.md").rename(self.docs / "renamed.md")
        self.index.refresh(force=True)
        result = self.index.search({"query": "pe", "source_id": "pe-headers-sections"})
        self.assertEqual(result["matches"][0]["metadata"]["path"], "renamed.md")
        self.assertFalse(result["matches"][0]["text"].startswith("---"))
        self.assertEqual(self.index.search({"query": "cpp", "filters": {"platform": "plan9"}})["total"], 0)

    def test_ranked_context_is_separate_from_complete_evidence(self):
        result = self.index.search({"query": "Windows VirtualProtect 0x40", "limit": 1, "context_limit": 3})
        self.assertEqual(result["returned"], 1)
        self.assertGreaterEqual(len(result["context_matches"]), 1)
        self.assertLessEqual(len(result["context_matches"]), 3)
        self.assertIn("PAGE_EXECUTE_READWRITE", "\n".join(item["text"] for item in result["context_matches"]))
        self.assertEqual(result["context_selection"]["omitted"], result["total"] - len(result["context_matches"]))
        best = min(m["score"] for m in result["context_matches"])
        self.assertTrue(all(m["rank"] <= 2 or m["score"] <= best * result["context_selection"]["relative_score_floor"] for m in result["context_matches"]))

    def test_invalid_metadata_and_duplicate_ids_fail_explicitly(self):
        for text in ("---\nkind: banana\n---\n# Bad\n", "---\ntopics: cpp\n---\n# Bad\n", "---\nid: pe-headers-sections\n---\n# Duplicate\n", "---\ntopics: &a [*a]\n---\n# Bad\n"):
            (self.docs / "bad.md").write_text(text, encoding="utf8")
            self.index.refresh(force=True)
            self.assertEqual(self.index.status()["status"], "stale")
        (self.docs / "bad.md").unlink()
        self.index.refresh(force=True)
        self.assertTrue(self.index.status()["ok"])

    def test_document_updates_are_discovered_on_requests(self):
        path = self.docs / "notes" / "external-review" / "nested" / "lesson.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nid: external-lesson\n---\n# New lesson\ningestionprobealpha\n", encoding="utf8")
        # Simulate expiry of the five-second throttle, without forcing refresh.
        self.index.last_scan = 0
        self.assertEqual(self.index.search({"query": "ingestionprobealpha"})["total"], 1)
        path.write_text("---\nid: external-lesson\n---\n# Revised lesson\ningestionprobebeta\n", encoding="utf8")
        self.index.last_scan = 0
        self.assertEqual(self.index.search({"query": "ingestionprobebeta"})["total"], 1)
        self.assertEqual(self.index.search({"query": "ingestionprobealpha"})["total"], 0)
        path.unlink()
        self.index.last_scan = 0
        self.assertEqual(self.index.search({"query": "ingestionprobebeta"})["total"], 0)

    def test_unreviewed_documents_require_external_review(self):
        path = self.docs / "draft.md"
        path.write_text("---\nid: draft-example\ntopics: [unreviewed]\n---\n# Quarantined lesson\nquarantineprobe\n", encoding="utf8")
        self.index.refresh(force=True)
        result = self.index.search({"query": "quarantineprobe", "context_limit": 8})
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["context_matches"], [])
        path.write_text(path.read_text().replace("[unreviewed]", "[reviewed]"), encoding="utf8")
        self.index.refresh(force=True)
        self.assertEqual(len(self.index.search({"query": "quarantineprobe", "context_limit": 8})["context_matches"]), 1)

    def test_http_contract(self):
        server = serve(self.index, port=0)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with urllib.request.urlopen(base + "/status") as response:
                self.assertEqual(json.load(response)["documents"], len(list(self.docs.rglob("*.md"))))
            request = urllib.request.Request(base + "/search", data=json.dumps({"query": "VirtualProtect 0x40"}).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request) as response:
                self.assertGreater(json.load(response)["total"], 0)
            before = sorted(p.relative_to(self.docs).as_posix() for p in self.docs.rglob("*.md"))
            for route in ("/notes", "/write", "/promote"):
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    urllib.request.urlopen(urllib.request.Request(base + route, data=b"{}",
                        headers={"Authorization": "Bearer obsolete-token"}))
                self.assertEqual(rejected.exception.code, 404)
            self.assertEqual(before, sorted(p.relative_to(self.docs).as_posix() for p in self.docs.rglob("*.md")))
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(urllib.request.Request(base + "/read", data=b"[]"))
            self.assertEqual(error.exception.code, 400)
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


if __name__ == "__main__":
    unittest.main()
