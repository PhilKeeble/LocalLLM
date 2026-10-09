---
id: vulnerability-authentication-nonce-iv-lifecycle-failure
title: Nonce or IV reuse, collision, or multi-writer lifecycle failure
kind: vulnerability
topics: [cryptography, nonce, initialization-vector, aead, counters, lifecycle]
platforms: [cross-platform]
architectures: [any]
---

# Nonce or IV reuse, collision, or multi-writer lifecycle failure

## Definition and violated invariant

A nonce or initialization-vector lifecycle vulnerability occurs when encryption operations violate the selected algorithm or protocol's required relation between the complete nonce or IV and the key, such as uniqueness, unpredictability or construction constraints. For AEAD algorithms under the RFC 5116 interface, each encryption invocation with a given key requires a distinct nonce except where the selected algorithm permits a zero-length nonce.

The complete cryptographic input may combine transmitted, implicit and derived fields. A repeated packet field is not necessarily a repeated nonce, and an equal nonce under demonstrably different keys is not the same-key reuse condition.

## Conditions that establish the issue

Recover algorithm and mode, key material or generation identity, complete nonce/IV bytes presented to encryption, allocation rule, writer coordination, counter width and rollover, persistence, process/device restart, snapshot or rollback behavior, concurrency and successful-use records. Establish at least two accepted encryption operations that violate the construction's requirement under the relevant key and scope.

When only static code is available, report the lifecycle that permits collision or reuse and the missing runtime premises. Do not claim an observed collision, plaintext recovery or forgery without the additional evidence required for that conclusion.

## Evidence that is not sufficient

A fixed-looking field, zero IV, random nonce, local counter, process restart, shared key ID or two equal displayed values is not sufficient. The algorithm may define a fixed component, a hidden component may differ, keys may be distinct, the attempted operation may have failed, or persistent allocation may coordinate writers.

Random selection does not prove uniqueness, and a monotonic counter in one process does not prove uniqueness across processes, devices, restored snapshots or rollover.

## Investigation sequence

Build a lifecycle table keyed by actual key generation and writer. Record nonce components, allocation and commit point, process/device identity, restart and restore state, concurrency, encryption result and ciphertext consumer. Compare complete byte strings only after reconstructing implicit fields and endianness. Follow failures and retries to learn whether a nonce is reserved before or after successful encryption.

At binary level, trace the nonce pointer and length passed to the selected primitive, counter load/increment/store width, synchronization and persistence calls. Confirm which key handle or bytes reach the same invocation.

## Hypothetical multi-run example

```text
persistent key K
process start: counter = 0
encrypt M1 with nonce encode(counter++), key K
process restart: counter = 0
encrypt M2 with nonce encode(counter++), key K
```

If both operations succeed with the same complete encoded nonce and unchanged key `K`, the lifecycle violates a per-key uniqueness requirement such as RFC 5116's AEAD contract. The cryptographic consequence remains algorithm-specific; the diagram does not itself establish recovered plaintext or a valid forgery.

## Primitive and impact limits

The direct effect is violation of the selected construction's nonce/IV premise for successful encryption operations. Resulting confidentiality, integrity or key-recovery impact depends on the exact algorithm, message relation, attacker observations and query capabilities. Replay acceptance is a separate receiver-state question even when a nonce appears in the message.

## Related knowledge and primary sources

`reference-crypto-nonce-iv-lifecycle` provides complete-input, key-scope and multi-writer fundamentals. Randomness and replay references cover separate properties that should not be conflated with nonce uniqueness.

Reviewed 2026-10-09 against [RFC 5116 sections 2.1 and 3](https://www.rfc-editor.org/rfc/rfc5116.html) for the AEAD nonce interface, per-key distinctness, partially implicit nonces and multiple-device coordination. The example is hypothetical; other modes and protocols require their own nonce or IV contract.
