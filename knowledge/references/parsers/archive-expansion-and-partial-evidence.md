---
id: reference-parser-archive-expansion-partial-evidence
title: Archive expansion budgets, sparse files and incomplete extraction evidence
kind: reference
topics: [parsers, archives, decompression, resource-exhaustion, sparse-files, evidence]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Archive expansion and incomplete evidence

## Compressed size does not bound extraction cost

CWE-409 describes mishandled highly compressed input whose expanded output
consumes excessive resources. [1] Python tarfile warns that its data extraction
filter does not prevent denial of service. [2] Path filtering and resource
accounting therefore answer different questions.

Investigative model: follow compressed input bytes, produced bytes, cumulative
outputs, member count, nesting depth, CPU work and simultaneously retained
state as distinct quantities. A declared size is input to validate, not evidence
of an enforced limit. Find checks during production, not merely before it.
An expansion ratio can supplement but cannot replace an absolute budget: many
ordinary-ratio members can still exhaust storage or memory.

## Nested archives and repeated members need an aggregate accounting scope

Constructed model: each nested extraction starts a fresh per-archive budget,
while the parent retains every output. Each local check can pass although total
retained data exceeds the intended task budget. Repeated member names can also
consume work even when only the last output remains on disk.

Recover the budget owner, unit, checked arithmetic, recursion policy, concurrent
jobs, cancellation and charge/release points. Decide whether the promised limit
is per member, archive, request, principal or service. See
`reference-logic-configuration-quotas-fallbacks` for reservation arithmetic and
identity. A large legitimate archive is not by itself evidence of a vulnerability
or deliberate denial of service; establish reachable influence and policy failure.

## Sparse-file logical extent differs from allocated storage

libarchive ARCHIVE_EXTRACT_SPARSE can represent zero-filled blocks as filesystem
holes, independently of whether the archive format itself uses sparse storage.
[3] A hole represents a logical range without corresponding allocated data blocks.

Investigative inference: keep archive bytes, logical output extent and allocated
disk storage separate. A small allocated size does not justify reading the whole
logical file into memory. Inspect seek offsets, resulting file length, quota
units and later copying/scanning behavior. A sparse representation is a normal
storage mechanism, not alone evidence of an archive bomb.

## Skipped, encrypted or rejected members remain unexamined evidence

Investigation rule: record each original member identity, attempted transformation,
result, output hash when available and reason for missing output. Distinguish
unsupported compression, unavailable decryption, policy rejection, damaged input
and resource exhaustion. Do not silently replace any of these with “empty” or
“benign.” Preserve the original container so another supported analysis path can
later examine it without inventing the missing bytes.

An incomplete extraction can support findings about recovered members, but not
an exhaustive claim that the package lacks another payload. For malware triage,
separate extracted capability from proof that the original application selected,
loaded or executed it. Use `playbook-re-archive-extraction-boundary` for the chain.

## Sources and scope

Reviewed 2026-10-02. Budget models are constructed analytical guidance, not
implementation defaults or target measurements. Decompressor-specific streaming
contracts require separate review from these archive-level accounting rules.
See `reference-parser-decompression-stream-results` for completion and
`reference-parser-decompression-size-memory-limits` for decoder/output budgets.

1. [CWE-409](https://cwe.mitre.org/data/definitions/409.html): data amplification and resource exhaustion.
2. [Python tarfile](https://docs.python.org/3/library/tarfile.html): extraction-filter limitations, Python 3.14.8 documentation.
3. [libarchive archive_write_disk manual](https://raw.githubusercontent.com/libarchive/libarchive/master/libarchive/archive_write_disk.3): ARCHIVE_EXTRACT_SPARSE, source inspected 2026-10-02.
