# Offline Markdown knowledge service

This first implementation runs SQLite FTS5/BM25 retrieval on CPU. It has no
embedding model, neural reranker, outbound runtime requests, or dependency on the
generation model. PyYAML is installed at image build time for safe front matter.
The Pi extension controls automatic consultation and records how sources are
applied; this service supplies versioned reference evidence.

## Run and update

From LocalLLM:

```sh
docker compose build kb
docker compose up -d --no-deps kb
curl http://localhost:8080/kb/status
```

Start Caddy through the usual Compose workflow if it is not already running.
Only Caddy publishes a port. KB joins `llm_internal`, mounts `knowledge/`
read-only, and writes its SQLite index to the persistent `kb_index` volume.
Editing Markdown needs no rebuild: requests rescan at most once every five
seconds. Source-code/dependency changes require rebuilding/recreating `kb`.
The `kb` refresh does not require restarting the model service.

## Documents and front matter

See [library organisation and quality checks](LIBRARY.md) for the PE/C++ folder
layout, authoring rules, review flow, and repeatable growth regression suite.

All UTF-8 `*.md` files beneath `knowledge/` are indexed. Front matter is optional:

```yaml
---
id: cpp-coding-standard
kind: playbook
topics: [cpp, coding, raii, exceptions, memory-safety]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
```

Supported fields are `id`, `title`, `kind`, `topics`, `platforms`, `architectures`.
`kind` is `playbook`, `reference`, or `note`; lists contain short strings.
Without front matter, the ID is the relative path, kind is reference, and lists
are empty. An explicit ID stays stable after a rename. IDs must be unique.
Title defaults to the first top-level heading, then the relative filename.
Category lists are lowercased. Malformed YAML, unsupported fields, duplicate IDs,
or invalid types fail the refresh explicitly. YAML anchors/aliases are rejected.
Classification does not make document instructions authoritative.

Headings delimit passages; long passages are split into contiguous pieces of at
most 1800 Unicode code points. Source offsets include front matter even though
the header is excluded from body chunks. The revision hashes the complete text
after BOM removal and CRLF-to-LF normalization. `read` returns this exact text.
The response includes source ID, metadata/path, revision, line ranges, offsets,
and a stable citation. Historical document text remains available in the index;
deleting a source removes it from current search but not old citations. Index
storage therefore grows with revisions. Removing the index volume loses that
history; the current Markdown can still rebuild the active index.

## Retrieval and API v1

- `GET /status` or `/health`: backend, generation, counts, and refresh errors.
- `POST /search`: `query`, optional `source_id`, `filters`, `offset`, `limit`,
  `index_revision`, and `context_limit` (used by automatic Pi retrieval).
- `POST /read`: exact `source_id`, `revision`, optional character `offset` and
  `limit`. No arbitrary filesystem reads or execution.

Caddy strips `/kb` before forwarding. Example:

```sh
curl http://localhost:8080/kb/search -H 'Content-Type: application/json' \
  -d '{"query":"VirtualProtect 0x40","filters":{"kind":"reference","topic":"pe"},"limit":8}'
```

Filters are exact `kind`, `topic`, `platform`, `architecture` matches and combine
with AND. Search normalizes C++/cxx to cpp, drops common query stopwords, and ORs
the remaining terms using quoted FTS literals. Titles and metadata are indexed
with every chunk. It computes BM25 scores; lower is stronger. This is lexical
matching, not semantic understanding. The default query is not automatically
restricted by inferred topic, architecture, or OS.

`matches` exposes **all collected lexical matches** through deterministic
source/offset pagination (`total`, `offset`, `returned`, `truncated`,
`next_offset`). Nonzero offsets require the original `index_revision`; a changed
generation returns 409 and instructs a fresh search. There is no hidden hit cap.
The optional `context_matches` is explicitly a separate top-BM25 selection,
presented in source order with ranks. `context_selection` states its budget,
omitted count, and how to retrieve the complete evidence. Pi injects this bounded
selection rather than arbitrary early source pages.

Automatic context excludes documents tagged `unreviewed`; complete raw search
still exposes them for explicit review. The exclusion and omitted count are
returned in context_selection. No automatic document-type priority is implied.

## Externally reviewed updates only

The entire knowledge/ tree is mounted read-only. There is no library write
endpoint or credential. Only the SQLite index is writable. Pi's kb_record
journals source application in the session, not the library.

Review Pi sessions externally, independently verify claims and reproductions,
then edit Markdown on the host. See [the review workflow](LIBRARY.md).
Subfolders, additions, edits and removals are picked up on requests, at most once
every five seconds. Document changes need no rebuild; service code changes do.
Do not grant Pi writable library mounts or Docker control.

Read/search endpoints remain unauthenticated on the LAN HTTP route. Keep the
pilot on a trusted network; add authentication/encryption before expanding access.

A failed refresh leaves the previous complete index on disk, reports stale
status, and returns 503 for current search until corrected. Exact historical
reads still work. Empty libraries/no hits are explicit. Files over 32 MiB must
be split into chapters. The first version rescans file contents and is intended
for a small pilot; benchmark before importing a large library.

## Validation

```sh
docker run --rm --entrypoint python -v "$PWD:/repo:ro" -w /repo/kb \
  localllm-kb -B -m unittest -v test_server
```

Tests cover both initial documents, ranked-context relevance, complete pages,
source coordinates, revision retention, deletion, changed-index recovery,
Unicode/oversized lines, metadata filters/renames, malformed metadata, and HTTP
validation. Pi loader/focus/model exercises live in the sibling `pi` repository
under `tests/knowledge`. No model call is needed for these server tests.
