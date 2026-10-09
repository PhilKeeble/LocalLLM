---
id: vulnerability-kernel-physical-fault-injection-security-bypass
title: Physical fault injection bypasses a security-sensitive transition
kind: vulnerability
topics: [hardware, firmware, fault-injection, voltage-glitch, clock-glitch, electromagnetic]
platforms: [embedded, firmware]
architectures: [any]
---

# Physical fault injection bypasses a security-sensitive transition

## Definition and violated invariant

This vulnerability occurs when a controlled voltage, clock, electromagnetic, optical or related physical disturbance induces a fault that reproducibly bypasses a security check or corrupts a protected transition. The invariant is that the stated physical attacker must not be able to turn faulted execution into an unauthorized accepted state, data disclosure or control transfer.

Fault injection actively perturbs computation and differs from a physical side channel that only observes emissions. A crash, reset or random corruption is not yet a security bypass.

## Conditions that establish the issue

Define target device and revision, physical access, injection method and location, timing/trigger precision, parameter range, repetitions, induced fault model, security operation, expected result, faulted result and resulting authority. Demonstrate reproducibility above uncontrolled error and validate that the protected effect actually occurs.

Establish whether the fault skips an instruction, changes data, corrupts a bus transfer, alters sensing or affects persistent state; do not infer the mechanism solely from the final result. Include detectors, retries, redundancy and reset behavior.

## Evidence that is not sufficient

Voltage or clock control, an EM probe, boot failure, corrupted output, sensor alert or one anomalous success is not sufficient. Environmental instability and ordinary software races can create similar effects. A fault near a signature comparison does not prove that comparison was bypassed or that unverified code executed.

Do not generalize a successful setup across packaging, board, silicon revision, frequency or temperature without evidence.

## Investigation sequence

Map the security transition and observable milestones before and after it. Recover check, branch, state commit and use of the accepted result in firmware or hardware. Correlate injection timing with these events and classify outcomes, including detected faults, resets and unauthorized success.

In binary or RTL review, identify single points whose corruption could create acceptance and whether later independent checks consume the result. Physical testing evidence must state equipment, geometry and statistics; static code only supplies candidates.

## Constructed fault model

A hypothetical boot ROM verifies an image, branches once on the Boolean result and immediately jumps to the image. A precisely timed fault that changes the branch outcome could bypass verification if the unchecked image actually executes. The source pattern alone is not a vulnerability; hardware susceptibility, repeatability and control transfer must be demonstrated.

## Primitive and impact limits

Report the induced state change, success probability, attempts, physical access and resulting capability. Impact can include protected readout, unauthorized boot or persistent modification. Random denial of service should not be promoted to code execution without controlled accepted behavior.

## Related knowledge and primary sources

Boot-chain and debug profiles define common protected transitions. This profile supplies the physical attacker and fault-model evidence threshold.

Reviewed 2026-10-09 against [MITRE CWE-1247](https://cwe.mitre.org/data/definitions/1247.html), [MITRE CWE-1319](https://cwe.mitre.org/data/definitions/1319.html) and Dehbaoui et al., [Injection of transient faults using electromagnetic pulses](https://eprint.iacr.org/2012/123). The model is hypothetical; published fault results are setup-specific.
