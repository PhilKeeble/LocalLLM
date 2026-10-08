---
id: reference-validation-corpus-mutation-semantics
title: Seed corpora, token dictionaries, structured mutations and representation loss
kind: reference
topics: [fuzzing, corpus, seeds, dictionaries, structured-mutation, serialization, input-representation]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Input selection and mutation semantics

## A seed corpus is a search starting point, not a safety certificate

A corpus is a collection of candidate inputs; seeds are the initial examples used
to explore variants. Coverage-guided mutation retains inputs according to execution
feedback, not according to a proof that they are safe. LLVM's fuzzing documentation
describes varied valid and invalid seeds and retaining newly reached paths. [1]

Investigative consequence: distinguish syntactic validity, deeper handler reach,
relevant semantic variety and absence of a detected failure. Ten differently named
files rejected at the same header are not ten explored parser variants. Retain
sample origin, exact bytes, expected representation and any known prerequisites.
In malware work, a collected configuration is evidence about that sample; changing
its fields produces a constructed variant, not new observed behavior.

## A reduced corpus preserves a chosen feedback property, not every useful case

Coverage-based corpus reduction selects inputs preserving measured execution
features; AFL++ and LLVM document this criterion. [1,2] It is distinct from reducing
one failing input while preserving its failure.

For that separate objective, use reference-validation-failure-reduction-semantics
and playbook-validation-failure-minimization; coverage equivalence alone does not
establish that the original violation survives.

Investigative consequence: equal measured coverage does not imply equal principal,
object identity, decoded value, side effect or sequence state. Cases important for
policy, historical findings or format variants may deserve retention even when
redundant under that coverage metric. Preserve original evidence separately from
derived working sets. An engine's corpus membership is not a finding-confidence
score, and removing a sample is not proof its behavior is impossible.

## A mutation dictionary supplies byte tokens, not a grammar

Mutation dictionaries provide keywords or interesting byte sequences, including
multibyte magic values; LLVM documents this mechanism. [1] A useful token must
have the representation expected at the selected input boundary.

Investigative consequence: distinguish numeric field values from their byte order,
width, variable-length encoding or textual spelling. A token found in a log format
string need not be an accepted input keyword. Token insertion alone does not keep
nested lengths, checksums, object references or command ordering consistent.
Record the evidence connecting a token to a parser comparison or dispatch value.

## Structured mutation preserves a model, not all application semantics

A structure-aware mutator changes fields or syntax-tree components rather than
only arbitrary bytes. The libprotobuf-mutator implementation documents protobuf
tree/field mutation and postprocessing for cross-field consistency or checksums.
[3] Such constraints can help reach code behind early rejection gates.

Investigative consequence: separate well-formed encoding, schema consistency and
application authorization/state. Satisfying the first two does not establish the
third. Conversely, always repairing every inconsistency prevents examining some
validation and error paths. State which relationships are intentionally preserved
and which are deliberately violated; do not interpret the generated domain as all
inputs the deployed boundary can receive.

## Parsing and reserializing can erase the wire condition under investigation

Protocol Buffers accepts repeated occurrences of singular numeric/string fields
using the last value, merges embedded-message occurrences, and does not guarantee
serialized field order. [4] An API object is therefore not a lossless record of
every original field occurrence and byte arrangement.

Investigative consequence: mutations of a decoded object can miss wire-level
duplicates, malformed lengths, truncated encodings or ordering disagreements
eliminated by the decoding/serialization path. Preserve raw bytes for those
questions. Separate wire-decoder findings from findings in consumers of already
decoded objects. The same distinction applies to another format only after its
actual transformations are established, not by importing protobuf semantics.

## Repair and postprocessing are part of input identity

Postprocessing can also change user-supplied reproductions. The libprotobuf-mutator
documentation warns that its callbacks run on generated and supplied inputs, and
that unnecessary changes can stop a reproducer triggering its bug. [3]

Investigative consequence: retain original, mutated and actually consumed bytes
or objects separately, with the transformations connecting them. Recomputing an
unkeyed checksum differs from disabling verification or fabricating authenticated
input. A deep consumer failure after bypassing a gate does not prove a sender can
pass that gate. Use playbook-validation-faithful-harness for entry fidelity and
reference-parser-container-boundaries-integrity for scoped checksum facts.

## Sources and scope

Reviewed 2026-10-02. Concepts are independent of a chosen tool; named implementations
provide supporting contracts, not installation or command requirements. Workflow:
playbook-validation-input-selection-mutation. No corpus files or runnable targets
are supplied by this reference.

1. [LLVM fuzzing documentation](https://llvm.org/docs/LibFuzzer.html): Corpus, Dictionaries and corpus merge criteria.
2. [AFL++ input preparation](https://aflplus.plus/docs/fuzzing_in_depth/): collecting inputs, coverage-based corpus reduction and individual-input reduction; operational tuning advice is not adopted here.
3. [libprotobuf-mutator documentation](https://github.com/google/libprotobuf-mutator/blob/master/README.md): tree/field mutation and postprocessor constraints.
4. [Protocol Buffers encoding](https://protobuf.dev/programming-guides/encoding/): Last One Wins and Field Order.
