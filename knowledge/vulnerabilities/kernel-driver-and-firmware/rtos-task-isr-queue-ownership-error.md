---
id: vulnerability-kernel-rtos-task-isr-queue-ownership-error
title: RTOS task, ISR, queue-pointer or allocator-policy error
kind: vulnerability
topics: [rtos, firmware, interrupts, queues, pointer-lifetime, allocator]
platforms: [embedded]
architectures: [any]
---

# RTOS task, ISR, queue-pointer or allocator-policy error

## Definition and violated invariant

This vulnerability occurs when RTOS code uses a task-only operation from an interrupt, violates interrupt-priority restrictions, queues a pointer whose storage does not outlive consumption, mishandles queue failure, or assumes allocation/free behavior different from the configured heap. The invariant is that API context, ownership transfer and resource lifetime must match the selected RTOS and port configuration.

FreeRTOS queue sends copy the queue item; if the item is a pointer, only the address value is copied. Other RTOS APIs can have different semantics and require their own contracts.

## Conditions that establish the issue

Identify task or ISR entry, interrupt priority and port rules, exact API variant, queue item size/type, send result, producer storage, consumer timing, allocator implementation and cleanup. Prove a reachable path blocks illegally, consumes stale pointer data, treats failed enqueue as ownership transfer, or exhausts/incorrectly frees configured storage.

Include scheduler mode, multicore execution and priority inheritance where they affect concurrency, but do not treat them as lifetime guarantees.

## Evidence that is not sufficient

A queue API, pointer item, `FromISR`-named function, stack buffer or missing free is not sufficient. The consumer may run before scope ends under a proven synchronous contract, storage may be static, the send may copy inline data, or the allocator may intentionally never free permanent objects.

A high-priority task being ready does not prove it executed or consumed the item.

## Investigation sequence

Recover the concrete RTOS build and port, scheduler policy, interrupt rules and allocator choice. Trace queue creation to establish item size, then each send/receive result and ownership. For pointer items, follow the pointee independently through producer scope, mutation and consumer completion.

At binary level, distinguish task and ISR API entry points, context-switch requests and queue-copy widths. Inspect full-queue and allocation-failure paths. Map object storage to static region, RTOS heap, caller stack or another owner.

## Constructed timeline

An ISR places the address of a local temporary structure into a pointer-sized queue item and returns. A task later dequeues the address after the interrupt stack storage has been reused. The queue retained only the pointer, so the task accesses stale storage.

The finding requires that the temporary is truly stack-local under the target interrupt model and no consumer completes before return. Queuing the structure bytes inline with a matching item size would be different.

## Primitive and impact limits

Direct effects include stale access, race, invalid block in interrupt context, resource leak or denial of service. Memory corruption and privilege impact depend on the pointee, allocator and flat-address-space authority.

## Related knowledge and primary sources

`reference-rtos-task-queue-ownership` provides scheduling and allocator distinctions. This profile repeats context and pointer ownership locally.

Reviewed 2026-10-09 against FreeRTOS [queue behavior](https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues), [interrupt management](https://www.freertos.org/Documentation/02-Kernel/03-Supported-devices/02-Customization) and [memory management](https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/09-Memory-management/01-Memory-management). The timeline is constructed and FreeRTOS-specific where named.
