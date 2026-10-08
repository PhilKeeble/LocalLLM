---
id: reference-parser-duplicate-fields-decoded-values
title: Duplicate fields, merged messages and decoded-value equality
kind: reference
topics: [parsers, parser-differentials, duplicate-fields, json, protobuf, cbor]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Duplicate fields and decoded values

## JSON duplicate object names do not have a universal winner

RFC 8259 recommends unique object names but describes differing duplicate-name
handling: retaining the last value, reporting all pairs or rejecting the object.
It does not establish a universal first-wins or last-wins rule. [1]

Investigation consequence: recover each parser's actual insertion/update behavior
and the accessor used by its caller. Constructed case: a validator reads the first
occurrence of an operation field while the executor uses the last. The candidate
weakness is their disagreement at a security decision, not duplicate syntax alone.
An already collapsed dictionary cannot reveal every original occurrence.

## JSON escape decoding changes what name equality means

JSON name/string comparison must account for escape conversion: comparing raw
escaped spellings can disagree with comparison of decoded code units. [1]

Constructed example: the JSON name spellings `"mode"` and `"\u006dode"` denote
the same decoded name. A raw-byte name filter is not equivalent to a parsed-name
lookup. This is escape equivalence, not a rule that every Unicode normalization
or case-folding operation is appropriate. Determine the downstream equality rule
before calling two spellings interchangeable.

## JSON producer output does not bound parser acceptance

RFC 8259 permits parsers to accept extensions, while generators must produce
conforming JSON grammar. [1] Investigative inference: recovering the serializer
does not establish every form accepted by the decoder. Locate actual parser
configuration and error handling before treating a producer's normal output
as a complete description of reachable input.

## Protobuf duplicate singular fields differ from repeated fields

For Protocol Buffers binary encoding, duplicate singular numeric/string fields
use the last value. Multiple occurrences of a singular embedded-message field
merge: later singular scalars replace earlier values, embedded messages merge
recursively, and repeated values concatenate. [2]

Thus a recovered field number is insufficient to select a duplicate policy;
recover its schema type and cardinality (singular or repeated). A second message occurrence need not
erase fields supplied only by the first. Investigative inference: validation of
one occurrence is not necessarily validation of the final merged object.

## Protobuf packed repeated fields may span several records

Protocol Buffers parsers accept multiple packed records for a packable repeated
field and concatenate their element sequences; each packed record must contain
whole elements. Packed and unpacked encodings of such fields must both be
accepted. Field records need not be grouped by field number. [2]

Investigative inference: a count or policy check over the first record can miss
later values. Recover whether limits apply per record or to the accumulated
logical field. Do not misclassify an allowed repeated record as malformed solely
because the producer usually emits one contiguous packed record.

## CBOR duplicate-key validity is separate from decoder output

Duplicate map keys violate CBOR map validity. Generic decoders may reject them,
expose all entries or lose entries by retaining only some occurrences; not all
CBOR decoders perform validity checking. An application cannot check original
key uniqueness after a decoder has discarded duplicates. [3]

CBOR's applicable data model defines key equality. In the generic model, integer
and floating-point keys are distinct even when numerically equal; byte strings
and text strings are also distinct. Host-language key conversion can collapse
distinctions, so application-level equality needs separate attention. [3]

Investigative inference: trace map construction and key conversion, not merely
the decoder's success return. See reference-parser-container-boundaries-integrity
for well-formed, valid and application-expected data as separate questions.

## Protobuf deterministic serialization is not canonical identity

Deterministic Protocol Buffers serialization does not promise one universal byte
representation across schemas, builds or library changes. Unknown fields make
generic canonicalization problematic: a length-delimited field might be opaque
bytes or a submessage, requiring different treatment. [4]

Investigation consequence: distinguish a hash of exact captured bytes from a
claimed identity of decoded content. Reserializing before comparison may change
the evidence. For malware configuration recovery, retain both original bytes
and the schema-dependent interpretation; byte differences alone do not prove
different commands, and matching selected fields does not prove identical behavior.

## Primary sources and scope

Reviewed 2026-10-02. These are format contracts, not claims about every custom
decoder. Protocol Buffers sources are living documentation; JSON RFC 8259 is
dated 2017 and CBOR RFC 8949 is dated 2020. Workflow:
playbook-re-parser-differentials.

1. [RFC 8259 §§4, 8.3, 9-10: JSON names, equality and parser/generator rules](https://www.rfc-editor.org/rfc/rfc8259.html).
2. [Protocol Buffers encoding: repeated elements, last-one-wins and field order](https://protobuf.dev/programming-guides/encoding/).
3. [RFC 8949 §§5.3-5.6.1: validity checking and map keys](https://www.rfc-editor.org/rfc/rfc8949.html).
4. [Protocol Buffers serialization is not canonical](https://protobuf.dev/programming-guides/serialization-not-canonical/).
