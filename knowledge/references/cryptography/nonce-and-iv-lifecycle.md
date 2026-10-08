---
id: reference-crypto-nonce-iv-lifecycle
title: Nonce and initialization-vector requirements across keys, writers and resets
kind: reference
topics: [cryptography, nonces, initialization-vectors, keys, uniqueness, lifecycle, authenticated-encryption]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Nonce and IV lifecycle evidence

## A nonce requirement is scoped to its algorithm and key

RFC 5116's authenticated-encryption interface requires distinct encryption nonces
for a given key, except its all-zero-length nonce case. The selected algorithm
defines allowed nonce lengths and properties. This is not a rule for every
cryptographic construction or initialization vector (IV). [1]

For investigation, identify algorithm/mode, actual key generation and the nonce
bytes consumed by encryption. Equal displayed nonce values under different keys
are not automatically the same violation; two key IDs do not prove distinct key
material. Preserve algorithm-specific exceptions and conditions. No portable IV
size, random-generation rule or universal consequence is assumed.

## Uniqueness must include concurrent writers and restored state

For analysis, map nonce allocation across writers sharing a key, process restarts,
counter rollover, persisted state, snapshot restore and rekeying. RFC 5116
discusses coordination when several devices encrypt under one key. [1]

A local increment or fresh process launch does not establish global uniqueness.
Conversely, a possible reset does not prove that duplicate nonces reached the
same-key encryption operation. Retain the actual allocation, accepted value,
key generation and recorded use. If only static code is available, describe the
supported lifecycle and missing premises rather than asserting observed reuse
or recovered plaintext.

## Nonce secrecy, unpredictability and uniqueness are different properties

For investigation, determine the property's actual requirement from the selected
mode/protocol. A public nonce can satisfy a uniqueness requirement; being randomly
generated does not itself certify uniqueness across the relevant key lifecycle.

Keep IV/nonce generation, serialization and reconstruction separate. Some protocols
combine transmitted and implicit context into the value actually consumed;
RFC 5116 describes partially implicit nonces. [1] A packet field alone may not be
the complete nonce. Do not compare partial encodings as complete encryption inputs
or promote a naming convention to a mode-specific security contract.

## Reuse evidence and resulting harm need separate supported claims

For analysis, bind two accepted encryption operations to the same key material,
complete nonce and required algorithm condition before reporting reuse. Then
state only the security property the algorithm's source supports as affected.

A repeated string, failed encryption attempt or extracted default does not prove
two successful uses. Lack of observed duplicates only describes the captured
writers/intervals; it does not certify the lifecycle. AEAD verification, replay
acceptance and authorized content selection are separate questions. Use
reference-crypto-aead-verification-boundary for output authenticity limits.

## Source and scope

Reviewed 2026-10-08. RFC 5116 sections 2.1, 3.1 and 3.2: scoped nonce inputs,
coordination and implicit representations. No nonce-construction recipe,
reuse exploitation or current algorithm-policy recommendation.

1. [RFC 5116](https://www.rfc-editor.org/rfc/rfc5116.html): authenticated-encryption interface and nonce handling.

Workflow: playbook-crypto-operation-evidence. Scope belongs with every comparison;
the word nonce alone cannot supply an algorithm's uniqueness or IV requirements.
