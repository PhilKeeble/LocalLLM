---
id: reference-parser-protobuf-types-presence-evolution
title: Protocol Buffers wire types, signed values, field presence and schema evolution
kind: reference
topics: [parsers, serialization, protobuf, schema, field-presence, unknown-fields]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Protocol Buffers schema evidence

## Protocol Buffers wire types define payload mechanics, not full types

Binary record tags select these encodings. [1]

| Wire type | Payload |
| --- | --- |
| 0 | Varint: several integer types, Boolean or enum |
| 1 | Eight-byte little-endian fixed integer or double |
| 2 | Varint length followed by string, bytes, message or packed values |
| 3 / 4 | Start/end of a deprecated group |
| 5 | Four-byte little-endian fixed integer or float |

Group ending tags must match the opening field number. [1] For tag construction
and nested-message ambiguity, use reference-parser-wire-fields-lengths-tags.

## Protobuf int and sint have different negative-number encodings

Protocol Buffers int32/int64 negative values use ten-byte varints of the
sign-extended two's-complement representation. sint32/sint64 use ZigZag: signed
values 0, -1, 1, -2 map to unsigned 0, 1, 2, 3 before varint encoding. [1]

Investigative inference: the same wire type does not establish signed meaning.
Recover schema/accessor type before treating a value as a length, index or command.
Do not identify ZigZag solely from a right shift without tracing its sign handling.

## Implicit presence cannot distinguish absent from explicitly default

Under protobuf implicit presence, the API stores a value without separate set/unset
state. Default values are omitted during serialization and skipped during API
merge-from. Explicit presence also tracks whether the field is set, including
an explicitly set default. Presence discipline depends on schema/features and
field kind; it is not one universal rule for all protobuf fields. [2]

Constructed investigation: zero means revoke a grant, but an implicit-presence
patch message merges only nondefault values. Recover whether the application
uses merge semantics, a field mask or explicit replacement before concluding the
requested zero took effect. A numeric getter returning zero does not prove the
sender supplied a field.

## Protobuf oneof selection is distinct from field presence

A oneof represents alternatives, with at most one member selected in the API.
Selecting another member clears the previous selection; incoming multiple
alternatives are resolved by wire order. [3]

Investigative inference: recover the selection discriminator used at dispatch,
not just a payload accessor or one observed wire tag. An earlier validation can
become irrelevant if a later alternative replaces the selected operation.
For repeated occurrences and embedded-message merging, use
reference-parser-duplicate-fields-decoded-values rather than assuming every
duplicate replaces an entire object.

## Unknown protobuf fields can survive an intermediary

Current proto3 documentation specifies preserving unknown fields through binary
parsing and serialization. JSON conversion or copying known fields individually
can lose them. [3]

Investigative inference: an older component ignoring a field does not prove a
newer downstream consumer cannot receive it. Recover exact schema and transform
at every hop. Conversely, a dumped or reserialized message may omit original
evidence. Preserve captured bytes independently of a schema-dependent diagnostic
view; do not claim unknown data caused behavior without following its consumer.

## Primary sources and limits

Reviewed 2026-10-02 against living Protocol Buffers documentation. Wire format,
generated API representation and application policy are separate. Match deployed
schema/runtime behavior, especially custom or historical implementations.
Workflow: playbook-re-serialization-schema-boundary.

1. [Protocol Buffers encoding: wire types, signed values and groups](https://protobuf.dev/programming-guides/encoding/).
2. [Field presence: implicit/explicit and merge semantics](https://protobuf.dev/programming-guides/field_presence/).
3. [Proto3 guide: unknown fields and oneof](https://protobuf.dev/programming-guides/proto3/).
