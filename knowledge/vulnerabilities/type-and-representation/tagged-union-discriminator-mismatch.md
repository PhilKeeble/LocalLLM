---
id: vulnerability-type-tagged-union-discriminator-mismatch
title: Tagged-union or variant discriminator and payload mismatch
kind: vulnerability
topics: [type-confusion, tagged-union, variants, discriminators, parsers]
platforms: [cross-platform]
architectures: [any]
---

# Tagged-union or variant discriminator and payload mismatch

## Definition and violated invariant

A discriminator mismatch occurs when a tag, enum, version, length, or state selects one payload layout while the stored or serialized payload was created for another. The discriminator and payload must be validated and consumed as one coherent snapshot under the selected schema and object lifetime.

Unknown tags, default branches, optional states, and niche encodings are runtime- or format-specific. A familiar integer tag is not proof of a C union or a separate in-memory discriminant.

## Conditions that establish the issue

Recover every writer and reader of the discriminator and payload, accepted tag set, selected layout, initialization path, mutation synchronization, and final access. Prove a feasible tag/payload combination passes dispatch and makes a field, length, pointer, destructor, or method be interpreted under the wrong variant.

For mutable shared state, establish whether validation and use can observe different tag or payload generations. For serialized data, validate nested payload bounds after selecting the arm.

## Evidence that is not sufficient

Overlapping fields, a switch, enum load, union-like decompiler output, or unknown tag is not sufficient. Byte operations, reused storage, compiler niche encoding, or a rejecting default can be valid.

Matching sizes do not prove matching meanings, while differing sizes do not prove a defect if the selected arm is independently bounded.

## Investigation sequence

Create a variant table containing tag values, payload layout, initialization, ownership, and destructor or consumer. Trace tag and payload together from production to access. Inspect default and error states and whether a callback can reenter while an update is incomplete.

In assembly, correlate compare/switch targets with layout-specific offsets and access widths. Confirm the branch uses the same discriminator snapshot associated with the payload.

## Constructed source example

```c
enum kind { inline_text = 1, external_text = 2 };
struct value {
    enum kind kind;
    union {
        char inline_bytes[8];
        struct { const char *pointer; size_t length; } external;
    } payload;
};

size_t length_of(struct value *value)
{
    return value->kind == external_text ? value->payload.external.length : 8;
}
```

If an inline payload is published with tag `external_text`, the consumer interprets inline bytes as pointer/length fields. The vulnerability requires that inconsistent state to be constructible or race-observable; a constructor that atomically enforces the pair refutes it.

## Primitive and impact limits

The direct result can be type confusion, invalid pointer access, incorrect destruction, out-of-bounds range, or wrong dispatch. Severity depends on controlled payload bytes and the selected consumer.

## Related knowledge and primary sources

`reference-native-type-confusion-object-validity` covers discriminators and object representations, while serialization references cover schema variants. This profile repeats coherent tag/payload binding locally.

Reviewed 2026-10-09 against C++ [unions](https://eel.is/c++draft/class.union), Rust [enumerations](https://doc.rust-lang.org/reference/items/enumerations.html), and [MITRE CWE-843](https://cwe.mitre.org/data/definitions/843.html). The C example is constructed.
