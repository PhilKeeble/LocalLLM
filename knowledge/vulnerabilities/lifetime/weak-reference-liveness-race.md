---
id: vulnerability-lifetime-weak-reference-liveness-race
title: Weak or unowned reference liveness-check race
kind: vulnerability
topics: [lifetime, weak-reference, race-condition, ownership, use-after-free]
platforms: [cross-platform]
architectures: [any]
---

# Weak or unowned reference liveness-check race

## Definition and violated invariant

A weak-reference race occurs when code observes that an object appears live, then uses an unowned reference after another execution context can perform final release between the check and ownership acquisition or dereference. A liveness observation and later use must be covered by one atomic promotion to strong ownership or by synchronization that excludes destruction.

Weak, unowned, unsafe, and raw references have runtime-specific behavior. Some become null, some trap, and some remain dangling; recover the selected contract.

## Conditions that establish the issue

Identify weak-reference creation, liveness check, strong-acquisition operation, final-release path, synchronization, and later use. Prove a feasible interleaving in which destruction occurs after the check but before a protected owner covers the use.

For C++ `weak_ptr`, `lock()` atomically attempts to acquire shared ownership and can return empty. A separate `expired()` check does not guarantee a later `lock()` succeeds.

## Evidence that is not sufficient

A weak reference, liveness check, or concurrent release is not sufficient. The code may retain another strong owner, hold the required lock, validate the promotion result, or use a runtime operation that atomically loads a strong reference.

A null result handled before dereference is a normal expired-object path, not a UAF.

## Investigation sequence

Draw the check, promotion, final decrement, destruction, and use as separate events. Identify locks, epochs, reference acquisitions, or runtime barriers that order them. Follow every promotion failure path and confirm the later dereference uses the promoted owner rather than a stale raw alias.

In assembly, distinguish a count or flag read from the atomic helper that acquires ownership. A nonzero count observed earlier does not prove the count storage still belongs to the same generation.

## Constructed C++ example

```cpp
void run_if_live(std::weak_ptr<worker> weak)
{
    if (!weak.expired()) {
        std::shared_ptr<worker> strong = weak.lock();
        strong->run();
    }
}
```

Another thread can release the last strong owner after `expired()` returns false but before `lock()`, causing `lock()` to return an empty `shared_ptr`; dereferencing it is invalid. Testing `strong` before use or using `if (auto strong = weak.lock())` would refute this path.

## Primitive and impact limits

The direct result may be a null dereference, stale unowned access, runtime trap, or use of a replacement object, depending on the weak-reference implementation. Stronger memory or control primitives require the concrete runtime behavior and reuse evidence.

## Related knowledge and primary sources

`reference-concurrency-refcounts-reuse` covers acquisition-before-reclamation and object generations. This profile repeats atomic promotion and result checking locally.

Reviewed 2026-10-09 against C++ [`weak_ptr` observers](https://eel.is/c++draft/util.smartptr.weak.obs), C++ [`shared_ptr` observers](https://eel.is/c++draft/util.smartptr.shared.obs), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The example is constructed.
