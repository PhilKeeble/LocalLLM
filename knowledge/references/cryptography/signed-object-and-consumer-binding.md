---
id: reference-crypto-signed-object-consumer-binding
title: Signature verification, exact signed representation and consumed object identity
kind: reference
topics: [cryptography, signatures, hashes, object-binding, canonicalization, parsers, authorization]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Signed representation and consumed-object evidence

## Signature verification is a relation between message, key and signature

NIST's signature model uses a private key to generate a signature on data and
the corresponding public key to verify it. Mathematical verification and the
additional assurances required for trusted validation are distinct. [1]

For investigation, retain exact message representation or defined digest input,
algorithm/parameters, verification key, signature and result. A success label
does not identify who may authorize this operation unless trusted key selection
and policy also support that relation. A signature is not encryption and does
not make the content safe or its execution benign. Keep authentication, object
authorization and observed effect as separate claims.

## A verified digest binds content only through a trusted reference and selection

For analysis, trace original bytes through any digest/signature transform to the
verified representation, then to the object actually parsed, installed or used.
Preserve extents, selected member, path/object generation and result.

An untrusted expected digest does not authenticate content simply because it
matches. A trusted manifest can bind a member only under its actual selection
and digest rules. Reopening a name after verification can select changed bytes.
Keep checked and consumed objects joined by evidence rather than a filename or
file-size match. Shared update/object invariants remain in
reference-logic-update-verification-installation.

## Canonicalization is a specified representation, not arbitrary normalization

RFC 8785's JSON Canonicalization Scheme defines a deterministic representation
under its input restrictions, including no duplicate property names and preservation
of string data. It does not apply Unicode normalization to those strings. [2]

For investigation, identify the actual scheme and parser/serializer consumers.
A custom sorted JSON display cannot be assumed equivalent to JCS or to the bytes
used for verification. Keep numeric representation, string preservation and
duplicate handling under the selected contract. A valid signature over one
canonical object does not authenticate another consumer's different field
interpretation. Other formats require their own canonicalization rules.

## Unsigned context and mutable state can change a signed message's effect

For analysis, identify which operation, audience, object, environment and lifecycle
fields are bound by the signed representation. Follow defaulted or external values
that select the resulting effect.

The same authenticated bytes can be interpreted in a different context when that
context is outside the binding. This is a relation to investigate, not an automatic
replay or authorization defect. Establish accepted context and sensitive use,
retaining expiry, trusted state and policy prerequisites. A key's identity or a
signature's presence cannot supply those missing premises.

## Sources and scope

Reviewed 2026-10-08. FIPS 186-5 sections 2-3 for signature/key/validation concepts;
RFC 8785 sections 3.1-3.2 for a scoped canonicalization example. No current
algorithm selection, key-size table or private signature implementation assumed.

1. [NIST Digital Signature Standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf): signature relation and validation assurances.
2. [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html): JCS input and string/serialization rules.

Workflow: playbook-crypto-operation-evidence. Cryptographic success and the
authorized consumption of those exact bytes need separate evidence.
