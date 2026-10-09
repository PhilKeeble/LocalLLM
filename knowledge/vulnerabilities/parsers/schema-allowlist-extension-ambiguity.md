---
id: vulnerability-parser-schema-allowlist-extension-ambiguity
title: Schema allowlist, extension-data, or unknown-field ambiguity
kind: vulnerability
topics: [parsers, schemas, allowlists, unknown-fields, extensions, serialization]
platforms: [cross-platform]
architectures: [any]
---

# Schema allowlist, extension-data, or unknown-field ambiguity

## Definition and violated invariant

A schema-boundary vulnerability occurs when decoded types, variants, fields or extensions exceed the intended closed contract, or when different stages reject, ignore, preserve, merge or reinterpret unknown data differently. Validation must cover the final logical object and every field or type that can acquire meaning before the security-relevant consumer.

Unknown-field tolerance can be deliberate forward compatibility. It becomes unsafe when ignored data is later forwarded, rebound or interpreted under a broader schema without equivalent validation.

## Conditions that establish the issue

Recover the exact schema/profile at each stage, required and optional fields, type and variant allowlists, aliases, defaults, duplicate handling, unknown-field behavior, extension maps, merge rules, nested objects, reserialization and final consumer. Prove attacker-controlled data escapes the validating schema and later changes an operation, object, authority decision or bound.

Bind allowlist checks to exact loaded type or variant identities. Name-only, base-interface or assignability checks can admit implementations with different authority, but only actual resolver and consumer behavior establishes the issue.

## Evidence that is not sufficient

Unknown fields, extension storage, optional values, defaults, schema evolution, polymorphism or an allowlist is not sufficient. The data may remain inert, be discarded before use, or be validated by the later component that understands it.

Unknown-field rejection does not prove required-field presence or value validity, and successful generic decoding does not prove the application schema was enforced.

## Investigation sequence

Build a stage table showing raw fields, decoded names/types, duplicates, defaults, preserved unknown data, selected variant and reserialized output. Follow every extension container and flatten/merge operation into later binding. Compare validators with the final consumer's exact schema and configuration.

For versioned protocols, determine whether old components sign, cache or authorize representations that newer components interpret more broadly.

## Constructed forwarding example

```json
{"user":"alice","extension":{"operation":"delete"}}
```

Assume a gateway schema validates only `user` and preserves `extension` for forward compatibility, then a backend flattens extension fields and treats `operation` as a command. The gateway's successful validation did not authorize that later meaning. The finding requires the actual preservation, flattening and backend operation path; the presence of an unknown object alone is not enough.

## Primitive and impact limits

The direct primitive is unvalidated data gaining meaning under a later schema or implementation. Consequences can include unauthorized operation selection, type confusion, signature/canonicalization mismatch, hidden policy fields or bounds bypass.

## Related knowledge and primary sources

`reference-parser-serde-type-binding-validation`, `reference-parser-protobuf-types-presence-evolution`, `reference-parser-cbor-types-schema`, and duplicate-field references define concrete schema behavior. This profile repeats stage-by-stage field meaning locally.

Reviewed 2026-10-09 against Serde [field attributes](https://serde.rs/field-attrs.html) and [container attributes](https://serde.rs/container-attrs.html), Protocol Buffers [field presence](https://protobuf.dev/programming-guides/field_presence/), CBOR [acceptance levels](https://www.rfc-editor.org/rfc/rfc8949.html), and CDDL [occurrence rules](https://www.rfc-editor.org/rfc/rfc8610.html). The JSON scenario is constructed.
