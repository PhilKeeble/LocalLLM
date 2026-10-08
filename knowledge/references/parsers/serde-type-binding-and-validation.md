---
id: reference-parser-serde-type-binding-validation
title: Rust Serde field binding, enum selection and validation conversions
kind: reference
topics: [parsers, deserialization, rust, serde, enums, field-binding, validation]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Serde type selection and reconstructed invariants

## Serde Deserialize implementation, not a type name, determines construction

Serde supports field-level deserialize_with and with functions that replace
ordinary field deserialization. Container from and try_from attributes deserialize
an intermediate type and convert through From or fallible TryFrom respectively.
[1][2]

Investigative inference: locate the selected Deserialize implementation and any
custom field functions or conversion. A public new/try_new method elsewhere in
the binary is not evidence that reconstruction invokes it. For an intended
nonempty, bounded or authority-carrying type, find the actual rejecting branch
before the sensitive operation. Rust memory safety does not establish the
application's value or authorization invariant.

## Serde missing fields, defaults and skipped directions are distinct

Serde field default supplies Default::default or a configured function when a
field is absent. skip_serializing does not prevent deserialization of that field;
skip_deserializing skips input binding and supplies a default instead. [1]

Investigative inference: an output document omitting a sensitive field does not
prove that input cannot set it. Trace serialization and deserialization contracts
separately, including omitted, explicit null and explicit default values. A
default-generating function is executable application code, not necessarily a
zero fill. Establish which defaults actually survive later validation and use.

## Serde aliases and flattened maps expand the accepted field surface

Serde alias adds accepted input names for a field. flatten can place nested
fields at the enclosing level or collect remaining entries into a map.
deny_unknown_fields rejects unknown fields but is not supported together with
flatten; without it, self-describing formats such as JSON normally ignore unknown
fields in derived struct binding. [1][2]

Investigative inference: compare actual input names at validator and consumer.
A field ignored by one type can acquire meaning after forwarding or rebinding.
Do not equate unknown-field rejection with required-field presence. Trace custom
Deserialize implementations separately; derive attributes are not evidence of
the contract of unrelated handwritten code or every binary-format adapter.

## Serde tagged enum representations select declared variants

Serde's default enum representation is externally tagged. Internally tagged
enums put a tag alongside the variant fields; adjacently tagged enums separate
tag and content fields. Untagged enums omit an explicit discriminator. [3]

Investigative inference: recover the representation and compiled variant mapping
before interpreting a wire type field. An ordinary derived enum tag selects
among that enum's variants; it is not automatically a request to import a class
or load a library. Each accepted variant still needs operation-specific value
and authority checks. Custom factories or trait-object registries require their
own evidence beyond these enum contracts.

## Serde untagged enums choose the first successful variant

Serde tries untagged variants in declaration order and returns the first that
deserializes successfully. [3]

Constructed scenario: an early variant accepts field id and ignores other JSON
fields; a later variant additionally understands operation. Input containing both
can match the early variant before the later interpretation is attempted.
Whether that is a flaw depends on the intended operation and downstream use.
Compare variant order, unknown-field handling and custom validation rather than
assuming the most specific shape wins. Repeated attempted conversions can also
add work; a final error is not proof that earlier custom code had no effects.

## Sources and scope

Reviewed 2026-10-02 against Serde's current attribute/representation documentation.
These are Serde derive and conversion contracts, not a universal serialized byte
layout or a claim about every crate implementing Deserialize. Binary investigation
must recover actual monomorphized code, input format and adapter configuration.
Workflow: `playbook-re-object-reconstruction-boundary`.

1. [Serde field attributes](https://serde.rs/field-attrs.html): defaults, skipped directions, aliases, flatten and custom conversion.
2. [Serde container attributes](https://serde.rs/container-attrs.html): unknown fields, from and try_from.
3. [Serde enum representations](https://serde.rs/enum-representations.html): tag placement and untagged first-success selection.
