---
id: reference-parser-tlv-asn1-encoding
title: TLV lengths and ASN.1 BER/DER tags, nesting and scalar interpretation
kind: reference
topics: [parsers, serialization, tlv, asn1, ber, der, length-fields]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# TLV and ASN.1 encoding evidence

## TLV does not specify a universal length convention

TLV means type/tag, length and value, but the format defines their widths and
meaning. RFC 2865's base RADIUS attribute has one-byte Type and Length fields;
Length includes both fields and the value. DER Length instead counts content
bytes, excluding the tag and length encoding. [1][2]

Investigative inference: recover the next-record calculation before subtracting
a presumed header size. A custom format called TLV need not follow either rule.
Check length-field decoding, minimum record size, parent containment and zero-length
progress separately. This RADIUS example is not a specification for every later
extended attribute format.

## ASN.1 BER identifiers include class and primitive/constructed form

In BER, an identifier carries tag class, tag number and primitive/constructed
form. The low five bits hold tag numbers 0-30; value 31 introduces subsequent
base-128 tag-number octets, most-significant group first, with the high bit marking
continuation. [3]

Primitive means the content directly encodes the value; constructed content
contains component encodings. Investigative inference: do not compare only a
tag-number mask and discard class/form, or treat every tag as one byte. A high-tag
accumulator needs its own termination and integer-range checks. These BER/DER
rules do not describe every ASN.1 encoding system.

## ASN.1 definite length has short and long forms

For DER, lengths below 128 fit a single byte with its high bit clear. In long
form, the low seven bits of the first byte count the following length octets;
those octets encode the content length in big-endian order. [2]
The initial length octet FF is reserved, not a 127-octet length prefix. [3]

Constructed example: `82 01 00` encodes a 256-byte content length; object size also
includes its identifier and three length octets. First establish that all length octets exist and fit the accumulator,
then check the content against its parent. Do not add attacker-controlled length
to a pointer before proving the arithmetic and remaining range are valid.

## BER indefinite length requires constructed context and an end marker

BER permits indefinite length for constructed encodings, not primitive ones.
The length byte is 80 hexadecimal; end-of-contents is two zero octets. [3]

Investigative inference: end-of-contents is parsed at an element boundary in an
indefinite container, not found by scanning arbitrary payload bytes for `00 00`.
Recover nesting and which container an end marker closes. Input exhaustion is
not a substitute for a missing end marker. Treat indefinite length as a distinct
state, not an enormous unsigned byte count.

## Explicit and implicit ASN.1 tagging expose different nesting

Explicit tagging wraps the complete base encoding inside a constructed tagged
encoding. Implicit tagging retains the base contents and primitive/constructed
form under the replacement tag. [3]

Investigative inference: context-specific tags alone may not disclose the base
type. Recover the schema or the decoding branch before treating their contents
as another full TLV. Mistakenly stripping an implicit tag as though it were an
explicit wrapper can shift the interpretation into payload bytes.

## DER restricts BER; BER acceptance does not prove DER conformance

DER requires definite lengths using the minimum number of length octets and
prohibits constructed encodings for bit strings, octet strings and restricted
character strings. These are selected restrictions, not a complete DER validator. [3]

Investigative inference: identify the required encoding profile and the decoder's
actual enforcement. Successful decoding does not establish canonical representation,
schema constraints or trust. Preserve original bytes when a later integrity check
uses encoded data; re-encoding is a separate transformation.

## ASN.1 INTEGER sign bytes are not native padding

An untagged DER INTEGER uses universal tag 02 and signed two's-complement content.
A positive value whose first magnitude byte has its high bit set needs a leading zero content
byte to preserve its positive sign. [4]

Constructed example: positive 128 has INTEGER contents `00 80`; contents `80`
alone represent a negative value. Recover signedness and destination width before
stripping leading bytes or converting to an allocation size. A sign-preserving
content byte is not arbitrary alignment padding.

## DER BIT STRING has an unused-bit count before its data

An untagged DER BIT STRING uses universal tag 03. Its content starts with a byte
describing unused bits in the final data byte; that count byte is included in content length. [5]

Investigative inference: a BIT STRING is not simply the same span as an OCTET
STRING. Account for the count byte before passing embedded data onward. A zero
unused-bit count does not mean empty content, and syntactically decoded bit data
does not prove that an embedded key, signature or executable was validated or used.

## Primary sources and scope

Reviewed 2026-10-02. X.690 edition 02/2021, selected BER/DER clauses only;
Microsoft's DER explanations describe encoding facts, not Windows-only byte layouts.
Workflow: playbook-re-serialization-schema-boundary.

1. [RFC 2865 §5: base RADIUS attribute layout](https://www.rfc-editor.org/rfc/rfc2865.html#section-5).
2. [DER encoded length and value bytes](https://learn.microsoft.com/en-us/windows/win32/seccertenroll/about-encoded-length-and-value-bytes).
3. [ITU-T X.690 (02/2021), §§8.1.2-8.1.5, 8.14 and 10.1-10.2](https://www.itu.int/rec/T-REC-X.690-202102-I/en), printed pp. 4-6, 11-12 and 19-20.
4. [DER INTEGER encoding](https://learn.microsoft.com/en-us/windows/win32/seccertenroll/about-integer).
5. [DER BIT STRING encoding](https://learn.microsoft.com/en-us/windows/win32/seccertenroll/about-bit-string).
