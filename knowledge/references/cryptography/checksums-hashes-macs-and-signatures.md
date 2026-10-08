---
id: reference-crypto-integrity-authentication-roles
title: Checksums, unkeyed hashes, MACs and signatures establish different relations
kind: reference
topics: [cryptography, checksums, hashes, mac, signatures, integrity, authentication]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Integrity and authentication roles

## An error-detection checksum is not automatically adversarial authentication

RFC 3385 discusses cyclic redundancy checks (CRCs) as error-detection codes. [1]
Their error-detection purpose is different from authenticating an authorized
producer against deliberate modification.

For investigation, identify the algorithm, covered bytes and how the expected
value is obtained. A CRC or ordinary checksum can detect corruption without
proving sender identity or trusted content selection. Conversely, finding such
a field does not prove that a separate authenticated layer is absent. Trace
the complete protection and acceptance path before reporting an integrity defect.
No polynomial, collision recipe or checksum-based malware verdict is supplied.

## An unkeyed fingerprint needs a trusted expected value to bind an object

For analysis, an unkeyed content digest can identify the bytes examined, subject
to its algorithm and byte extent. It does not independently identify an authorized
producer when both content and expected digest come from an untrusted source.

Bind algorithm, representation, trusted reference and comparison result. A digest
in a signed manifest can participate in authenticated selection only if the
manifest's signature/policy and member binding hold. An extracted or partial-
memory hash is not a whole-file identity. Use
reference-malware-indicator-provenance and reference-crypto-signed-object-consumer-binding.
This is a trust-relation distinction, not a claim that every hash lacks security use.

## A MAC authenticates through shared-key possession, not public verifiability

RFC 2104 describes HMAC as a message authentication code (MAC) computed and
verified using a shared secret key. [2]

For investigation, identify exact message, key generation, accepted tag extent
and verification result. Parties able to generate valid MACs through that shared
key cannot be distinguished merely by tag validity. Key distribution, audience
and operation authorization remain separate. A keyed construction is not itself
encryption; a tag cannot supply confidentiality for its visible message. This
reference adopts HMAC's role, not the older source's example algorithms, strength
estimates or recommendations.

## A signature verifies under a public key whose trust must be established

NIST distinguishes private-key signature generation from corresponding public-key
verification and the additional assurances for validation. [3]

For investigation, retain signed representation, algorithm/parameters, verification
key, result and authorized signer policy. The key's public availability does
not make every key trusted. A valid signature over selected bytes does not prove
freshness, executable safety or correct object consumption. Comparing a signature
field's length or shape is not mathematical verification. Keep the claimed
security role separate from the presence of crypto-looking strings or routines.

## Sources and scope

Reviewed 2026-10-08. RFC 3385 introduction and section 10 for CRC error-detection purpose;
RFC 2104 introduction/definition for shared-key MAC roles; FIPS 186-5 sections
2-3 for signature and validation roles. No current cryptographic-policy advice.

1. [RFC 3385](https://www.rfc-editor.org/rfc/rfc3385.html): error-detection context, not an authentication scheme.
2. [RFC 2104](https://www.rfc-editor.org/rfc/rfc2104.html): HMAC role; obsolete example algorithm choices are not adopted.
3. [NIST signature standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf): private/public-key and validation distinctions.

Workflow: playbook-crypto-operation-evidence. Mechanism presence, successful
verification, authorization and observed effect remain separate claims.
