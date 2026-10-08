---
id: playbook-crypto-operation-evidence
title: Recover cryptographic inputs, trust decisions and consumer effects
kind: playbook
topics: [cryptography, investigation, authentication, data-flow, trust, failure-policy]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Cryptographic operation investigation

## Classify the operation before assigning a security property

Identify the executed operation, input representation and consumer. Separate
error detection, unkeyed hashing, shared-key authentication, signatures,
encryption and password verification. A library import or algorithm name is
discovery evidence; it does not prove execution, key trust or correct use.

Use reference-crypto-integrity-authentication-roles for the factual distinctions.
Record the exact claim under investigation, such as message authenticity or
unauthorized key use. Avoid turning an unspecified cryptographic weakness into
demonstrated compromise.

## Bind the key, generator and nonce to the same operation

Recover actual key or supported handle identity, owner, operation authority and
lifecycle state. Follow randomness initialization, result extent and fallback;
then the algorithm's nonce/IV requirement across writers and state restoration.
Do not equate an opaque handle with disclosure or a restart with nonce reuse.

Use reference-crypto-key-access-lifecycle, reference-crypto-randomness-state-failure
and reference-crypto-nonce-iv-lifecycle. Retain missing seed, key or history
evidence explicitly. A value's role determines whether uniqueness,
unpredictability or another property is relevant.

## Recover the complete verification decision and covered representation

Map bytes, lengths, signature/tag, associated data, certificate trust inputs,
reference service identity and the actual result consumer. Include overrides,
callbacks and failure/retry branches. A successful mathematical check cannot
alone establish trusted signer identity or application authorization.

Use reference-crypto-aead-verification-boundary,
reference-crypto-signed-object-consumer-binding and
reference-crypto-certificate-service-identity. Establish whether output is
released before authentication completes and whether the verified representation
is the one later parsed or acted upon. Unavailable paths remain unresolved.

## Follow freshness, negotiation and verifier state through acceptance

Recover authenticated counters/timestamps, retained replay state, negotiated
policy and fallback conditions. Bind enrollment and login to the password
representation, verifier parameters and bounded resource use actually selected.
Successful authentication alone cannot establish freshness or acceptable policy.

Use reference-crypto-freshness-replay-state,
reference-crypto-negotiation-fallback-policy and
reference-crypto-password-verifier-binding. Keep protocol-specific early-data
limits local; do not apply them to every encrypted channel.

## State the supported effect and observation limits

For a candidate finding, identify controlled input, reachable decision, violated
requirement and resulting consumer effect. For timing claims, identify secret
dependence, observer access and collection confounders; a noisy duration or a
constant-time helper does not settle the whole operation.

Use reference-crypto-timing-comparison-evidence. Report established facts,
inferences and missing relations separately. Crypto APIs occur in ordinary
software and malware; identify the behavior and authority involved before
classifying intent. This workflow requires no target execution or attack recipe.

## Basis and scope

Reviewed 2026-10-08 against the cited cryptography references and their inspected
primary contracts. This is an evidence-recovery workflow, not an algorithm,
parameter or deployment recommendation. Update-specific binding belongs in
playbook-crypto-update-evidence.
