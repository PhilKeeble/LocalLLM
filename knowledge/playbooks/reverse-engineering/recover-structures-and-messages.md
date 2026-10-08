---
id: playbook-re-recover-structures-messages
title: Recover native structures and wire-message layouts from access evidence
kind: playbook
topics: [reverse-engineering, structures, layout, wire-format, fields, packing, evidence]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover structures and message contracts

## Start with byte accesses, not a guessed type

For each access record base-object hypothesis, offset, width, read/write,
endianness conversion, dominating condition and use. Distinguish a pointer to
an object from a pointer into its interior. Separate native in-memory layout
from the wire format; copying bytes between them does not establish identical
packing, pointer meaning or field lifetime.

Use the target ABI for alignment and call classification. Ghidra's structure
recovery examples explicitly produce partial structures reflecting observed
fields; unobserved offsets are not proof of padding. [1]

## Build and challenge a layout table

Maintain candidate fields as offset/size/meaning/evidence, leaving unknown
ranges explicit. Look across constructors, readers, writers, serializers,
destructors and array loops. Array stride constrains total layout but does not
identify every member. Overlapping accesses may reflect unions, bitfields,
vector operations or distinct lifetime phases; do not force them into separate
simultaneously live fields.

For C++ objects, account for bases, virtual dispatch and ABI-specific layout.
The Itanium C++ ABI includes size, data-size and alignment distinctions and
base-subobject layout rules; its results must not be transplanted to MSVC
objects. [2] Record packing and compiler evidence where available.

## Normalize bases and distinguish size constraints before merging layouts

Express each field observation relative to the established owner and, separately,
the actually passed interior/base-subobject pointer. Record every adjustment;
do not merge +0 fields from differently based helpers. Maintain accessed-span,
candidate object-size, array-stride and allocation-capacity constraints in
separate columns. Mark which claims assume the disputed access was valid so an
overread cannot circularly establish its own bounds.

Use `reference-native-structure-layout-access` for packing, nested members,
unions and size distinctions. Test the model against writers and other variants;
split variant/lifetime layouts when needed. A compile-time layout check is useful
only after matching architecture, compiler ABI, declaration, packing and relevant
options. A host sizeof result for an invented declaration is not target evidence.
Do not change the running target merely to make the reconstructed type fit.

## Recover wire units and discriminated variants

Locate the producer and consumer independently. For each field establish byte
order, signedness, width, unit, semantic limit and whether lengths include
header/terminator bytes. Follow tags/version fields into branch selection.
Treat an optional field as conditional only after finding the corresponding
presence condition in both framing and consumption.

Use `reference-native-binary-protocol-framing-deserialization` for framing and
`reference-native-integer-size-buffer-arithmetic` for checked ranges. A C
structure declaration reconstructed from reads does not establish a protocol
maximum or permission to construct every representable variant.

For detailed wire-grammar recovery, use `playbook-re-parser-grammar` with
`reference-parser-wire-fields-lengths-tags` and
`reference-parser-container-boundaries-integrity`. Keep this workflow's native
layout evidence separate from their encoded lengths, padding and nesting rules.

## Constructed layout example and falsification

Hypothetical observations: a decoder reads two bytes at +0, four at +4 and
copies data from +8 for the count obtained at +4. Candidate interpretations:
a 16-bit tag at +0 and a 32-bit byte count at +4; +2..+3 remain unknown.
Do not call the gap padding until producer/consumer evidence supports that.
Prove byte versus element count from the copy and all preceding conversions.

Test the hypothesis against short inputs, exact-end counts, another tag/version
and the producer's writes. A contradictory access should revise or split the
layout hypothesis, not be explained away as an impossible input without proof.

## Verify and preserve unresolved fields

When runtime inspection is permitted, use a known valid message and one
controlled field variation; inspect exact bytes and the resulting branch/use.
Preserve target build and tool configuration. Changing a field may invalidate
a checksum or earlier gate, so failure to reach consumption does not refute
the guessed meaning by itself.

Deliver layouts with offset/width/unit/condition/evidence and unresolved ranges.
Do not claim the full structure size from its highest observed access unless
allocation/stride/API evidence establishes that size. Keep native and wire
tables separate when their contracts differ.

## Connect recovered fields to security and malware questions

A plausible layout is supporting evidence, not the final finding. Follow a recovered
count to its checked allocation/copy, a selector to the chosen variant or handler,
and an identifier to the actual resolved object. A field bounded for storage can
still select an unauthorized operation. Preserve variant, object generation and
producer/consumer representation when linking those uses.

For malware configuration, distinguish decoded field names assigned by the analyst
from roles established by code: destination, interval, command, path or key material.
An embedded string is not evidence it is consumed or transmitted. Use
playbook-re-parser-bounds-semantics for combined memory/meaning/authority analysis,
and playbook-re-sensitive-data-flow to connect the field to a concrete effect.

## Sources and review

Reviewed 2026-10-02. The worked example is constructed, not a recovered specimen.

1. [Ghidra advanced analysis](https://ghidra.re/ghidra_docs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf): partial data-type recovery and applying types.
2. [Itanium C++ ABI, data layout](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#data-layout): size/alignment, bases and class layout; applies only to the corresponding ABI.
3. [Microsoft x64 layout](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions?view=msvc-170): aggregate alignment, padding and packing controls.
