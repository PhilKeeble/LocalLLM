---
id: vulnerability-resource-asymmetric-cpu-work-amplification
title: Asymmetric attacker-to-defender CPU work amplification
kind: vulnerability
topics: [resource-exhaustion, cpu, amplification, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Asymmetric attacker-to-defender CPU work amplification

## Definition and violated invariant

This vulnerability lets an actor trigger substantially more defender computation than the effort, bandwidth or authorization needed to request it, without an effective work budget or admission control. The violated invariant is that expensive work must be bounded, authenticated, rate-limited or charged so a low-cost request stream cannot monopolize shared CPU.

Asymmetry can arise from cryptographic work, repeated cache misses, fan-out, retries, conversions or expensive validation. Algorithmic-complexity defects are a more specific subtype when crafted input changes the algorithm's growth order.

## Conditions that establish the issue

Identify the attacker request cost and rate, defender operations and cost, concurrency, cache state, authentication position, rate or work limits and shared availability target. Show a feasible request stream consumes the protected CPU or worker budget and delays or rejects authorized work.

Include downstream fan-out and work performed after the client disconnects. A small network packet can trigger many local operations even when the response is small.

## Evidence that is not sufficient

An expensive function, cryptographic verification or high CPU profile is not sufficient. The path may require equivalent attacker work, strong authentication, scarce credentials, bounded concurrency, cached results or a quota below the harmful rate. A laboratory worst case without reachable inputs or service contention does not establish the vulnerability.

Do not equate traffic amplification with computational amplification; record bytes and CPU separately.

## Investigation sequence

Trace one admitted request through all synchronous and asynchronous work. Count operations, fan-out, retries and cancellations per controllable unit. Recover cache keys and deduplication because attacker-selected uniqueness can defeat otherwise effective caching. Identify where cost is incurred relative to authentication and quota reservation.

At binary level, locate loops, cryptographic primitives, decompression, database or IPC fan-out and work-queue submission. Compare request parsing cost with downstream execution and determine whether disconnect or timeout cancels already queued work.

## Constructed flow

A hypothetical unauthenticated request contains one identifier. The service fans it out to 200 backends, verifies a signature on every response and continues after the client disconnects. One request therefore reserves little attacker bandwidth but large defender CPU and downstream work.

The finding requires reachable fan-out, insufficient concurrency or per-actor limits and consequential contention. If requests require a scarce authenticated entitlement and consume a reserved tenant budget, the same work may be intentional and bounded.

## Primitive and impact limits

Report the amplification ratio in the relevant units, sustainable request rate, worker or CPU budget, affected principals and containment. The direct effect is degraded availability. Starvation, queue exhaustion or retry storms may form additional root causes; memory corruption does not follow from CPU pressure alone.

## Related knowledge and primary sources

Algorithmic complexity, queue accumulation and retry amplification profiles refine common mechanisms. This profile retains the actor-to-defender cost asymmetry and admission boundary.

Reviewed 2026-10-09 against [MITRE CWE-405](https://cwe.mitre.org/data/definitions/405.html), [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html) and [RFC 4732](https://www.rfc-editor.org/rfc/rfc4732.html) denial-of-service and amplification considerations. The flow is hypothetical; service capacity and attacker cost require target evidence.
