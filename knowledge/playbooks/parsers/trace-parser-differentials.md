---
id: playbook-re-parser-differentials
title: Trace producer, validator and consumer parser disagreements
kind: playbook
topics: [reverse-engineering, parsers, parser-differentials, vulnerability-analysis, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Trace parser disagreements

## Identify every interpretation boundary, not just the first decoder

Map producer, transport/framing layer, validator, translator, serializer and
final consumer. One executable can contain several parsers. Record actual input
bytes/length and output representation at each boundary, including transforms
such as decompression or escape decoding. Preserve original evidence separately
from formatted or reconstructed output.

A producer emitting one representation does not prove its consumer accepts only
that representation. For malware work, include the analyst's extraction script
as a separate interpreter; do not silently substitute its rules for the target's.
Use playbook-re-parser-grammar when field layout itself remains uncertain.

## Compare consumed extent and residual bytes

For each parser, recover start, available length, returned bytes consumed,
termination condition and treatment of residual input. Separate byte counts from
element counts, encoded lengths and expanded lengths. Follow numeric conversion
and overflow behavior into the actual comparison and memory operation.

Ask what receives the remainder: another field, another message, a new parser or
discard logic. Constructed case: validator checks one complete object but executor
continues with a second object in the same buffer. Establish that the second
interpretation reaches an operation outside the validated scope; extra bytes
alone do not prove bypass. Route HTTP-specific rules to
reference-parser-framing-normalization-differences.

## Recover duplicate handling and final values after conversion

Record field identity, schema type, repetition rules, insertion behavior, merge
behavior and lookup API. Compare both pre-conversion and final values used by
security checks and dispatch. Include default substitution, unknown-field handling
and numeric/key conversion when present; do not assume absence equals zero.

Use reference-parser-duplicate-fields-decoded-values. A schema-aware decoder's
merged result can differ from a handwritten scanner's first match. Record exactly
which difference matters rather than declaring one library universally correct.

## Follow malformed-input exits into the caller

Distinguish rejection, partial result, replacement, ignored field and retained old
state. Trace the returned status and output object together: the caller might
ignore failure or keep a previously populated value. Determine whether error
cleanup stops downstream processing and whether a subsequent message inherits
buffered bytes or state.

An import or documented strict mode does not prove that mode is enabled. An error
message does not prove that no effect occurred before it. Preserve uncertainty
where control flow or target configuration is not established.

## Compare normalized identity with authorized and executed identity

Trace raw spelling through decoding, case conversion, normalization and final
object resolution. Record the exact equality rule and namespace at each use.
Do not infer that all normalizations commute, or that a canonical spelling freezes
a mutable resolved object. Use reference-logic-authorization-object-binding for
subject, operation and object binding.

Constructed malware-analysis case: an extracted configuration has two candidate
destinations. Report the one selected by the target's proven rule, or retain both
as unresolved; a convenient dictionary conversion is not behavioral evidence.

## State the invariant and the supported conclusion

For a vulnerability candidate, record input control, divergent interpretations,
feasible path, missing/ineffective check and forbidden consequence. Distinguish
static evidence from observed execution. For malware analysis, report decoded
meaning and reachable effects separately from intent, attribution and execution.

For comparison-oracle and normalization limits, use
playbook-validation-differential-metamorphic-analysis. A reference decoder is not
automatically correct for every target mode. If both local parser choices are
permitted, their composition can still be unsafe when validation and execution
bind different values; establish that boundary rather than requiring one parser
to violate its own format contract.

Reviewed 2026-10-02. This is an analytical workflow grounded in the two parser
references above and their cited RFC/Protocol Buffers contracts. It does not
require sample execution. Any later dynamic investigation needs its own authorized
scope and isolation; this document is not evidence that a target was tested.
