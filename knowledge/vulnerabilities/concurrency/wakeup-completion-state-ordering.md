---
id: vulnerability-concurrency-wakeup-completion-state-ordering
title: Lost wakeup, duplicate completion, or state/result ordering mismatch
kind: vulnerability
topics: [concurrency, condition-variables, wakeups, completion, state-machine]
platforms: [cross-platform]
architectures: [any]
---

# Lost wakeup, duplicate completion, or state/result ordering mismatch

## Definition and violated invariant

A wakeup or completion vulnerability occurs when notification, terminal state and result publication are not bound by one coherent protocol. A waiter must test the predicate under the synchronization that protects it and tolerate permitted spurious wakes; a request must have one terminal owner, with result data visible before consumers act and object lifetime extending through every completion observer.

Notifications are usually events, not durable permission tokens. A notification can occur when no thread is waiting, and waking does not itself prove the application predicate is true.

## Conditions that establish the issue

Recover the predicate and its protecting synchronization, check and wait sequence, every predicate writer, notification calls, permitted spurious wakes, terminal states, result writes, completion delivery and cleanup. Prove a feasible interleaving loses required progress, consumes unpublished or wrong-generation result state, or executes a terminal effect more than once.

For duplicate completion, distinguish terminal events from progress notifications and establish that both paths refer to the same request generation. For state/result ordering, prove the observer can see completion without the writes that define the result under the actual memory model.

## Evidence that is not sufficient

A condition variable, notify without an obvious waiter, two completion functions, spurious wake, timeout, or repeated callback is not sufficient. The predicate may already be durable, a loop may recheck it, completions may be nonterminal, or a serialized state transition may select one owner.

A non-timeout wait return does not prove success, and a timeout does not prove the worker has stopped.

## Investigation sequence

Draw predicate changes, checks, atomic unlock-and-wait, notifications, reacquisition and rechecks on one timeline. Verify all waiters use the required lock identity and that state survives notifications. Then trace result initialization and the terminal transition to every consumer and cleanup path.

Include timeout, cancellation, shutdown and retry paths. Bind request identity and generation so an old completion cannot satisfy a new wait on a reused object or slot.

## Constructed lost-wakeup example

```c++
if (!ready.load()) {
    std::unique_lock<std::mutex> lock(mutex);
    ready_condition.wait(lock);       // no predicate recheck under the mutex
}
```

Constructed schedule: the consumer loads `false`; the producer acquires the mutex, sets `ready=true`, releases the mutex and calls `notify_one` while no waiter is blocked; the consumer then acquires the mutex and waits. Because it does not recheck the predicate, the earlier notification need not be retained for it. The finding requires the actual predicate and notification protocol and a security-relevant indefinite or incorrect recovery path.

## Primitive and impact limits

The direct result can be indefinite wait, duplicate response or cleanup, consumption of incomplete result data, stale-generation completion, or skipped required work. Consequences include denial of service, resource leakage, wrong authorization state or memory-lifetime violations.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy` and `reference-concurrency-cancellation-completion-shutdown` cover predicate waits and terminal ownership. This profile repeats predicate, notification, result, generation and cleanup binding locally.

Reviewed 2026-10-09 against the C++ [condition-variable contract](https://eel.is/c++draft/thread.condition.condvar), [atomic ordering rules](https://eel.is/c++draft/atomics.order), and [MITRE CWE-833](https://cwe.mitre.org/data/definitions/833.html). The source and schedule are constructed.
