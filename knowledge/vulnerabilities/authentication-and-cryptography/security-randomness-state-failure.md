---
id: vulnerability-authentication-security-randomness-state-failure
title: Predictable, uninitialized, repeated, or failure-ignored security randomness
kind: vulnerability
topics: [cryptography, randomness, entropy, initialization, failure-handling, secrets]
platforms: [cross-platform]
architectures: [any]
---

# Predictable, uninitialized, repeated, or failure-ignored security randomness

## Definition and violated invariant

A security-randomness vulnerability occurs when a value whose role requires unpredictability, independent generator state or another stated random-source property is derived from state that does not provide that property, or when source failure or short output leaves bytes uninitialized, stale or predictably filled. The defect is defined by the consumer's security contract, not by whether bytes look varied.

Randomness roles differ. Secret keys, bearer tokens and challenges commonly require attacker-resistant unpredictability; salts primarily require protocol-defined uniqueness; encryption nonces have algorithm-specific requirements. Deterministic generation can be sound when its seed, state protection and lifecycle satisfy the governing construction.

## Conditions that establish the issue

Recover the generated value's exact security role and extent, selected generator and instance, initialization and seed provenance, return contract, requested and produced byte counts, retries and fallbacks, state sharing, fork/snapshot/reset behavior, concurrency, attacker observations or influence and final consumer. Prove the missing property under a stated attacker model and connect it to an accepted key, credential, challenge, nonce or security decision.

For prediction claims, establish feasible knowledge of state or a constrained candidate space within the value's lifetime and attempt limits. For uninitialized output, identify the unwritten extent and show it reaches the consumer.

## Evidence that is not sufficient

A call named `rand`, timestamp seed, deterministic generator, duplicate sample, low entropy estimate, virtual-machine snapshot, missing reseed or unchecked-looking call is not sufficient. The selected API may be a cryptographic generator, another layer may reject failure, the duplicate may have a different key or role, or fresh state may be mixed before use.

Observed statistical quality cannot certify unpredictability, and absence of observed duplicates cannot certify generator lifecycle. Preserve source and consumer contracts.

## Investigation sequence

Trace the exact buffer or integer from generator acquisition through initialization, fill, status handling, encoding and truncation into the security consumer. Record generator-instance identity and state transitions across process creation, fork, restore and restart. At each call site, reconcile the API's success convention and produced extent with the bytes later consumed.

In optimized native code, follow the result register and condition flags after the randomness call. A later branch may be inlined, folded or delegated, so absence of a nearby comparison is only useful when data flow proves the result is discarded and the entire destination is consumed.

## Hypothetical source example

```c
unsigned char session_key[32];
(void)getrandom(session_key, sizeof session_key, 0);
install_session_key(session_key, sizeof session_key);
```

On a path where this `getrandom` request fails, the code still consumes the whole automatic buffer. The finding requires the actual API result contract and a reachable failure; the call alone does not prove failure occurred or that all platforms share this convention. Other APIs and larger or differently flagged requests can also require handling a short successful result.

## Hypothetical x86-64 System V evidence

```asm
lea  0x20(%rsp), %rdi       ; destination session_key
mov  $0x20, %esi            ; requested length 32
xor  %edx, %edx             ; flags
call getrandom@PLT          ; RAX is byte count, or -1 on error
lea  0x20(%rsp), %rdi
mov  $0x20, %esi
call install_session_key    ; no use of RAX before full-buffer consumption
```

This hypothetical non-inlined sequence supports discarded-result data flow under the stated ABI; it does not show that `getrandom` returned short or failed. Stack offset, register allocation and instruction selection are compiler-dependent.

## Primitive and impact limits

The direct effect can be predictable secret material, repeated state, or consumption of partially unwritten bytes. Consequences depend on the role: impersonation, key recovery, challenge prediction, confidentiality or integrity loss, or disclosure of stale memory may require different additional evidence. Do not transfer a nonce-reuse consequence to a secret-key defect without the selected algorithm's analysis.

## Related knowledge and primary sources

`reference-crypto-randomness-state-failure` and `reference-crypto-nonce-iv-lifecycle` provide the underlying generator and role contracts. This profile retains the path from deficient state or result handling to the security consumer.

Reviewed 2026-10-09 against NIST [SP 800-90A Rev. 1](https://csrc.nist.gov/pubs/sp/800/90/a/r1/final) for deterministic random-bit-generator instantiation, state and generation concepts, and Linux [`getrandom(2)`](https://man7.org/linux/man-pages/man2/getrandom.2.html) for the named example's byte-count and error contract. The example is hypothetical and does not generalize that return convention to other APIs.
