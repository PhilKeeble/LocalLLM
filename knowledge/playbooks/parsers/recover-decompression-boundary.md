---
id: playbook-re-decompression-boundary
title: Recover decompression loops and payload boundaries
kind: playbook
topics: [reverse-engineering, decompression, streaming, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover a decompression boundary

## Bind the codec, wrapper and context to actual bytes

Identify the call or inlined decoding loop, input span, wrapper, initialization
flags, dictionary/history and output destination. Distinguish the compression
algorithm from its file/container wrapper. Imports, entropy and byte signatures
are leads, not proof that this path decodes the suspected payload.

Preserve compressed identity and offsets separately from decoded offsets. Record
dictionary identity and transformations needed to recover the bytes. Use
`reference-parser-compression-framing-history` for concrete wrapper and history
rules. A missing dictionary or unsupported format leaves content unexamined;
it does not justify inventing output or calling the payload benign.

## Recover each loop transition and progress measurement

Track input consumed, output produced, output capacity, status, pending internal
state and final-input indication before/after a call. Determine which branches
refill input, drain output, grow buffers, request a dictionary, reset or fail.
Use `reference-parser-decompression-stream-results` for API-specific meanings.

Examine paths where neither input nor output advances, output fills exactly,
input ends before a completion result, or another member follows completion.
Account for buffering: no output on one call does not imply no progress. A spin
or truncation claim needs the actual repeated transition, not just a loop around
a decompressor. Keep error recovery separate from ordinary buffer exhaustion.

## Trace capacity, history validity and global cost separately

Follow every count conversion into allocation, API capacity and later copy/use.
For custom decoding, inspect back-reference distance, available history, overlap
semantics, bit-reader refill and destination range. A legal overlapping match
is not itself an out-of-bounds access.

Identify independent ceilings for decoder memory, output bytes, nesting, retained
objects and work. Follow frame resets into the request-wide accounting scope.
Use `reference-parser-decompression-size-memory-limits`; do not mistake a window
limit or a small compressed input for a bounded total output. Show the reachable
policy violation and resulting effect before classifying a vulnerability.

## Follow produced bytes through integrity checks and subsequent use

Recover when partial output becomes visible and whether a later decoder error
prevents its use. Distinguish decoded prefix, complete stream, accepted checksum,
authenticated source and valid application object. Identify the actual consumer:
configuration parser, executable mapper, file writer or another decoder.

For malware analysis, report contained payload capability separately from proof
of selection, loading or observed execution. Compression also occurs in ordinary
software. Explain why the recovered content and use path support the conclusion,
and record encrypted, missing or rejected layers as evidence limits.

## Evidence and source basis

Retain call sites, widths/units, branch conditions, context/dictionary ownership,
consumed/produced coordinates, output identities and the consumer chain. Label
static inference separately from observed behavior. No sample execution is
required merely to apply these reference contracts.

Reviewed 2026-10-02. This workflow is synthesized from the primary sources linked
in `reference-parser-decompression-stream-results`,
`reference-parser-compression-framing-history` and
`reference-parser-decompression-size-memory-limits`. It does not assume one
library's defaults or return convention applies to another.
