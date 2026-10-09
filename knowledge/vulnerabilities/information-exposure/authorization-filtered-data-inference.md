---
id: vulnerability-information-authorization-filtered-data-inference
title: Protected data inferred through metadata, indexes or aggregates
kind: vulnerability
topics: [information-disclosure, authorization, metadata, inference, side-channel]
platforms: [cross-platform]
architectures: [any]
---

# Protected data inferred through metadata, indexes or aggregates

## Definition and violated invariant

This vulnerability occurs when an interface hides protected records or fields but exposes metadata, counts, ordering, search hits, cache state or aggregate results from which an unauthorized actor can infer protected state. The violated invariant is that authorization must cover derived observations whose information content reveals the protected object, not only the primary record body.

This profile covers application and data-layer inference. Cryptographic validity or padding oracles belong to the adaptive-oracle profile, while CPU cache and transient-execution channels require a microarchitectural observer model.

## Conditions that establish the issue

Define the hidden fact, unauthorized observer, permitted query or observation, returned metadata and inference procedure. Show that feasible changes to attacker-controlled queries produce a repeatable distinction correlated with the protected state and that ordinary public state does not explain it. For aggregates, establish that filtering, grouping or differencing can isolate the target population.

The observer may have legitimate access to the interface while lacking access to particular records. This is often horizontal or cross-tenant disclosure rather than vertical privilege elevation.

## Evidence that is not sufficient

A count, index, search endpoint, cache, sort order or different response is not sufficient. The distinction may derive only from public records, noise, rate limiting, eventual consistency or unrelated workload. A theoretically different internal path is not exposure unless the attacker can observe and interpret it under the supported query model.

Do not claim recovery of record contents when the evidence supports only existence, membership, size or change. State the exact inferred predicate.

## Investigation sequence

Map the authorization filter and every operation performed before and after it. Trace protected records into counts, facets, pagination totals, suggestions, ordering keys, deduplication, caches and error behavior. Define paired or adaptive queries that differ in one controlled condition and identify confounders such as concurrent writes and cached responses.

At binary level, compare control and data flow from record selection through authorization to aggregation and serialization. A protected row contributing to a counter before filtering is a stronger lead than a response-size difference alone. Recover tenant and object binding at both the query and cache-key layers.

## Constructed query example

A hypothetical search API suppresses unauthorized records from `items` but computes `total_matches` before applying the caller's tenant filter. By submitting a rare exact identifier and observing `total_matches` change from zero to one, a caller may infer that another tenant holds that identifier.

This supports only an existence oracle unless further fields can be inferred. It is refuted if the total is computed after authorization, is deliberately public, or noise and concurrency prevent a reliable distinction.

## Primitive and impact limits

State the inferred predicate, error rate, number of observations, query budget, rate limits and affected security boundary. Repeated membership tests may reveal a larger dataset, but extrapolation requires a feasible enumeration space.

The direct effect is information disclosure. Account compromise, authorization bypass or code execution requires a separate capability; knowing that an object exists does not grant access to it.

## Related knowledge and primary sources

Authorization profiles define caller, action and object binding. This profile adds derived-data flow and observer inference while retaining the protected fact and limits locally.

Reviewed 2026-10-09 against [MITRE CWE-202](https://cwe.mitre.org/data/definitions/202.html) for exposure through data queries, [MITRE CWE-203](https://cwe.mitre.org/data/definitions/203.html) for observable discrepancies and [NIST SP 800-53 Revision 5.1 control AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for enforcement of approved authorizations. The concrete inference model and authorization policy remain application-specific.
