---
id: vulnerability-lifetime-asynchronous-use-after-free
title: Asynchronous use after free in callbacks, queues, and I/O
kind: vulnerability
topics: [use-after-free, asynchronous, callbacks, work-queues, io]
platforms: [cross-platform]
architectures: [any]
---

# Asynchronous use after free in callbacks, queues, and I/O

## Definition and violated invariant

Asynchronous use after free occurs when queued or in-flight work retains a pointer or context after the owning object can be released. Submission, cancellation request, timeout, handle closure, and callback deregistration do not by themselves prove that every worker or completion has stopped accessing backing storage.

The owner must keep the object and all referenced buffers valid until the selected API's completion or quiescence condition, or transfer ownership to the asynchronous operation under an explicit contract.

## Conditions that establish the issue

Identify allocation generation, owners and borrowed aliases, submission, possible completion contexts, cancellation semantics, release, and later dereference. Prove an ordering in which release completes before a still-admitted callback, worker, future continuation, timer, or I/O operation uses the same generation.

Account for synchronization and reference acquisition. A callback holding an owning reference or a cancellation routine that waits for quiescence can refute the stale-use path.

## Evidence that is not sufficient

An asynchronous API, raw context pointer, close call, or callback after a cancellation request is not sufficient. The API may copy data, retain the object, serialize teardown, or guarantee no callback after successful deregistration.

An address reused in a trace is not enough; bind allocation and use to generations and confirm the later instruction consumes stale state.

## Investigation sequence

Build a timeline of admission, ownership changes, cancellation, completion, rundown, release, and callback entry. Follow normal, timeout, error, shutdown, and duplicate-completion paths. Identify the synchronization relation that should exclude new work and drain existing work.

In assembly, recover the callback function and context separately, then trace indirect loads through the context. Verify allocator reuse and object layout before interpreting a later virtual call or field access.

## Constructed example

```c
void start(struct job *job) { queue_work(run_job, job); }
void cancel(struct job *job) { request_cancel(job); free(job); }
void run_job(void *context) { ((struct job *)context)->callback(context); }
```

The free is unsafe only if `request_cancel` can return while `run_job` remains pending or active and no independent owner protects `job`. A synchronous cancel-and-drain contract would change the result. A binary pattern of loading a function pointer from the queued context after the free establishes the use only when the same allocation generation is proven.

## Primitive and impact limits

The direct primitive is a stale asynchronous read, write, or indirect call. Impact depends on reuse, controlled replacement contents, timing, and mitigations; many paths produce only a fault or corrupted result.

## Related knowledge and primary sources

`reference-windows-overlapped-io-lifetime-cancellation`, `reference-linux-io-uring-request-buffer-lifetime`, and `reference-native-ownership-release-dangling` provide API-specific contracts. This profile repeats the completion/quiescence requirement locally.

Reviewed 2026-10-09 against Microsoft [CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/fileio/cancelioex-func), Linux [`io_uring_prep_cancel`](https://man7.org/linux/man-pages/man3/io_uring_prep_cancel.3.html), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The code is constructed.
