---
id: vulnerability-authorization-incorrect-authorization-tuple
title: Authorization checks the wrong actor, action, object, context, or policy state
kind: vulnerability
topics: [authorization, access-control, object-binding, stale-policy, confused-identity]
platforms: [cross-platform]
architectures: [any]
---

# Authorization checks the wrong actor, action, object, context, or policy state

## Definition and violated invariant

An incorrect-authorization vulnerability occurs when a check exists but decides a different authorization tuple from the operation that executes. The mismatch can involve subject, action, resolved object, operands, tenant or namespace, delegation context, object generation, policy snapshot or time. A correct decision for one tuple cannot authorize a materially changed tuple.

This differs from a wholly missing check: the decisive evidence is the relation between checked and consumed identities or state, not the mere presence of policy code.

## Conditions that establish the issue

Recover the subject and security context used by the check, requested and checked action, checked object identity and generation, operands and tenant, policy/version/time, later transformations or substitutions, final effective context and executed object. Prove the checked tuple is permitted while the consumed tuple is forbidden for the initiating actor.

For stale decisions, establish the policy or ownership change and the contract requiring revalidation. Some acquired capabilities intentionally survive later policy changes.

## Evidence that is not sufficient

A cached Boolean, separate lookup, object ID conversion, changed policy, asynchronous work, impersonation, reused slot or check far from use is not sufficient. The cache may bind every required dimension, the object may be stable, the policy may grant durable authority, or later code may revalidate the consumed object.

Matching names or numeric IDs do not establish matching object generations, while different handles can intentionally refer to one authorized object.

## Investigation sequence

Write the checked and consumed authorization tuples side by side. Trace trusted identity, operation, object resolution, namespace, policy generation and lifetime through normalization, queues, caching and callbacks. Mark every field that changes between decision and effect, then determine whether the applicable policy permits that change. Preserve live object identity rather than only display names.

At binary level, follow data dependencies from policy inputs and result into the sensitive call. Recover structure offsets and generations carefully; similar fields can represent requester, owner, service account or audit identity.

## Hypothetical wrong-object example

```text
if policy.may_read(caller, request.source_id):
    privileged_copy(source=request.source_id, destination=request.destination_id)
```

Read permission on the source does not authorize writing the independently selected destination. The example is vulnerable only if the caller controls a forbidden destination, the copy uses greater authority, and no destination-specific policy or capability check occurs later.

## Primitive and impact limits

The direct primitive is an operation authorized against the wrong tuple. Impact is the authority difference between the checked and consumed subject, object or action, classified from the actual boundary. Code execution or escalation requires the mismatched operation to alter or invoke a resource that yields that additional authority.

## Related knowledge and primary sources

`reference-logic-authorization-object-binding`, object-identity, concurrency and platform-authority references govern tuple and lifetime details. The complete-mediation profile covers repeated decisions after change.

Reviewed 2026-10-09 against NIST [SP 800-53 Rev. 5 AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for enforcing approved authorizations and [CWE-863](https://cwe.mitre.org/data/definitions/863.html) for incorrect authorization. The example is hypothetical and requires the target's actual policy.
