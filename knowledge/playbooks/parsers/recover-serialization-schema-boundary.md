---
id: playbook-re-serialization-schema-boundary
title: Recover serialization schemas and trace decoded values to sensitive use
kind: playbook
topics: [reverse-engineering, serialization, schema-recovery, parsers, vulnerability-analysis, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover the serialization schema boundary

## Bind a format hypothesis to the actual decoder

Find the byte source, outer framing and transformations before decoding. Correlate
dispatch masks, cursor arithmetic, generated accessors, descriptors and error
strings. Neither a library signature nor one successful generic decode establishes
the message's application type. Mark uncertain regions rather than recursively
decoding every plausible byte span as a nested object.

Use reference-parser-tlv-asn1-encoding, reference-parser-cbor-types-schema,
reference-parser-protobuf-types-presence-evolution and
reference-parser-offset-based-serialization for scoped format anchors.

## Recover both the wire field and its application meaning

Record encoded tag/class, width, length unit, presence, repetition, nested type,
default and conversion into the consuming representation. Locate the schema
selected by version/opcode/context. Distinguish an encoded scalar from a native
pointer, object layout or enum discriminator inferred by the decompiler.

For custom formats, follow both producer and consumer where available. Recover
unknown-tag handling, checksums, padding and trailing-byte policy from evidence;
do not borrow another format's rules just because both use TLV or varints.
Use playbook-re-parser-grammar for field-by-field reconstruction.

## Follow bounds through child items and referenced objects

Recover parent extent, child extent, offset base and bytes consumed. Check that
length decoding and subsequent arithmetic are valid before checking containment.
For offset-based structures, follow each referenced extent and interpretation;
the enclosing buffer size is not a native object-size guarantee.

Distinguish a valid primitive/constructed tag from a complete child, a bounded
child from bounded aggregate work, and structural verification from application
policy. A recursion cap does not bound all repeated entries or output allocation.

## Reconstruct final state after defaults, duplicates and unknown fields

Trace what the application actually sees after parsing, merging and conversions.
Determine whether absent, empty, zero, null and unset are distinguishable. Follow
oneof/union selection together with its payload, and track unknown fields through
forwarding or reserialization. Use playbook-re-parser-differentials when two
components apply different rules.

Constructed logic candidate: a validator examines one representation while a
later schema selects another operation or resolves a different object. Establish
the actual decision and forbidden effect; schema evolution alone is not a flaw.

## For malware, separate decoded configuration from executed behavior

Retain original encoded bytes, recovered schema and uncertain interpretations.
Bind decoded fields to configuration storage, command dispatch or external effects.
A field named command, a valid certificate encoding or a nested byte string does
not prove execution, trust or family attribution.

Document which branch uses the value, its transformations and any authority gate.
Keep capability inferred from reachable code separate from behavior observed in
an authorized analysis. Do not execute an unknown object merely to assign a type.

## Report exactly what the decoding evidence proves

For each finding, state input control, schema/profile, checked bytes, consuming
bytes/objects, feasible path and violated invariant. Record unknown configuration
or target behavior explicitly. Preserve the distinction between malformed encoding,
unsafe implementation, valid-but-unexpected data and unauthorized operation.

Reviewed 2026-10-02. The four format references above provide primary-source
anchors. This workflow supplements reverse engineering; it is not a claim that
any target or generated parser has been executed or validated.
