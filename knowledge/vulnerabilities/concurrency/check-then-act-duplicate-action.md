---
id: vulnerability-concurrency-check-then-act-duplicate-action
title: Check-then-act race and non-atomic state transition
kind: vulnerability
topics: [concurrency, check-then-act, state-machine, atomicity, duplicate-action]
platforms: [cross-platform]
architectures: [any]
---

# Check-then-act race and non-atomic state transition

## Definition and violated invariant

A check-then-act vulnerability occurs when multiple actors can observe a state that permits an operation and perform the operation before any one actor commits the mutually exclusive state transition. The permission check, ownership claim, state update, and one-time effect must be bound as one logical transition.

Every individual access can be atomic or locked without making the compound operation indivisible. This is commonly a logical race rather than a source-language data race.

## Conditions that establish the issue

Recover the state-machine invariant, every admission check, commit point, side effect, rollback and competing path. Prove two feasible operations can both pass the check before either excludes the other and that both reach an effect intended to occur once, such as refund, authorization use, token redemption, object creation, quota reservation, or cleanup.

If a compare-and-exchange or database transaction exists, verify that its success selects the effect owner and that losing paths do not perform the effect before or after failure. A state transition after the external effect may leave an unavoidable duplicate window.

## Evidence that is not sufficient

A load followed by a store, repeated requests, an atomic Boolean, or two completion handlers is not sufficient. Requests may serialize elsewhere, the operation may be idempotent, a unique downstream key may reject duplicates, or only one path may be reachable for the same object generation.

A successful atomic store proves only that the store was indivisible; it does not prove the earlier decision remained exclusive.

## Investigation sequence

Draw the allowed states and name the exact event that transfers ownership of the one-time action. Trace all paths from initial check through commit and external effects. Then construct a two-actor timeline around the smallest interval in which both can still win.

Bind both operations to the same logical object and generation. Follow retry, timeout and error paths because a failed response can trigger another attempt while the first effect later commits.

## Constructed duplicate-refund example

```c
if (!request->refunded.load()) {
    issue_refund(request->payment_id);
    request->refunded.store(true);
}
```

Constructed schedule: threads A and B each load `false`; A issues the refund; B issues the same refund; both then store `true`. The atomic field prevents tearing and a data race on that field, but it does not reserve the action. A finding requires that both threads can process the same request generation and that the refund service does not independently enforce one-time semantics.

## Primitive and impact limits

The direct primitive is duplicate, omitted, or conflicting execution of a state-dependent action. Consequences can include duplicate payment, repeated privilege grant, quota bypass, double cleanup, or inconsistent persistent state; impact depends on idempotency and downstream enforcement.

## Related knowledge and primary sources

`reference-concurrency-memory-order-atomic-invariants` and `reference-concurrency-cancellation-completion-shutdown` cover compound transitions and duplicate terminal paths. This profile repeats the check, commit, effect, and object-generation proof locally.

Reviewed 2026-10-09 against the C++ [atomic operation contract](https://eel.is/c++draft/atomics.types.operations), [memory-order rules](https://eel.is/c++draft/atomics.order), and [MITRE CWE-362](https://cwe.mitre.org/data/definitions/362.html). The source and schedule are constructed.
