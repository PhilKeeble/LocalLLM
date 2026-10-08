---
id: playbook-re-parser-bounds-semantics
title: Investigate parser memory bounds, decoded meaning and consuming effects together
kind: playbook
topics: [reverse-engineering, parsers, memory-safety, logic-bugs, vulnerability-identification, malware-analysis, validation]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Investigate parser bounds and semantics together

## Start with a consumed operation, not a parser success flag

Identify the input source, reachable parser entry and first operation of interest:
allocation, copy, indexed lookup, object construction, file selection, command
dispatch or response. Record which bytes and state the actor can influence.
Follow outer framing, decoding and nested parsing until the operation's actual
operands are known. A library import or successful parse alone proves no violation.

For malware, ask which decoded configuration or command selects which effect.
Malicious behavior can use entirely valid formats and safe memory accesses.
Keep behavior recovery separate from searching for a defect in the parser, and
distinguish reachable capability from an effect observed to have executed.

## Separate the properties established by each check

Use this investigative classification, not a universal decoder API contract.

| Property | Evidence to recover | Does not establish by itself |
| --- | --- | --- |
| Readable/writable extent | Object, offset, width, initialized bytes | Correct format or permission |
| Structural acceptance | Selected grammar, lengths, tags, completion | Application-allowed values |
| Semantic acceptance | Schema, cross-field relations, accepted values | Requester's authority |
| Authorization | Subject, operation, resolved object, state | Unchanged later bytes or lifetime |
| Stable consumption | Same checked representation and live owner | Affordable processing cost |
| Resource bound | Effective bytes/work/time/retention budget | Harmless accepted behavior |

Bind each credited property to its value/object version and accepted branch.
CBOR's well-formed/valid/expected distinction is in reference-parser-cbor-types-schema;
FlatBuffers' structural-verifier scope is in reference-parser-offset-based-serialization.
Neither format's vocabulary should be silently imposed on another library.

## Preserve a representation chain through each component

Record original byte range → decoded fields → constructed object → normalized
identifier → resolved object → operation. For each boundary retain exact input,
output, size unit, schema/mode, source location and any loss or ambiguity.
A repaired representation must not be treated as the original input; unknown
bytes remain unknown. A buffer pointer and its current contents are separate
pieces of evidence.

Compare producer, validator and consumer independently: duplicate selection,
defaults, unknown fields, case/Unicode rules, escaped NULs, relative-offset bases,
trailing input and recovery can change interpretation. A validator accepting one
object is not evidence that the consumer selects that object. Use
playbook-re-parser-differentials and playbook-re-text-decoding-boundary.

## Prove complete source and destination ranges in their own units

For a byte access at offset o with width w in extent n, establish nonnegative,
representable coordinates, then o <= n and w <= n-o. Do this independently for
copy source and destination. Include actual vector width, loop iterations,
terminators, padding and any element-to-byte conversion. Do not form unchecked
offset+width and then use its wrapped result as proof of a bound.

Separate allocated capacity, live object/subobject, logical payload and initialized
range. A mapped page or allocator bucket size does not prove an access is valid
for the selected object. A legal wide lookahead needs its own readable-extent
contract; a suspicious access cannot establish its own capacity by circular reasoning.
Use reference-native-bounds-objects-terminators and
reference-native-integer-size-buffer-arithmetic for these conditions.

## Reconcile lengths, counts, tags and cross-field constraints

Recover the meaning of each count before using it: bytes, elements, key/value
pairs, samples, code units or expanded output. Follow conversions and compare the
value checked with the value allocated, iterated, copied or returned. Keep parent
and child extents, record-relative and file-relative offsets, and tag-specific
payload layouts distinct. A field fitting its integer type is not a semantic cap.

Check required combinations as relations: offset with length, count with available
elements, tag with payload arm, dimensions with row/plane stride, and declared
identity with resolved object. Individually in-range fields can describe an
inconsistent object. Use playbook-re-parser-grammar and
playbook-re-serialization-schema-boundary; unknown format variants remain explicit.

## Bind validation to the representation actually consumed

Find the precise branch accepting validation and follow the same bytes/object
to every sensitive use. Record buffer owner, aliases, copying, mutation, callbacks,
asynchronous handoff and deallocation. A copied pointer is not an immutable
snapshot; a complete byte copy does not extend the life of objects it references.

If validation is cached, recover its key and invalidation: schema, object generation,
content version, principal and operation can matter. A guard that precedes the sink
on every graph path still needs the correct accepted edge and unchanged relation.
Use reference-concurrency-mutable-validation-double-fetch and
reference-native-data-flow-alias-call-context. State unresolved calls or writes
rather than assuming they preserve validation.

## Follow partial decoding and callbacks before final acceptance

Recover whether decoding emits fields, constructs objects, invokes application
code or publishes state before its final result. Distinguish incomplete input,
valid prefix, complete item, complete container and all trailing bytes consumed.
Final failure cannot retroactively prevent an earlier file write, disclosure or
callback effect. A partial private object may instead be harmless if discarded.

Use playbook-re-incremental-parser-state for fragment/remainder ownership and
playbook-re-object-reconstruction-boundary for constructors and conversion hooks.
For errors, trace surviving state into the next message/session; for stream reset,
distinguish per-operation cleanup from connection-wide parser state.
Protocol-specific rules are in playbook-re-protocol-security-state.

## Check cost even when every access stays in bounds

Recover expanded output, retained objects, nesting, shared-graph visits, repeated
scanning, matching and concurrent work. A small compressed file or shallow syntax
does not necessarily imply cheap processing. Trace the actual limit's unit, scope,
activation and reset rather than crediting a nearby constant or function name.

Use playbook-re-decompression-boundary and playbook-re-algorithmic-resource-boundary.
If a decoding budget is exhausted, preserve the unexamined region as unknown;
do not classify it as empty, invalid under every parser, or free of malicious
content. Rejected input and inaccessible content are different evidence states.

## Trace container selection to application activation

For archives and documents, keep member name, hierarchy, selected revision,
physical range and reconstructed logical stream distinct. Follow actual extraction
or loading behavior, including alternate entries and repair paths. A successfully
enumerated outer container does not validate the inner decoder or prove activation
of embedded code/content.

Use playbook-re-archive-extraction-boundary for path/link/write effects,
playbook-re-document-content-selection for document relationships and active content,
and playbook-re-media-font-decoding for dimensions, strides and decoder output.
Report which content the target consumes, not merely which content an analyst tool
happened to display. Unsupported or encrypted members limit the conclusion.

## Constructed example of independent bounds and authorization obligations

Assume an immutable N-byte input, unsigned byte offset o and count n, an output
buffer of independently established capacity C, and a decoded destination ID d.
The checks o <= N, n <= N-o and n <= C support copying that byte range, provided
the pointers are live and the actual copy contract is satisfied. They do not
prove the copied data matches a required schema or that d names an allowed object.

Conversely, authorizing d does not make an unchecked copy safe. If a later helper
redecodes d differently or replaces n with a value from mutable storage, the prior
proofs no longer automatically apply. This is an analytical example, not a reproduced bug:
an actual finding needs the controlling input, feasible path, missing obligation
and resulting forbidden operation or behavior.

## Deliver a narrow conclusion with the missing edge identified

For a vulnerability, report the controlled field/state, checked interpretation,
consumed interpretation, violated requirement and first invalid or unauthorized
effect. Include counterevidence such as an upstream guard, rejected variant,
stable snapshot, compatible lifetime or intentionally permitted behavior.

For malware, report the selected content, decoding chain, dispatch condition,
operation, target/destination and evidence of execution versus capability. A
malformed file, powerful API or parser disagreement alone is not a malware verdict.
Keep specification rules, target-derived facts and hypotheses distinct; name any
unresolved dispatch, alias, format variant or environmental prerequisite.

## Basis and scope

Reviewed 2026-10-02. This is a combined analytical workflow, not another file-format
specification or a requirement to run samples. Arithmetic and the final example
are constructed. The linked references supply scoped API/format facts and their
primary sources. CBOR terminology was rechecked against
[RFC 8949 §1.2](https://www.rfc-editor.org/rfc/rfc8949.html#section-1.2), and verifier
scope against the [FlatBuffers C++ guide](https://flatbuffers.dev/languages/cpp/#access-of-untrusted-buffers).
Use playbook-re-sensitive-data-flow for detailed bidirectional slicing and
playbook-re-reconstruct-operation-invariants for broader logic and commit evidence.
