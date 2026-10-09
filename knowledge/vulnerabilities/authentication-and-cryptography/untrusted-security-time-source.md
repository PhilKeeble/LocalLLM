---
id: vulnerability-authentication-untrusted-security-time-source
title: Security decision uses an untrusted, rollbackable, or discontinuous time source
kind: vulnerability
topics: [authentication, time, expiry, freshness, rollback, monotonic-clock]
platforms: [cross-platform, firmware]
architectures: [any]
---

# Security decision uses an untrusted, rollbackable, or discontinuous time source

## Definition and violated invariant

A security-time vulnerability occurs when expiry, freshness, lockout, certificate, lease or anti-replay policy relies on a clock or counter whose authority, monotonicity, persistence, synchronization or suspend/reset behavior does not meet that decision's contract. Calendar validity and elapsed duration are different questions: a monotonic clock can measure intervals within its defined lifecycle but does not inherently supply trusted civil time or persistence across restart.

Clock discontinuity is not itself a vulnerability. An attacker must control or predict the relevant change, or the system must enter a reachable state that makes a forbidden object or action acceptable.

## Conditions that establish the issue

Recover the security decision and required time semantics, source clock or counter, units and width, comparison signedness, synchronization and trust source, privilege needed to alter it, rollback and reset behavior, boot and snapshot persistence, suspend/resume treatment, error and unknown-time policy, attacker capability, accepted object and resulting effect. Prove the time behavior changes a protected decision contrary to policy.

For distributed systems, include skew assumptions and which node's time governs acceptance. For retained anti-rollback state, distinguish protected counters from display versions and ordinary cache timestamps.

## Evidence that is not sufficient

A call to `time`, wall clock, monotonic clock, RTC read, timestamp, expiry field, clock adjustment, integer conversion or device reset is not sufficient. The caller may lack authority to influence the source, signed or server state may bound acceptance, the policy may tolerate the change, or the affected object may be independently revoked.

A timestamp can be authentic yet stale, and a monotonic value can be unsuitable after reboot even though it never moves backward within one boot.

## Investigation sequence

Trace the timestamp or counter from acquisition through conversion, comparison and failure handling into the security decision. Record source identity, set/sync paths, boot and resume initialization, persisted state and actor authority. Explore forward jumps, rollback, wrap, unavailable time and concurrent updates according to the target's actual contract.

At binary level, identify the selected clock ID or platform service, returned width and error handling. Follow arithmetic for unit conversion, subtraction overflow and signed comparisons before interpreting branch meaning.

## Hypothetical rollback example

```text
now = wall_clock()
if verify_signature(token) and now <= token.expiry:
    accept(token)
```

The signature authenticates the expiry value but not the trustworthiness of `now`. The path is vulnerable only if an attacker with less authority than the token grants can roll the accepted clock backward, the token remains otherwise valid, and no protected freshness or revocation state rejects it. A trusted synchronized wall clock can satisfy a calendar-expiry policy.

## Primitive and impact limits

The direct primitive is acceptance or denial under an incorrect security-time relation, including reuse of expired authority, bypass of lockout or rejection of valid service. Consequences are bounded by the affected policy and object. Clock control by an already-equivalent privileged actor may add no escalation.

## Related knowledge and primary sources

Replay, update rollback, certificate and state-transition references provide consumer-specific time contracts. This profile keeps source authority and the accepting comparison together.

Reviewed 2026-10-09 against POSIX [`clock_gettime`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/clock_getres.html) semantics distinguishing settable realtime from a monotonic clock with an unspecified origin. Platform clocks differ in suspend and persistence behavior, so the example is hypothetical and no clock name alone establishes suitability.
