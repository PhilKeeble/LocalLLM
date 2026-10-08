---
id: reference-parser-wire-fields-lengths-tags
title: Wire fields, length units, tags and alignment in binary grammar recovery
kind: reference
topics: [parsers, wire-format, grammar-recovery, length-fields, tags, alignment, serialization]
platforms: [windows, linux, macos, android, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Wire-field interpretation for parser investigations

## Fixed-width integers and variable-length integers need different decoders

XDR encodes its ordinary signed integer as a 32-bit two's-complement value with
the most significant byte first. Protocol Buffers uses base-128 varints for
many integer fields, with seven payload bits per encoded byte and a continuation
bit; lower-significance groups come first. [1,3] Neither is the target machine's
C structure layout.

Recover byte loads, shifts, masks, sign extension and cursor advancement together.
A four-byte native load can read part of a variable encoding or combine multiple
fields. A familiar decoded number is insufficient to establish width or byte
order. Keep the on-wire encoding separate from the width used for allocation,
comparison and pointer arithmetic after decoding.

## Payload length excludes overhead only when the format says so

PNG's chunk length counts data bytes, excluding its length field, four-byte type
and four-byte CRC. It is unsigned, limited to 2^31-1 bytes, and may be zero. [2]

For an unknown format, determine whether a candidate length includes header,
payload, terminator, padding or trailer by following the next-field cursor.
Constructed example: with a four-byte length field, four-byte tag and four-byte
trailer, payload length L implies 12+L encoded bytes only if that interpretation
and arithmetic range are established. A representable length is not evidence
that the captured input contains those bytes or that the application permits it.

## An element count cannot be used as a byte count without a size model

XDR variable-length arrays encode an element count followed by individually
encoded elements. Equal element types need not have equal encoded sizes. [1]

If elements have verified fixed encoded width S, the payload span is count*S
only after checking multiplication range and available bytes. If elements are
variable-length, recover each element boundary; native sizeof(T) is not an
encoded stride. Compare allocation count, decoded element count and consumed
byte extent independently when looking for under-allocation or overread.

## Wire padding belongs to an encoding, not automatically to the CPU ABI

XDR variable-length opaque data is a four-byte byte-count followed by that many
bytes and zero to three zero padding bytes so the data-plus-padding length is a
multiple of four. The count excludes padding. [1] PNG chunks, by contrast, do not
guarantee alignment beyond individual bytes. [2]

Constructed XDR example: five data bytes consume 4+5+3=12 encoded bytes. For an
unknown parser, identify the alignment origin and whether it rounds an offset,
payload length or absolute address. Rounding arithmetic and the padded span
both need bounds checks. Unread gaps are not proven padding without writer or
format evidence, and alignment alone does not establish initialized contents.

## A discriminant selects a variant; it does not prove that variant is permitted

An XDR discriminated union encodes a discriminant followed by the selected arm.
Without a default arm, unspecified discriminant values are not valid encodings. [1]
A discriminant is a field that selects which payload interpretation applies.

In recovered code, follow the tag/version through dispatch, field presence and
all later consumers. A switch accepting a tag does not establish that a caller
is authorized to request that operation. Check the selected arm's required size
and state independently; a union reconstructed from overlapping native accesses
does not establish which wire tags can select those accesses.

## A Protocol Buffers wire type is not a complete application schema

A Protocol Buffers tag combines field number and wire type as
(field_number << 3) | wire_type. Length-delimited records prefix payload bytes
with a varint length; strings, bytes, submessages and packed repeated scalar
fields can all use this wire type. [3]

For unknown data, a length-delimited region that happens to decode as another
message is only a nesting hypothesis. Corroborate with descriptors, generated
accessors or the target's consumer. A wire-type match establishes neither field
meaning nor an application's range, cardinality or authority rule.
Use reference-parser-protobuf-types-presence-evolution for scalar encoding,
field-presence and unknown-field rules; use reference-parser-tlv-asn1-encoding
for a different TLV family whose tag/length conventions must not be conflated.

## Primary sources and scope

Reviewed 2026-10-02. These named formats provide verified contrasts, not a claim
that all custom protocols use their rules. Grammar-recovery workflow:
playbook-re-parser-grammar. Arithmetic: reference-native-integer-size-buffer-arithmetic.

1. [RFC 4506 XDR](https://www.rfc-editor.org/rfc/rfc4506.html), sections 4.1-4.2, 4.10, 4.12-4.15: integers, opaque padding, counts and union arms.
2. [PNG third edition](https://www.w3.org/TR/2025/REC-png-3-20250624/), section 5.3: chunk lengths and byte alignment.
3. [Protocol Buffers encoding](https://protobuf.dev/programming-guides/encoding/): varints, tags, length-delimited fields and packed repetition; living documentation.
