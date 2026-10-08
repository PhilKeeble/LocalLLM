---
id: playbook-validation-input-selection-mutation
title: Select seed inputs and boundary mutations for a reversed parser or stateful interface
kind: playbook
topics: [reverse-engineering, fuzzing, corpus, boundary-values, dictionaries, structured-mutation, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Select inputs that answer an investigation question

## Establish the entry representation and the operation of interest

Identify whether the selected boundary receives file bytes, a framed stream,
decompressed content, a decoded object or an ordered sequence. Recover its real
caller, permitted lengths, initialization and earlier validation. An input valid
at one layer may be meaningless at another.

State the question: a length conversion, nested extent, alternative dispatch,
cleanup path, identity transition or resource limit. Use recovered code and
existing artifacts to choose relevant candidates. This workflow describes input
reasoning; it does not require generating files, running a campaign or changing
the exposed toolstack. Entry contracts: playbook-validation-faithful-harness.

## Select seeds by mechanism and state diversity

Prefer examples distinguishing relevant versions, tags, optional fields, nesting,
empty/nonempty collections, encodings and operation states. Include malformed
inputs when rejection/cleanup is in scope; valid examples help establish deeper
paths. Small comprehensible examples simplify attribution, but a large/history-
dependent case may be essential to the failure mechanism.

Preserve exact original bytes, source, format assumptions and prerequisite state.
Separate captured evidence from constructed variants. File count, filename and
extension are not diversity measures. A seed failing an early gate does not
support a claim about an unreached consumer. Concepts and limits:
reference-validation-corpus-mutation-semantics.

## Derive numeric boundaries from actual widths, units and comparisons

Recover the encoded domain, decoded domain and each later conversion. Consider
zero, one, accepted endpoints and adjacent values only where representable.
For a boundary B, B-1/B/B+1 are different mathematical cases; serializing B+1 into
an already maximal fixed-width field may wrap, fail or change the encoding.
Do not silently substitute the wrapped value for the intended case.

Distinguish bytes, elements and code units. For a checked range, compare offset
with total first, then length with total-offset. For nonnegative n, s and h in an
allocation expression n*s+h evaluated in one width with maximum M, s>0 and h<=M,
the largest arithmetically representable count is floor((M-h)/s); recover actual operation widths before
using this model. Representability does not establish affordable allocation.
See reference-native-integer-size-buffer-arithmetic.

## Target structural boundaries and field relationships

These are constructed comparison dimensions, not assertions that every format
permits the inputs or that acceptance is defective.

| Boundary | Useful distinction |
| --- | --- |
| Extent | Actual bytes shorter/equal/longer than declared length |
| Count | Zero/one/many elements; count disagrees with payload extent |
| Nested record | Child ends before/at/after its allowed parent boundary |
| Terminator | Absent, first, last permitted position or embedded before suffix |
| Variant | Tag/version/presence bit agrees or conflicts with payload |
| References | Valid target, missing target, repeated reference or cycle |
| Completion | Exact end, truncation within a field, trailing complete/partial item |

Trace the changed relationship to its check and consuming operation. A single
valid start address does not establish a full access fits. Use
reference-native-bounds-objects-terminators and reference-parser-container-boundaries-integrity.

## Preserve enough structure for the chosen question, not every question

For a deep field-use hypothesis, maintain unrelated framing and prerequisites so
the relevant consumer can be reached. For validation, inconsistency or recovery
hypotheses, preserve the malformed relationship under investigation instead of
automatically repairing it. Keep both classes of candidate distinguishable.

Account for serialized lengths, offsets, checksums and cross-field constraints.
Record each repair and its exact input range. If protected input is supplied
directly to an inner parser, qualify external reachability; this is not evidence
of an authentication bypass. Do not patch the target or disable a check merely
because the conceptual workflow names a deeper boundary.

## Derive dictionaries from consumed representations

Candidate tokens can come from confirmed input comparisons, dispatch tables,
format constants, field names or recovered examples. Record their width, byte
order, encoding, case behavior and any required delimiter. Do not treat every
embedded string as accepted syntax or a command executed by the binary.

A token dictionary does not encode nesting or object relationships. For those,
use a recovered structural model and preserve unknown fields explicitly. Keep
raw-wire variants where an object decoder would normalize away the property of
interest, including duplicates and malformed encodings. Format-specific semantics
belong in the relevant parser reference, not a guessed universal serializer rule.

## Preserve sequence and environmental prerequisites

For a stateful interface, vary a message or event in the context of its prerequisite
prefix. Keep dynamic identifiers tied to their producing operation and account
for authentication, reconnect, pending work and reset scope. Mutating only isolated
final messages can miss the defect's required history.

Use playbook-validation-stateful-sequences. If a maximum-size or timeout limit
excludes the needed input/state, report that coverage gap. Do not silently raise
resource budgets or reset shared environments. Input complexity and execution
budgets are analysis conditions, not proof of the target's production limits.

## Relate retained inputs to evidence rather than only coverage

For vulnerabilities, retain the bytes/state causing the violated invariant and
the first relevant effect. Keep near-boundary counterexamples that clarify the
cause. Coverage-based corpus reduction can discard semantically distinct cases;
preserve original findings and policy-relevant examples separately.

For malware, retain the original configuration/command and its decode/dispatch
evidence. A mutated selector reaching another handler demonstrates behavior under
that constructed input, not that the original sample received or executed it.
Preserve the actual postprocessed input so another investigator does not reason
from a different representation than the binary consumed.

## Basis and limits

Reviewed 2026-10-02. Conceptual synthesis from the linked input, native arithmetic,
parser and state references. Corpus/dictionary/mutation contracts are grounded in
LLVM, AFL++ and libprotobuf-mutator documentation; wire-normalization limits use
Protocol Buffers encoding. Numeric boundary formulas are conditional mathematics,
not a claim about unknown decompiler types or an executed target.
