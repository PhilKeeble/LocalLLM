---
id: vulnerability-information-physical-side-channel-leakage
title: Secret-dependent physical side-channel leakage
kind: vulnerability
topics: [information-disclosure, physical-side-channel, power-analysis, electromagnetic, acoustic]
platforms: [hardware, firmware, cross-platform]
architectures: [any]
---

# Secret-dependent physical side-channel leakage

## Definition and violated invariant

This vulnerability permits an attacker to infer protected data from secret-dependent physical phenomena such as power consumption, electromagnetic emissions, acoustic emissions or another measurable emanation. The violated invariant is that observable physical behavior must not carry a usable signal about the protected state under the stated physical attacker model.

Physical side-channel leakage differs from fault injection: leakage observes computation, while fault injection perturbs it to change behavior. One campaign can use both, but each requires separate evidence.

## Conditions that establish the issue

Define the device and implementation, secret-bearing operation, measured phenomenon, sensor position and bandwidth, trigger or alignment method, chosen-input capability, trace count, leakage model, signal processing and recovered predicate. Show reproducible statistical or attack-level dependence on protected data and validate the inference against known or independently checked values.

Include packaging, shielding, power delivery, clocking, noise, concurrent activity and attacker distance or contact. Results from one board revision, cryptographic implementation or measurement setup do not automatically transfer to another.

## Evidence that is not sufficient

Variable power use, audible noise, visible electromagnetic activity, physical proximity or a secret-dependent branch in source is not sufficient. The variation may reflect public input or unrelated work, and a detectable difference may not support useful inference. Correlation in a small unblinded sample can be a measurement artifact.

Passing a generic leakage test does not prove resistance to every model or full key recovery; failing one statistical test identifies leakage evidence but not necessarily a practical extraction path. State what was actually measured.

## Investigation sequence

Trace protected values into operations likely to change physical activity, including data-dependent control flow, memory access and arithmetic. Recover algorithm variants, masking, blinding, randomness, hardware acceleration and compiler transformations. Align measurements to the target operation and separate fixed-versus-random input effects, drift and external noise.

For binary review, identify secret-dependent branches, table accesses and variable-latency operations as candidates, then connect them to the physical implementation and measurement model. Machine code alone cannot establish measurable emissions or extraction reliability.

## Constructed measurement model

A hypothetical device performs square-and-multiply exponentiation and skips the multiply when a secret exponent bit is zero. If an attacker can align repeated power traces for chosen messages and reliably distinguish the two operation patterns, traces may reveal exponent-bit predicates.

The source pattern alone is not proof: the implementation may use blinding, masking, constant-pattern hardware or noise that defeats the stated classifier. A recovered full key requires enough correctly ordered predicates and validation, not merely two visually different traces.

## Primitive and impact limits

Report the information recovered per observation, confidence, traces, equipment, access, distance and affected units. The primitive may range from operation classification to key recovery. Do not generalize a laboratory result beyond its tested hardware and conditions.

Recovered credentials or keys have their own scope, binding and lifetime. Physical leakage does not write state or independently establish code execution.

## Related knowledge and primary sources

Software timing and microarchitectural channels use different observers and are covered separately. This profile keeps the physical measurement and implementation boundary explicit.

Reviewed 2026-10-09 against [MITRE CWE-1300](https://cwe.mitre.org/data/definitions/1300.html), [FIPS 140-3](https://csrc.nist.gov/pubs/fips/140-3/final) treatment of non-invasive security, Kocher, Jaffe and Jun's [Differential Power Analysis](https://www.princeton.edu/~rblee/ELE572Papers/Fall04Readings/DifferentialPowerAnalysis_Kocher.pdf), and Genkin, Shamir and Tromer's [RSA key extraction via low-bandwidth acoustic cryptanalysis](https://eprint.iacr.org/2013/857). Research results are implementation- and setup-specific, not universal device behavior.
