---
id: vulnerability-concurrency-teardown-rundown-admission-race
title: Teardown or rundown race with new or outstanding work
kind: vulnerability
topics: [concurrency, teardown, rundown, timers, callbacks, dma, workers]
platforms: [cross-platform]
architectures: [any]
---

# Teardown or rundown race with new or outstanding work

## Definition and violated invariant

A teardown/rundown vulnerability occurs when code releases an owner, resource, mapping or executable component while new work can still be admitted or previously accepted work can still access it. Teardown must close admission, account for every existing user, establish the required quiescence, and only then reclaim each dependent resource.

Closing a handle, setting a stopping flag, emptying a queue, requesting cancellation, or canceling a timer is not universally a drain. The exact callback, worker, I/O and DMA contracts determine when last use has ended.

## Conditions that establish the issue

Identify the owner and every dependent resource, all admission paths, references or rundown acquisitions, queued and in-flight work, timers, callbacks, device/DMA activity, cancellation semantics, drain or join, and final release. Prove either new work can pass admission after shutdown begins or accounted work can outlive the wait and reach a reclaimed resource.

Include work spawned by callbacks, retry paths and completion handlers. A live request reference may not retain its nested buffer, callback context, code module or hardware mapping.

## Evidence that is not sufficient

A stop flag, callback deregistration, timer cancellation, queue-empty check, close call, pending request, or late log line is not sufficient. Another mechanism may retain the resource and provide a documented drain, or the late work may no longer access released state.

A reference count reaches meaningful quiescence only when every relevant user participates and acquisition fails after rundown begins.

## Investigation sequence

Construct a lifecycle table covering admission, ownership acquisition, queueing, execution, completion, callback return, cancellation and release. Locate the transition that prevents new acquisitions and verify every path honors its failure. Match every accepted user with the event that proves its final use ended.

For timers, DMA and device work, distinguish dequeuing or cancellation from an already-running callback or transaction. Inspect wait dependencies so teardown does not hold a resource required for workers to drain.

## Constructed timer teardown example

```c
context->stopping = true;
cancel_timer(&context->timer);
free(context);
```

Constructed schedule: the timer expires and queues its callback; teardown sets `stopping`, cancellation no longer removes the already-queued callback, and `free` runs before the callback dereferences `context`. The finding requires that the selected timer API lacks a drain guarantee in this state and that no separate rundown reference covers the callback. Under Windows kernel `KeCancelTimer`, an already-running DPC runs to completion and resources it uses must remain valid.

## Primitive and impact limits

The direct result can be use-after-free, access to unmapped hardware or DMA memory, execution after module unload, duplicate cleanup, stale completion, or denial of service. Impact depends on what the late or newly admitted work controls and consumes.

## Related knowledge and primary sources

`reference-concurrency-cancellation-completion-shutdown`, `reference-windows-driver-pnp-power-rundown`, and callback-lifetime references cover admission and drain contracts. This profile repeats the close-admission, account-users, quiesce, then-release proof locally.

Reviewed 2026-10-09 against Microsoft [remove-lock guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-remove-locks), Microsoft [KeCancelTimer](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kecanceltimer), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The source and schedule are constructed.
