---
id: vulnerability-resource-descriptor-handle-thread-process-exhaustion
title: Descriptor, handle, socket, thread, task or process exhaustion
kind: vulnerability
topics: [resource-exhaustion, file-descriptor, handle, thread, process, socket]
platforms: [cross-platform]
architectures: [any]
---

# Descriptor, handle, socket, thread, task or process exhaustion

## Definition and violated invariant

This vulnerability lets an actor consume a finite count of kernel or runtime objects such as file descriptors, handles, sockets, threads, tasks or processes until required work cannot acquire one. The violated invariant is that object creation and retention must be bounded and charged across the scope sharing the exhausted limit.

This differs from a memory leak because the first binding limit can be an object table, process count, port range, connection pool or scheduler resource even when memory remains.

## Conditions that establish the issue

Identify the object type, allocation path, actor-controlled repetition or concurrency, lifetime and close/join/reap behavior, per-process and system-wide limits, and failure consequence. Prove the attacker can hold or leak enough objects within its reachability and rate constraints to deny a security-relevant operation.

Account for accepted connections waiting on input, child processes awaiting reaping, threads blocked indefinitely and duplicated or inherited handles. Closing one wrapper may not release the underlying object while another reference remains.

## Evidence that is not sufficient

A socket accept, thread creation, process spawn or missing close on one path is not sufficient. Admission caps, idle timeouts, quotas, process isolation, pooling or later cleanup may bound usage. A high numeric system limit is not automatically exploitable if the actor cannot sustain enough live objects.

An allocation failure is an effect; identify the uncontrolled creation or missing release that consumes the table.

## Investigation sequence

Trace object creation, every duplicate or inheritance, ownership transfer, terminal event and release. Build counts per request, connection, principal and process, then compare with the actual limiting scope. Follow errors, half-open protocols, cancellation, timeouts and child termination.

At binary level, map create/open/accept/spawn calls to cleanup blocks and long-lived collections. Recover failure handling: exhaustion can cause clean rejection, crash, busy retry or a security-sensitive fallback. Record which authorized function loses access first.

## Constructed example

A hypothetical server accepts connections and assigns one thread per connection, while unauthenticated clients may keep the connection idle indefinitely. If no connection, thread or idle-time budget applies, a client set can consume the process's thread or socket limit.

The finding is refuted by an effective admission cap below the harmful threshold or timely idle reclamation. One-thread-per-connection architecture alone is not proof.

## Primitive and impact limits

Report objects retained per action, applicable hard and soft limits, duration, cleanup rate and isolation scope. The direct effect is denial of new objects or scheduler capacity. Privilege escalation or code execution requires a separate failure-path defect.

## Related knowledge and primary sources

Queue, leak and cleanup profiles cover related retention mechanisms. This profile keeps count-limited OS and runtime objects distinct from byte-oriented memory or disk budgets.

Reviewed 2026-10-09 against POSIX [`getrlimit()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/getrlimit.html), Linux [`proc_pid_limits(5)`](https://man7.org/linux/man-pages/man5/proc_pid_limits.5.html), Windows [job object limits](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) and [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html). Concrete limits and object accounting are platform- and deployment-specific.
