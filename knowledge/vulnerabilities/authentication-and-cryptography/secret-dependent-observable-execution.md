---
id: vulnerability-authentication-secret-dependent-observable-execution
title: Secret-dependent comparison or access pattern with a supported observer
kind: vulnerability
topics: [cryptography, timing, side-channel, comparisons, access-patterns, secrets]
platforms: [cross-platform]
architectures: [any]
---

# Secret-dependent comparison or access pattern with a supported observer

## Definition and violated invariant

A secret-dependent execution vulnerability occurs when protected data controls branches, memory addresses, loop counts or other execution behavior and an attacker within the stated threat model can observe a signal that supports inference about that data. The finding requires both secret dependence and an observation relation; variable execution or an early exit alone does not establish disclosure.

Content-independent comparison has bounded scope. A helper whose time is independent of compared contents can still take time proportional to public length, and work before or after it can reintroduce secret dependence. Source-level uniformity does not prove uniform emitted code or hardware behavior.

## Conditions that establish the issue

Recover the protected value and extent, attacker-controlled inputs, source and emitted operations, branches and addresses dependent on secret data, platform and compiler/runtime behavior, observer location and precision, query or trace capability, environmental noise, repeated relation to the same secret, and final inference. Prove the signal is distinguishable under that model and reaches a security-relevant secret or decision.

For remote timing, include protocol scheduling, rate limits, concurrent work and response boundaries. For local cache or trace observations, state co-residency, shared resource and isolation assumptions.

## Evidence that is not sufficient

An early-return comparison, lookup table, variable duration, cache miss, branch trace, constant-time helper import or statistically different sample set is not sufficient. The compared value may be public, compiler output may differ, the observer may lack access or resolution, unrelated work may explain the signal, or the consumer may compare the wrong extent despite content-independent execution.

Avoid converting a static dependence into a demonstrated secret-recovery claim. Report the supported conditional exposure and missing observation premises.

## Investigation sequence

Trace attacker input and secret data into control flow, memory indices and variable work, then define the exact event an observer sees. Join measurements or traces to the same operation and secret generation, accounting for scheduling and instrumentation. Finally, follow the recovered or distinguishable property into an authentication or confidentiality consequence.

At binary level, inspect optimized code and called libraries. Record operand widths, loop bounds and exit branches; do not assume a source helper survived optimization or that one instruction sequence characterizes every build.

## Hypothetical early-exit example

```c
int equal_secret(const unsigned char *candidate, const unsigned char *secret, size_t length) {
    for (size_t i = 0; i < length; i++)
        if (candidate[i] != secret[i]) return 0;
    return 1;
}
```

The loop's work depends on the matching prefix, but vulnerability and impact require an observer capable of distinguishing that dependence across relevant queries to the same protected secret. It does not by itself prove remotely measurable timing or recoverability.

## Hypothetical x86-64 evidence

```asm
.loop:
movzbl (%rdi,%rcx), %eax   ; candidate byte
cmpb   (%rsi,%rcx), %al    ; compare secret byte
jne    .different          ; exit position depends on matching prefix
inc    %rcx
cmp    %rdx, %rcx
jb     .loop
```

This hypothetical optimized loop exposes secret-dependent control flow; register allocation and instruction selection are compiler-dependent. The snippet does not establish the observer, noise model or secret inference.

## Primitive and impact limits

The direct primitive is an observable relation to a secret-dependent operation. Consequences range from a one-bit validity distinction to partial or complete secret inference, depending on queries, signal quality and secret lifetime. Authentication bypass or decryption requires evidence that the learned information suffices for the accepting consumer.

## Related knowledge and primary sources

`reference-crypto-timing-comparison-evidence` and side-channel validation references provide comparison and observation limits. This profile keeps data dependence, observer capability and security consumer together.

Reviewed 2026-10-09 against the OpenSSL [`CRYPTO_memcmp`](https://docs.openssl.org/master/man3/CRYPTO_memcmp/) contract for the bounded distinction between content and length dependence. The examples are hypothetical analytical aids, not measurements or a universal constant-time guarantee.
