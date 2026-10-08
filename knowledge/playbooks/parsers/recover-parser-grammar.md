---
id: playbook-re-parser-grammar
title: Recover binary parser grammar from byte accesses, dispatch and consuming effects
kind: playbook
topics: [reverse-engineering, parsers, grammar-recovery, vulnerability-analysis, malware-analysis, wire-format]
platforms: [windows, linux, macos, android, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover a binary parser's grammar

## Locate the bytes actually consumed by the parser

Trace input from file, resource, network receive, IPC or an earlier decoder to
the parser entry. Record actual available byte count, buffer lifetime and any
decryption, decompression or text-to-binary transformation. Keep transport framing,
outer container, inner serialization and native object layout distinct.

For malware analysis, distinguish embedded candidate data from bytes actually
extracted and used. A file signature or protocol string is an attribution lead,
not a proven parser call. For vulnerability analysis, identify who controls each
input and any earlier bounds, integrity or authorization gate.

## Build a grammar table with evidence and uncertainty per field

Record candidate offset/base, encoded width, decoded width, byte order, unit,
presence condition, validation and use. Start with load/mask/shift/cursor evidence
rather than a guessed C struct. Locate writers or serializers independently;
an encoder's output choices do not prove the consumer rejects other forms.

Use reference-parser-wire-fields-lengths-tags. Leave unknown bytes explicit and
mark inferred versus directly observed rules. A tag that selects an operation,
a count that controls allocation and a checksum that gates dispatch should each
have their own evidence trail rather than one inferred packet name.

## Follow each length through allocation, iteration and cursor advancement

Determine whether the value counts bytes, elements, code units, padded data or
expanded output. Track sign extension, narrowing and arithmetic width at every
conversion. Compare the quantity checked with the quantity actually consumed;
include headers, trailers, terminators and alignment adjustments where applicable.

Use reference-native-integer-size-buffer-arithmetic for checked ranges. Recover
zero, exact-end and failure behavior from code. Do not treat observed allocation
capacity as the protocol's semantic maximum or use a disputed read to prove that
its containing object must be large enough.

## Reconstruct variants and nested parser state

Trace version/tag/presence fields into branch selection and every later use of
the selected object. Record parent and child bounds, termination conditions,
returned bytes consumed and the base for each relative reference. Separate input
advancement from output expansion and pointer-following traversal.

Use reference-parser-container-boundaries-integrity. Look for a child consuming
sibling bytes, inconsistent arm selection, unbounded reference traversal or
partial objects escaping error cleanup. These are hypotheses until a feasible
controlled path and violated invariant are established.

## Explain integrity gates before interpreting rejected input

Recover checksum coverage, update sequence and comparison result, and identify
whether verification occurs before or after sensitive use. Keep checksum,
authentication and application authorization as separate mechanisms.

For existing captures, a changed input rejected at an earlier integrity gate
does not disprove a field-layout hypothesis. If later controlled execution is
authorized, preserve the original bytes and record every deliberate change and
which gate accepted/rejected it. This workflow does not require executing unknown
samples merely to obtain a grammar.

## Compare recovered behavior with the claimed format and relevant variants

Keep three records distinct: the normative format, the implementation's observed
or statically established behavior, and unresolved hypotheses. Check unknown
tags, duplicate/present fields, trailing bytes, version branches and error paths
as relevant. Format acceptance is not evidence of sender trust.

For a vulnerability, report controlled field, checked interpretation, consuming
interpretation and consequence. For malware, report decoded command/configuration
fields and their reachable effects, distinguishing capability from execution.
Deliver only supported layout rules; uncertainty is preferable to an invented
schema that causes a later investigator to skip the real boundary.

## Evidence basis and related native-layout workflow

Reviewed 2026-10-02. The two parser references above cite XDR, PNG, Protocol Buffers,
CBOR and DNS contracts as scoped examples. For native structures, bases, member
offsets and object strides, use playbook-re-recover-structures-messages instead
of imposing a wire grammar on a compiler-specific object layout.
Use playbook-validation-input-selection-mutation when selecting seed, boundary
or structural variants from the recovered grammar; preserve the distinction
between modeled candidates and observed target behavior.
