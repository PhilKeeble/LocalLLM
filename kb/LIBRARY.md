# Knowledge library structure

All UTF-8 Markdown under knowledge/ is indexed recursively. This guide is outside
that tree so administrative instructions do not crowd out useful task evidence.

## Purpose and required quality

The knowledge base must be a useful, accurate reference during vulnerability,
malware and reverse-engineering investigations. Agents may receive only a small
passage, not the surrounding document. Judge every addition and edit by what an
analyst could safely conclude from that passage alone.

- Provide a concrete factual answer or useful evidence workflow. Explain essential
  terms locally and connect the mechanism to the investigation question. A list
  of links, keywords or generic advice is not sufficient reference material.
- Verify technical claims against primary sources. Preserve source provenance,
  scope and uncertainty; distinguish specification requirements, recommendations,
  implementation observations and investigative inferences. Do not turn an
  unavailable source or a model's recollection into an established fact.
- Keep each section focused and concise. Place the complete rule, its conditions,
  units, applicability and important exception together. Do not rely on a prior
  scope paragraph, another retrieved chunk or an external artifact to qualify it.
- Organize around durable concepts and investigation questions. Retain named
  API/format/platform contracts where they define the claim. Source versions are
  provenance; explain actual behavior differences locally when they matter.
  Never generalize one release, configuration or private layout to every target.
- Separate capability, a violated security/software condition, malicious behavior
  and an observed effect. An API, dependency, string, crash or apparent timing
  difference alone does not establish a vulnerability or maliciousness. Keep
  alternative explanations and limits beside the evidence they qualify.
- Review the saved sections individually before accepting a change. Factual
  support, investigation usefulness and isolated-passage clarity are required;
  valid metadata, short sections or good lexical matches cannot establish them.

## Three content types

```text
knowledge/
  notes/
    <project-or-task>/
      <lesson-or-clarification>.md
  playbooks/
    cpp/
      cpp-coding-standard.md
    reverse-engineering/
      initial-static-analysis.md
  references/
    windows/
      pe/
        pe-headers-sections.md
    books/
      <book>/<edition>/<chapter>.md
```

- notes/: scoped observations, things learned, corrections and clarifications.
  Group directly by project/task, not another generic projects/ or learned/ layer.
  Include what was observed, what was checked and where the lesson does NOT apply.
- playbooks/: the HOW. Group by task type. Keep workflows, investigation order,
  evidence standards, safety checks and verification methodology compact.
  Use focused subfolders such as runtimes/, parsers/, debugging/ or malware-analysis/
  when useful; reverse-engineering/ is for shared recovery workflows, not a
  mandatory destination. Keep stable IDs when reorganizing existing documents.
- references/: the WHAT. Store technical facts, encodings and domain knowledge,
  or book material grouped by title/edition. Include provenance and page/chapter
  details for books; only import content you have the right to use.

The library covers cross-platform mechanisms as well as specific OS, runtime,
architecture and format contracts. Do not introduce a case catalogue or synthetic
project observations as learned evidence. notes/ stores only scoped reviewed
observations; references/books/ requires provenance and permission for imported
material. Keep planning, review administration and acceptance tallies outside
the indexed tree.

## Metadata and authoring

Use stable unique id, descriptive title, kind (note/playbook/reference), topics,
platforms and architectures. Categories are explicit: folders do not supply them.
Supported front matter example for a real project note:

```yaml
---
id: my-project-pe-permission-clarification
title: My project permission field clarification
kind: note
topics: [pe, permissions]
platforms: [windows]
architectures: [x64]
---
```

Keep sections self-contained with meaningful headings. Put scope, evidence,
verification and sources in the body; unsupported front-matter fields fail
validation. Prefer specific topics to tagging every document with every category.
Do not duplicate references in multiple notes; merge broadly useful corrections
into the relevant source. The original source IDs were retained during condensation.
Use references/architectures/ and references/abis/ for machine and calling
convention facts, references/formats/ for shared executable-format facts, and
platform/runtime folders for their specific contracts. Existing source paths
need not move. Cross-link stable IDs and keep shared facts in one primary home.
Record source editions/versions, inspected sections, review dates and limits in
the body, not unsupported front matter. Separate normative rules, implementation
observations and investigative inferences. A source URL alone is not an offline
answer: include the necessary factual evidence in the document.

Prioritize broadly applicable technical facts and their reverse-engineering
relevance. Retain version distinctions where behavior changes or an internal
layout is not portable, rather than organizing references around experiments.
Do not add runtime fixtures or refer consuming models to local test artifacts.
References must provide self-contained, primary-source-backed technical facts;
remove experiment-specific observations instead of treating them as contracts.
For documentation-only changes, verify primary sources, technical scope,
coverage, clarity and cross-document consistency. Do not run retrieval suites or
checkpoint tests unless the user explicitly requests them.

Write for investigators with less reverse-engineering and software-development
experience. Where relevant, connect facts to the input, control flow, authority
and observable effect needed for an investigation. Do not pad every reference
with generic workflow prose; route to focused playbooks. Keep the necessary
primary-source-backed answer available offline in the document itself.

Organize references and playbooks around concepts and investigation questions,
not tool products, command recipes or an assumed installed toolstack. The consuming
agent has its own exposed tools. Describe the evidence or capability needed and
let it map that need to those tools. Retain named API, format and OS contracts where
the name defines the technical scope; retain tool-specific details only when they
explain an implementation-specific fact or interpretation limit. Such details must
not become universal rules or prerequisites for the workflow. This applies to
earlier sections as well as new additions.

Apply this lens retrospectively as well as to new material. Review existing
documents by topic family. State the actual reviewed IDs, scope and remaining
gaps in the change/review report outside knowledge/; do not call the corpus
reviewed after sampling a few documents.
Use headings and nearby text that name the mechanism, API/field and likely
investigation question in ordinary search terms. Avoid keyword stuffing. Split
unrelated rules, numeric domains and platform contracts into separate sections;
keep the scope, units, conditions and important exception with the rule itself.
A retrieved section should be usable without a preceding paragraph or an
unavailable local artifact. Review content directly; this does not authorize
retrieval-system changes or test runs.

Keep heading-delimited evidence sections within the 1800-character passage limit,
including the heading. Split longer material at meaningful headings and retain
each resulting section's necessary scope, conditions and caveats. Remove filler
rather than cutting a qualification to meet the limit. References and links may
provide additional depth, but must not carry a qualification missing locally.
Architecture/platform tags identify applicability, not proof that every variant
of an ABI or OS has identical behavior. Label constructed explanatory examples
as hypothetical; do not present them as observed cases or benign/malicious verdicts.
Search covers all folders, with optional exact category filters. Folder prefixes
are not currently search filters or automatically searchable with explicit IDs.

## Acceptance and maintenance review

For every knowledge change, read each affected evidence section in isolation.
Check its primary support, offline answer, investigation consequence, applicable
contract, units, conditions, exception and conclusion limits. Review related
documents for contradictions, duplicated facts and broken stable-ID references.
Statically check the six metadata fields, unique IDs and section lengths. Summarize
what was reviewed and any unresolved limits in the change report.

Re-review affected documents when upstream contracts change, a new target platform
or configuration is added, primary evidence conflicts, or an investigation exposes
a missing qualification. If an agent draws an unsupported conclusion from an
isolated passage, correct that passage's factual home and review linked workflows.
Retain source editions, inspected sections, review dates and outcomes in the
affected bodies; keep broader review administration outside knowledge/.

Source verification and static review do not demonstrate live retrieval ranking,
actual passage selection or usefulness in agent investigations. Report those
limits accurately. Documentation work does not require tests, target execution,
retrieval/API calls or service operations unless the user explicitly requests them.

## External review workflow

Pi cannot write to the library through its tools or API. kb_record journals source
application in the current session only.

1. Review a Pi session externally, including raw tool output, failures and corrections.
2. Identify a reusable gap and search for existing coverage.
3. Verify claims against primary sources or reproducible checks. An external model
   can also be wrong; agreement alone is not independent verification.
4. Save a project-specific clarification under notes/<project-or-task>/, a general
   workflow under playbooks/<task-type>/, or facts under references/<domain>/.
5. Review the saved content for factual accuracy, self-contained evidence and
   consistency with related documents. Retrieval testing is a separate task and
   is not required for documentation-only changes.

Keep drafts, PDFs, templates and administration outside knowledge/. A document tagged
unreviewed is excluded from automatic context but still appears in explicit search.
Do not give Pi a writable library mount or Docker socket if the read-only boundary
must also hold outside the KB API.

## Automatic ingestion and testing

No container rebuild is needed for Markdown additions, edits, moves or deletions.
On incoming requests the server rescans at most once every five seconds and updates
its index when content changes. Invalid metadata reports an error; it is not silently
accepted. Service-code changes, unlike document changes, need a rebuild.

The KB container has no scheduled Docker health check. After startup, an idle
service does not poll or rescan documents on a timer. Search and status requests
trigger the throttled refresh; /status and /health remain available on demand.

Explicit `/search` returns the best ten matching passages by default, ranked
across the full candidate set by BM25 before pagination. An explicit limit may
request 1-20 passages. Lower scores are stronger; source ID and chunk start only
break ties. Matching more distinct words is not a separate ranking criterion.
Technical spellings are normalized on both ingestion and queries, including
P/Invoke/pinvoke, UTF-8/UTF8, C++/cxx, C# and .NET. Encoding widths and LE/BE
suffixes remain distinct. Document term frequencies are retained for BM25;
duplicate query terms do not add weight. See README.md for the response contract.
Tokenizer/index-format changes rebuild the active index and change its revision,
while preserving historical citation reads.

The former test_server.py and retrieval_eval.py scripts were removed because
their checks did not establish first-page relevance for explicit agent searches.
For retrieval-code changes, use focused checks of representative real queries,
ranking, pagination and citation reads; do not treat lexical scores as semantic
confidence or as factual verification.

Remaining optional arithmetic checks, from LocalLLM:
```sh
docker run --rm --network none --entrypoint python -v "$PWD:/repo:ro" -w /repo/kb localllm-kb -B -m unittest -v test_content_examples
```

Automatic context is separate from explicit search. Its limit is a ceiling,
not a quota: automatic context retains the best two candidates
(if available and within the requested limit), then drops further candidates below
65% of the best BM25 score magnitude. Keeping two avoids losing a supporting
passage in a two-part question; the cutoff reduces weak filler. This is a
lexical heuristic, not a confidence probability. Complete ranked search remains
available through pagination; the selection reports its threshold and omissions.

Primary-source provenance and technical scope belong in the document bodies.
Report investigation sufficiency and the actual review coverage separately from
retrieval effectiveness, following the acceptance requirements above.
test_content_examples checks constructed numeric examples (endian conversion,
integer wrap, checked ranges, ELF/Mach-O coordinates, binary32 rounding and quota
reservation arithmetic).
These are arithmetic checks, not executions of target ABI/compiler behavior.
