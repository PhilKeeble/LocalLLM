---
id: vulnerability-authorization-cross-tenant-state-reuse
title: Cross-tenant or cross-user object reuse without identity and state reset
kind: vulnerability
topics: [authorization, tenants, object-reuse, pooling, sessions, state-reset]
platforms: [cross-platform]
architectures: [any]
---

# Cross-tenant or cross-user object reuse without identity and state reset

## Definition and violated invariant

A cross-context reuse vulnerability occurs when a pooled, recycled or reassigned object retains data, authorization, identity, callbacks, capabilities or protocol state from a previous user or tenant and exposes or applies it in the next context. Reuse is safe only when every security-relevant field is reset or rebound before the new owner can observe or exercise it.

This profile covers logical object and authority reuse. Reading stale freed memory has a memory-lifetime or disclosure root cause even if the visible impact is also cross-tenant.

## Conditions that establish the issue

Recover the original and new principals or tenants, pooled object identity and generation, release and reassignment transitions, retained data and authority fields, reset coverage and ordering, concurrent references, callbacks or queued work, new-context operation, effective security context and final read or effect. Prove prior-context state survives and is consumed by a different unauthorized context.

Include connection pools, session slots, worker objects, caches, shared buffers, virtual devices and resource identifiers. Numeric slot reuse alone does not establish retained state.

## Evidence that is not sufficient

An object pool, reused identifier, uncleared buffer capacity, persistent connection, shared cache, allocator reuse or stale-looking field is not sufficient. Initialization may overwrite the consumed extent, cache keys may include tenant identity, the object may be intentionally shared, or generation checks may reject old work.

Prove which bytes or authority fields survive, who receives them and what consumer uses them.

## Investigation sequence

Model the state machine from ownership by A through release, reset, reassignment to B and first B-visible action. Inventory data, grants, callbacks, handles, protocol authentication and queued work at each transition. Trace generation and tenant keys into every lookup and completion. Compare reset writes with the exact fields later read.

At binary level, follow allocator or pool free lists, constructor/reset routines and structure offsets. A zeroing call must cover the live representation and occur before publication to the new context.

## Hypothetical pooled-session example

```text
slot = session_pool.acquire()
slot.user = new_user
// slot.cached_permissions and slot.pending_results are not reset
publish(slot)
```

The example is vulnerable only if retained permissions or results belong to a different prior principal and the new user can consume them before rebinding or validation. Reusing allocation storage after complete initialization is safe.

## Primitive and impact limits

The direct primitive is cross-user or cross-tenant disclosure, action or capability reuse. Classify the exact retained state and whether the effect is horizontal access or crosses a higher privilege boundary. Code execution requires retained callbacks, executable content or another control path.

## Related knowledge and primary sources

Authorization-object binding, object-generation, buffer-initialization and cancellation references cover the independent relations joined by reuse. Memory disclosure profiles apply when stale bytes rather than logical state are exposed.

Reviewed 2026-10-09 against NIST [SP 800-53 Rev. 5 SC-4](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for preventing unauthorized information transfer through shared resources and AC-3 for authorization enforcement. The example is hypothetical and includes authority state beyond SC-4's information focus.
