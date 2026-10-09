---
id: vulnerability-concurrency-asynchronous-context-unsafe-shared-state
title: Signal-, interrupt-, or exception-unsafe shared-state access
kind: vulnerability
topics: [concurrency, signals, interrupts, exceptions, reentrancy, drivers]
platforms: [cross-platform]
architectures: [any]
---

# Signal-, interrupt-, or exception-unsafe shared-state access

## Definition and violated invariant

An asynchronous-context vulnerability occurs when a signal handler, interrupt routine, deferred interrupt, exception handler, APC-like callback, or comparable context interrupts code and accesses state or calls operations that are not valid or synchronized for that context. Shared state must obey the platform's interruption, masking, atomicity, reentrancy, execution-level and lifetime rules.

These mechanisms are not interchangeable. POSIX signal safety, Windows kernel IRQL, hardware interrupt masking, language exceptions and user-mode asynchronous callbacks have distinct contracts that must be identified before analysis.

## Conditions that establish the issue

Recover registration, delivery context and thread or CPU eligibility; masking or execution level; interrupted operations; shared byte ranges; callable APIs; lock and allocation behavior; saved error state; nesting; and return or unwind path. Prove the asynchronous entry can occur during an incompatible state and that it corrupts data, deadlocks, accesses invalid or pageable memory, violates a one-time transition, or causes another security-relevant effect.

For interrupts, include synchronization with ordinary paths and other CPUs, device acknowledgment and memory ordering. For signals, distinguish async-signal-safe library calls from the handler's own shared-state correctness.

## Evidence that is not sufficient

A signal handler, interrupt service routine, exception table, global variable, volatile qualifier, or logging call is not sufficient. Delivery may be masked, the relevant routine may be safe in that context, state may use the required atomic protocol, or the path may be unreachable at the stated execution level.

Ordinary thread safety does not establish signal or interrupt safety because the asynchronous entry can interrupt the same thread or CPU while it owns internal state.

## Investigation sequence

Identify the exact asynchronous mechanism and derive its permitted operations from the target platform. Build an interrupted timeline showing the outer operation's partial state, handler entry, nested accesses and return or nonlocal exit. Include locks already held and resources whose lifetime changes in either path.

At binary level, recover actual masking, execution-level changes, atomic instructions and barrier scope. Do not infer safety from source `volatile`, a disabled local interrupt when another CPU participates, or a handler that appeared not to fire in one trace.

## Constructed POSIX signal example

```c
static struct record *current;

void handler(int signal)
{
    log_record(current);        /* ordinary logger and shared object access */
}

void update(struct record *record)
{
    current = record;
    mutate_record(record);
    current = NULL;
}
```

If the signal is delivered to the updating thread while `mutate_record` or its logger has partially updated shared or internal library state, `handler` can reenter incompatible operations. The finding requires the actual handler registration and mask, a delivery window, the target implementation's signal-safety contract, and a concrete harmful access; the fragment alone does not prove one.

## Primitive and impact limits

The direct result can be shared-state corruption, deadlock, invalid memory access, unsafe nonlocal exit, or kernel fault at an invalid execution level. Impact depends on reachable asynchronous delivery and the interrupted resource or security operation.

## Related knowledge and primary sources

`reference-concurrency-locks-waits-reentrancy`, `reference-linux-signals-fork-exec-state`, and platform interrupt references define context-specific rules. This profile repeats the delivery, partial-state, allowed-operation, and effect proof locally.

Reviewed 2026-10-09 against Linux/POSIX [signal-safety](https://man7.org/linux/man-pages/man7/signal-safety.7.html), Microsoft [hardware-priority and IRQL guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities), and the C++ [signal-handler restrictions](https://eel.is/c++draft/support.signal). The source is constructed and is scoped to a POSIX-style signal mechanism.
