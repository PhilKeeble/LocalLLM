# Knowledge library structure

All UTF-8 Markdown under knowledge/ is indexed recursively. This guide is outside
that tree so administrative instructions do not crowd out useful task evidence.

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
- references/: the WHAT. Store technical facts, encodings and domain knowledge,
  or book material grouped by title/edition. Include provenance and page/chapter
  details for books; only import content you have the right to use.

The starter library contains three Markdown documents. notes/ and references/books/
are empty placeholders, not sample content. Synthetic project and learned notes
were removed. Their historical experiment reports are outside the indexed library.

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
Search covers all folders, with optional exact category filters. Folder prefixes
are not currently search filters or automatically searchable with explicit IDs.

## External review workflow

Pi cannot write to the library through its tools or API. kb_record journals source
application in the current session only.

1. Review a Pi session externally, including raw tool output, failures and corrections.
2. Identify a reusable gap and search for existing coverage.
3. Verify claims against primary sources or reproducible checks. An external model
   can also be wrong; agreement alone is not independent verification.
4. Save a project-specific clarification under notes/<project-or-task>/, a general
   workflow under playbooks/<task-type>/, or facts under references/<domain>/.
5. Query the topic and inspect the result. Extend regression cases for important gaps.

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

From LocalLLM:
```sh
docker run --rm --entrypoint python -v "$PWD:/repo:ro" -w /repo/kb localllm-kb -B -m unittest -v test_server
docker run --rm --entrypoint python -v "$PWD:/repo:ro" -w /repo/kb localllm-kb -B retrieval_eval.py
```

The eight retrieval cases check expected sources AND evidence in a bounded
eight-passage packet, then repeat with 100 and 1000 temporary distractors.
Eight is a ceiling, not a quota: automatic context retains the best two candidates
(if available and within the requested limit), then drops further candidates below
65% of the best BM25 score magnitude. Keeping two avoids losing a supporting
passage in a two-part question; the cutoff reduces weak filler. This is a
lexical heuristic, not a confidence probability. Complete raw search remains
available through pagination; the selection reports its threshold and omissions.
Fixtures never enter the live library. This is a lexical regression baseline,
not proof of performance on real books or of correct model application.
