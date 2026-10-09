---
id: vulnerability-authorization-complete-mediation-policy-change-gap
title: Complete-mediation failure after permissions, ownership, or policy changes
kind: vulnerability
topics: [authorization, complete-mediation, revocation, caches, policy-change, object-lifetime]
platforms: [cross-platform]
architectures: [any]
---

# Complete-mediation failure after permissions, ownership, or policy changes

## Definition and violated invariant

A complete-mediation vulnerability occurs when a security-sensitive operation reuses an authorization decision after a change in subject, object generation, ownership, operation, policy, revocation state or context that the system's contract requires to be checked again. The flaw is not caching itself; it is reuse outside the cache key and validity interval promised by policy.

Some capabilities and opened handles intentionally preserve authority after a later ACL change. Their continued use is not a bypass unless the relevant platform or application contract requires revocation or revalidation.

## Conditions that establish the issue

Recover the original authorization tuple and decision, cache or retained capability, validity and invalidation rules, subject and session generation, object identity and generation, ownership or permission mutation, policy version and propagation, later operation, effective security context and completed effect. Prove the changed state should deny the later tuple but stale authority remains accepted.

For distributed policy, include replication and consistency guarantees. A transient difference is a vulnerability only when it violates the stated authorization contract and exposes a forbidden operation.

## Evidence that is not sufficient

A cached `allowed` flag, policy update, ACL change, open handle, long session, revoked role, stale replica or missing repeated check is not sufficient. The grant may be deliberately durable, the object may be unchanged, invalidation may occur before use or the policy may permit in-flight operations.

Current policy does not prove the policy at an earlier decision, and current denial does not retroactively invalidate every acquired capability.

## Investigation sequence

Write the original and later authorization tuples side by side and identify every changed dimension. Trace cache keys, version fields, subscriptions, revocation messages, session and object generations, retries and failover. Establish the policy's required consistency and commit boundary, then follow the stale decision into the exact protected effect.

At binary level, follow authorization-result storage and all invalidation paths. Distinguish a cached object handle with durable rights from an application Boolean that is expected to reflect live policy.

## Hypothetical stale-grant example

```text
session.can_admin = policy.check(user, ADMIN)
later: administrator revokes user's ADMIN role
later: if session.can_admin: delete_tenant(request.tenant_id)
```

The example is vulnerable only if revocation policy requires existing sessions to lose the role before the later operation and the stale Boolean remains accepted. A contract that makes grants valid until session expiry would change the finding, though that policy may warrant separate review.

## Primitive and impact limits

The direct primitive is a protected operation accepted under stale authority. Impact is bounded by the cached grant and changed policy and can be horizontal or vertical. Broader escalation requires a resulting policy, credential or execution effect.

## Related knowledge and primary sources

`reference-logic-authorization-object-binding`, state-transition, distributed-state and capability references define decision identity and lifetime. The incorrect-authorization profile covers wrong tuples without a policy-change emphasis.

Reviewed 2026-10-09 against Saltzer and Schroeder's [The Protection of Information in Computer Systems](https://doi.org/10.1109/PROC.1975.9939) for the complete-mediation principle and NIST [SP 800-53 Rev. 5 AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for authorization enforcement. The example is hypothetical; revocation timing must come from the target's policy.
