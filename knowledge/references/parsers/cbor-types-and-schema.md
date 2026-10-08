---
id: reference-parser-cbor-types-schema
title: CBOR major types, argument units, semantic tags and CDDL schema
kind: reference
topics: [parsers, serialization, cbor, cddl, schema, tags]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# CBOR type and schema evidence

## CBOR well-formed, valid and expected are different acceptance levels

RFC 8949 distinguishes syntactically well-formed encoding, CBOR-valid meaning and
additional application expectations. For example, a correctly framed text string
with invalid UTF-8 is well-formed but invalid; a valid item can still have the wrong
type or value for the receiving application. [1]

Investigative inference: establish which level a decoder or verifier actually
checks and which result the caller uses. Structural success is not proof of required
field presence, permitted value range or operation authorization. Conversely, an
application rejecting a valid CBOR integer where it expects a map need not indicate
a parser defect. Bind the chosen schema/profile to the consumed value rather than
treating every function named validate as interchangeable.

## CBOR initial-byte dispatch and argument width

CBOR's first byte contains a high three-bit major type and low five-bit additional-information
value. For major types 0-6, values below 24 directly encode the argument; 24-27
select 1/2/4/8 following big-endian bytes. Values 28-30 are reserved. Value 31
means indefinite length only for types 2-5; it is invalid for 0, 1 and 6. [1]

## CBOR argument meaning depends on major type

For definite-length items, argument N has these meanings. [1]

| Major type | Meaning |
| --- | --- |
| 0 | Unsigned integer N |
| 1 | Negative integer -1-N |
| 2 | Byte string of N bytes |
| 3 | UTF-8 text of N bytes, not N characters |
| 4 | Array of N items |
| 5 | Map of N key/value pairs |
| 6 | Tag number N followed by one enclosed item |
| 7 | Separate simple-value/floating-point rules; FF is a break marker |

## CBOR recovered type controls the subsequent size calculation

Investigative inference: a map count is not a byte span, and a negative-integer
argument is not a native signed integer bit pattern. Follow the decoded type into
allocation, iteration and conversion. A tag adds semantic interpretation; it does
not itself establish authorization or that the application recognized the tag.

For indefinite strings/break context use reference-parser-container-boundaries-integrity;
for duplicate-key equality use reference-parser-duplicate-fields-decoded-values.
Those are separate from the header's width and units.

## CDDL occurrence constraints are not CBOR encoding lengths

CDDL is a description language for structured data. RFC 8610 occurrence indicators
include `?` for optional, `*` for zero or more, `+` for one or more and `n*m` for
a bounded count; without an indicator, an entry occurs once. They do not by
themselves require definite or indefinite CBOR encoding. Repetition notation also
does not make duplicate CBOR map keys valid. [2]

Investigative inference: recover application expectations independently from the
generic CBOR decoder. A decoder recognizing an integer or map does not prove a
required field, allowed range or permitted operation was checked. A schema found
in a binary is useful evidence only after binding it to the actual decode/use path.

## Primary sources and limits

Reviewed 2026-10-02. These are encoding/schema anchors, not a complete CBOR or
CDDL implementation guide. Check the application's selected profile separately.
Workflow: playbook-re-serialization-schema-boundary.

1. [RFC 8949 (2020) §§1.2 and 3-3.1: acceptance terminology, headers and major types](https://www.rfc-editor.org/rfc/rfc8949.html).
2. [RFC 8610 (2019) §3.2: CDDL occurrence constraints](https://www.rfc-editor.org/rfc/rfc8610.html#section-3.2).
