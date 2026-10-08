---
id: reference-rtos-task-queue-ownership
title: RTOS task scheduling, interrupt handoffs, queues and resource ownership
kind: reference
topics: [rtos, tasks, scheduling, interrupts, queues, mutexes, allocation, lifetime]
platforms: [embedded]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---
# RTOS asynchronous execution evidence

## A ready task is not evidence of completed work

FreeRTOS scheduling selects eligible tasks according to priority and configured
policy. A high-priority runnable task can starve lower-priority tasks; SMP permits
one running task per core, unlike a single-core configuration. [1]

Recover task entry, stack, priority, wake condition and selected scheduling mode.
Task creation, readiness or a wake notification does not prove the task consumed
an input. Distinguish blocked waiting from actual execution and retain deadline/
timeout units. These FreeRTOS facts are not a universal scheduler for every RTOS;
private task structures and the chosen port must be identified separately.

## Queueing a pointer does not copy its referenced buffer

FreeRTOS queues copy each item; that item may itself be a pointer. [2] A pointer
item therefore preserves an address value, not automatically the pointed-to
bytes or their lifetime.

Recover item size/type, producer ownership, queue result, consumer and cleanup.
Distinguish inline data from pointer/handle handoff and track whether storage
remains valid and stable until consumption. A full-queue failure does not transfer
ownership merely because a send was attempted. Other RTOS queue APIs may have
different copy/ownership contracts; do not infer them from this example.

## Interrupt APIs and mutex ownership are separate contracts

FreeRTOS interrupt handlers must use the permitted FromISR interfaces, rather
than ordinary task APIs. Its mutexes use task priority inheritance and must not
be used from interrupts. [2][3]

Recover interrupt priority/port restrictions, handoff result and task-side waits
for the target configuration. A semaphore notification is not automatically a
mutex protecting all shared fields. Priority inheritance addresses scheduling
priority, not buffer lifetime or every deadlock. Do not transfer the FreeRTOS
API naming or priority limits to another kernel.

## RTOS object creation does not imply one heap or freeing policy

FreeRTOS objects can use application-provided storage or dynamic allocation.
Its documented allocation implementations differ: heap_1 does not free, while
other implementations support freeing and may coalesce or span regions. [4]

Identify the actual allocator, object/stack storage, failure handling and cleanup
owner. A missing free is not necessarily a leak in a permanent static or no-free
allocation scheme. Conversely, keeping a queue alive does not retain arbitrary
pointed-to storage. Recover shutdown and cancellation users before judging
reclamation. Workflow: playbook-specialist-firmware-evidence.

## Sources and scope

Reviewed 2026-10-08. Rolling FreeRTOS documentation; kernel/port configuration
must be recovered for the target. No tick rate, private layout or heap default.

1. [Task scheduling](https://2fwww.freertos.org/Documentation/02-Kernel/02-Kernel-features/01-Tasks-and-co-routines/04-Task-scheduling): single-core and SMP eligibility/priority.
2. [Queues](https://www.freertos.org/Documentation/02-Kernel/02-Kernel-features/02-Queues-mutexes-and-semaphores/01-Queues): item copying and interrupt API distinction.
3. [Mutexes](https://freertos.org/Real-time-embedded-RTOS-mutexes.html): priority inheritance and interrupt exclusion.
4. [Memory management](https://2fwww.freertos.org/Documentation/02-Kernel/02-Kernel-features/09-Memory-management/01-Memory-management): static/dynamic storage and allocator variants.
