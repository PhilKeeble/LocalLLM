---
id: vulnerability-kernel-execution-context-lock-misuse
title: Kernel lock or API used in an incompatible execution context
kind: vulnerability
topics: [kernel, locking, interrupts, softirq, dpc, atomic-context, irql]
platforms: [cross-platform, linux, windows, android, freebsd]
architectures: [any]
---

# Kernel lock or API used in an incompatible execution context

## Definition and violated invariant

This vulnerability occurs when kernel code sleeps, faults, allocates, blocks or uses a lock/API in a process, interrupt, softirq, DPC or atomic context that does not permit that operation, or when the chosen exclusion primitive fails to cover a competing context. The invariant is that each operation must obey the current execution context and the lock must exclude every actor that accesses the protected state.

Context names and lock semantics are platform- and configuration-specific. Linux `spinlock_t` behavior can differ under PREEMPT_RT, while Windows IRQL constrains pageable access and waiting through its own rules.

## Conditions that establish the issue

Recover every entry context, current interrupt/preemption/IRQL state, held locks, called operation's blocking and faulting contract, allocation flags and competing access contexts. Prove a reachable path violates an API context requirement or allows an interrupt/CPU/device participant to race despite the apparent lock.

Include callbacks whose context is chosen by the framework and lock variants that disable local interrupts or bottom halves only on one CPU.

## Evidence that is not sufficient

A spin lock, interrupt handler, DPC, allocation or pageable symbol is not sufficient. The path may run at a permitted level, use nonblocking flags, pin code/data or rely on a lock variant covering the relevant context. Function names do not establish actual inlining, section placement or call context.

Do not translate one operating system's context levels directly into another's terminology.

## Investigation sequence

Propagate context state along every call edge: can sleep, interrupt enabled, preemption state, IRQL, held locks and CPU affinity. For each callee, compare documented requirements and possible page faults or waits. Map all accesses to the protected object and identify whether they occur in process, deferred and hard-interrupt contexts.

At binary level, recover interrupt masking, IRQL changes, lock primitives and allocation or wait calls. Check every exit restores prior context. A missing restoration can affect later unrelated operations even if the protected update completes.

## Constructed flow

A hypothetical interrupt handler takes a raw spin lock and calls a helper that can wait for pageable storage. If the platform forbids sleeping or faults in that context, the call can deadlock or fault. The same helper called from process context may be valid, so classification requires the actual entry and configuration.

## Primitive and impact limits

Direct effects include deadlock, invalid wait, page fault in an unsupported context, race, interrupt latency or corrupted context state. Memory corruption or elevation requires a separate unsafe access or attacker-controlled privileged effect.

## Related knowledge and primary sources

Linux and Windows kernel references provide their distinct lock, IRQL and pool contracts. This profile keeps context propagation and exclusion scope together.

Reviewed 2026-10-09 against Linux kernel [lock types and PREEMPT_RT distinctions](https://docs.kernel.org/locking/locktypes.html), Linux [hacking context guidance](https://docs.kernel.org/kernel-hacking/hacking.html) and Microsoft [Managing hardware priorities](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities). The flow is hypothetical.
