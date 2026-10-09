---
id: vulnerability-information-microarchitectural-cross-context-side-channel
title: Microarchitectural or transient-execution cross-context side channel
kind: vulnerability
topics: [information-disclosure, side-channel, cache-timing, transient-execution, speculation]
platforms: [cross-platform]
architectures: [any]
---

# Microarchitectural or transient-execution cross-context side channel

## Definition and violated invariant

This vulnerability lets an unauthorized observer infer protected data because victim activity changes shared microarchitectural state or resource timing. Candidate channels include caches, predictors, translation structures, execution units, contention and transient execution whose architectural results are discarded but whose microarchitectural effects remain observable.

The violated invariant is not speculation or timing variation alone. A security issue requires a secret-dependent transmitter, an observer with access to a correlated signal, and an isolation boundary that should prevent the inference.

## Conditions that establish the issue

Define victim and observer contexts, protected value, shared resource, transmitter operation, receiver measurement, synchronization, noise model and inference. Show that the observer can cause or await the relevant victim state and distinguish secret classes with reproducible advantage. Establish applicable processor behavior, topology and mitigation state rather than generalizing one microarchitecture.

For transient execution, connect attacker influence to a mistrained prediction, delayed permission/bounds resolution or other transient window, then connect protected data to an encoding operation and a non-transient receiver. For ordinary cache timing, transient execution is not required if architectural secret-dependent access already creates the signal.

## Evidence that is not sufficient

A conditional branch on a secret, a cache access, speculative instructions in a trace, simultaneous multithreading or a timing difference is not sufficient. The contexts may not share the relevant structure, the signal may depend only on public input, the protected data may never reach a transmitter, or noise and scheduling may prevent inference.

An architectural fault does not prove that protected data was forwarded transiently. Conversely, absence of an architectural result does not refute a microarchitectural signal. Use the documented behavior and affected processor conditions.

## Investigation sequence

Draw the channel as `secret -> victim operation -> shared state -> observer measurement -> inference`. Recover address relationships, cache-line or predictor aliasing, core/thread placement, timers, flushing or eviction capability and repetition. Locate fences, masking, isolation, predictor controls and platform mitigations on the exercised path.

At binary level, identify the secret load, bounds or permission decision, data-dependent address or contention operation and speculation barriers. Preserve dependencies through compiler transformations. A gadget-like sequence is only a candidate until the observer and supported hardware behavior complete the chain.

## Constructed representation

This hypothetical pattern encodes an architecturally read secret into one of 256 cache-separated locations after an attacker-influenced bounds check:

```c
if (index < public_length)
    value = probe[(size_t)secret[index] * 4096];
```

Architecturally, an out-of-range `index` should not reach the load. A transient disclosure claim additionally requires an affected processor to execute the body transiently after a misprediction, `secret[index]` to access protected data in that window, the probe effect to persist, and the attacker to distinguish the selected location. The source pattern alone proves none of these hardware conditions.

## Primitive and impact limits

Report the inferred unit, error rate, bandwidth, required co-location or scheduling, address knowledge, repetitions and affected boundary. Some channels reveal only aggregate activity or a bit predicate; others can recover bytes under controlled conditions.

The direct effect is information inference. It does not modify victim memory or independently establish code execution. A disclosed pointer or key has the downstream limits of that specific value.

## Related knowledge and primary sources

`reference-specialist-microarchitectural-side-channel-evidence` provides deeper architectural-versus-microarchitectural reasoning. This profile retains the complete transmitter, channel, observer and inference threshold for isolated retrieval.

Reviewed 2026-10-09 against Intel's [Analysis of Speculative Execution Side Channels](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/analysis-speculative-execution-side-channels.html), Arm's [Cache Speculation Side-channels whitepaper](https://developer.arm.com/documentation/102816/latest/) and [MITRE CWE-1422](https://cwe.mitre.org/data/definitions/1422.html). The example is constructed; susceptibility and controls are processor- and configuration-specific.
