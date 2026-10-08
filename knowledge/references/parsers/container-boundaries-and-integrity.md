---
id: reference-parser-container-boundaries-integrity
title: Nested parser bounds, compressed references, checksums and format acceptance
kind: reference
topics: [parsers, grammar-recovery, nesting, offsets, checksums, cbor, dns, png]
platforms: [windows, linux, macos, android, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Container boundaries and integrity evidence

## Child-parser bounds differ from the containing allocation's bounds

If O, L and P are nonnegative byte counts in one representable integer domain,
a child at parent-relative offset O with extent L fits parent extent P when
O <= P and L <= P-O. Establish the first condition before subtracting. These
checks prove containment only, not memory lifetime or the child's enforcement
of the passed bound; verify the actual input units and conversions first.

During investigation, record each parser's base, end, cursor and returned bytes
consumed. A child can remain inside the outer allocation while consuming a sibling
record. Conversely, some formats intentionally reference storage outside the
child's contiguous encoding; validate such references against their specified
base and domain rather than inventing a universal child-local offset rule.

## DNS compression offsets and expanded-name lengths use different coordinates

RFC 1035 name compression uses a two-byte pointer with leading bits 11 and a
14-bit offset from the beginning of the DNS message, not the current RDATA field.
When a length-delimited field contains a compressed name, its encoded length
counts compressed bytes rather than expanded name bytes. [1]

Track the outer input cursor separately from the pointer-following cursor and
output length. Check reference targets, termination and repeated/cyclic traversal
in malformed input. An offset inside the message is not by itself a valid name
reference. Do not transplant this historical name-encoding rule to every newer
DNS record type; the enclosing record's specification determines permitted use.

## A CBOR break marker closes one indefinite-length item in the right context

CBOR permits indefinite-length arrays, maps, byte strings and text strings.
The break byte FF is a syntax marker, not a data item. It closes one current
indefinite-length item; nested arrays/maps need their own closing markers. A
break after a map key without its value is malformed. [2]

Recover the container stack and expected next item before interpreting FF.
Scanning for that byte without decoding can mistake payload data for termination.
Keep input-exhaustion, valid container completion and nesting/resource limits
as separate conditions. A recursion-depth limit alone does not bound total items.

## CBOR indefinite strings have chunk-type restrictions

An indefinite CBOR byte/text string contains definite-length chunks of the same
string type, then a break. It cannot contain another indefinite string as a
chunk. Each text chunk must itself contain valid UTF-8, so a code point's encoding
cannot be split between chunks. [2]

Do not reuse array nesting rules for string chunks merely because both use an
indefinite-length marker. When recovering a decoder, identify the type-dependent
branch that controls legal children and how concatenated output size is accounted
for. A chunk individually fitting input does not establish bounded total output.

## Checksum coverage is a byte-range contract, not a type-name match

PNG's CRC covers chunk type and data, not the length field; even an empty chunk
has a CRC. [3] Recover the accumulator initialization, exact input bytes, byte/bit
order, update routine and final transformation before identifying an unknown
checksum solely from a constant or table.

An unkeyed checksum does not authenticate a sender: an input producer able to
change the bytes can also calculate its replacement checksum. Trace any separate
authentication mechanism. A failed checksum can explain why a modified field
never reaches its consumer, but a valid checksum does not establish safe lengths,
valid object state or trustworthy content.

## Unknown-tag handling is part of the grammar's compatibility contract

PNG distinguishes unknown critical chunks from unknown ancillary chunks using a
property bit in the chunk type. A decoder must signal that it cannot safely
interpret an unknown critical chunk; an unknown ancillary chunk can be ignored
for image display. [3]

For another format, recover whether unknown tags are rejected, skipped, preserved
or forwarded. Skipping still requires a trustworthy encoded extent. Successfully
displaying outer content does not prove an embedded record was interpreted, and
ignored payload bytes are not proof of covert execution. Malware behavior needs
the extraction/decoding and execution or external-effect path.

## Successful syntax parsing does not establish semantic or policy validity

CBOR explicitly distinguishes well-formed syntax, valid data-model semantics and
input expected by an application. [2] The distinction is useful during reverse
engineering even when an unknown format uses different terminology.

Label what each check proves: available bytes, legal encoding, consistent fields,
permitted operation or authorized principal. A complete parse can still yield an
unauthorized path or inconsistent object. A parser accepting bytes beyond a
normative format may indicate compatibility behavior, a bug or intentional payload
handling; establish the downstream effect before assigning a security conclusion.

## Primary sources and scope

Reviewed 2026-10-02. Protocol-specific facts are examples with explicit scope;
the investigation consequences and conditional range arithmetic are not claims
about observed target behavior. Workflow: playbook-re-parser-grammar.

1. [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035.html), section 4.1.4: name compression and encoded lengths; not a complete current DNS reference.
2. [RFC 8949](https://www.rfc-editor.org/rfc/rfc8949.html), sections 1.2 and 3.2: acceptance layers, nested indefinite items and strings.
3. [PNG third edition](https://www.w3.org/TR/2025/REC-png-3-20250624/), sections 5.3-5.5: CRC coverage and chunk properties.
