---
id: vulnerability-concurrency-aba-generation-wrap-stale-completion
title: ABA, generation wrap, or stale completion bound to a reused object
kind: vulnerability
topics: [concurrency, aba, generations, object-reuse, stale-completion]
platforms: [cross-platform]
architectures: [any]
---

# ABA, generation wrap, or stale completion bound to a reused object

## Definition and violated invariant

An ABA or reuse vulnerability occurs when code treats equality of a pointer, slot, handle, state value or finite generation as proof that the underlying object and relevant history are unchanged. A completion or atomic update must remain bound to the logical object generation and state captured when the operation began.

ABA can occur without freeing memory: a value can change from A to B and back to A while an observer retains stale dependent state. Reclamation safety and logical freshness are separate obligations.

## Conditions that establish the issue

Identify the compared representation, dependent state captured before the comparison, every transition that can change and restore the representation, storage or identifier reuse, reclamation protocol, generation width and reset rules, and the commit operation. Prove a feasible stale observer passes the equality check and applies old state to a different history or object generation.

For generation wrap, establish a plausible number and rate of reuses relative to the maximum outstanding operation lifetime. For reconnect or restart, account for explicit counter reset even when arithmetic wrap is infeasible.

## Evidence that is not sufficient

A compare-and-exchange loop, reused address, finite counter, repeated handle value, or late completion is not sufficient. No stale dependent state may exist, reclamation may exclude the interval, a wider generation may remain unique for all outstanding work, or commit may validate another stable identity.

A successful compare-and-exchange proves equality of the compared representation at that instant, not absence of intervening changes.

## Investigation sequence

Trace the initial observation and list every value derived from it, including successor pointers, owner, length, request context and authorization state. Enumerate transitions before the final compare or lookup and preserve object generations even when addresses match. Determine what keeps every dereferenced object alive.

For completions, bind submission token, session or device generation, slot reuse and commit-time lookup. Calculate wrap or reset feasibility from actual width and lifecycle instead of labeling every small counter exploitable.

## Constructed lock-free stack schedule

Thread A reads `head=P` and `P->next=Q`. Thread B removes P, removes Q, and later places the still-valid node P back at the head. Thread A compares only `head==P`; its compare-and-exchange succeeds and installs the stale successor Q even though the stack changed in between. The address equality is real, but the history on which A's `Q` depended is no longer current.

The finding requires the stated operations to overlap and the reclamation protocol to permit A's reads. If P or Q was freed without protection, a use-after-free may be an additional or earlier root cause rather than evidence needed for logical ABA.

## Primitive and impact limits

The direct result can be stale state commit, lost or duplicated list elements, completion applied to a new session, wrong-owner update, or invalid lifetime transition. Consequences range from logic corruption and authorization bypass to memory corruption, depending on the reused identity and consumer.

## Related knowledge and primary sources

`reference-concurrency-refcounts-reuse` and `reference-concurrency-cancellation-completion-shutdown` cover ABA, generations, reclamation and stale sessions. This profile repeats representation equality, intervening history, lifetime and commit binding locally.

Reviewed 2026-10-09 against the C++ [compare-and-exchange contract](https://eel.is/c++draft/atomics.types.operations), Linux kernel [kref ownership rules](https://docs.kernel.org/core-api/kref.html), and [MITRE CWE-362](https://cwe.mitre.org/data/definitions/362.html). The schedule is constructed.
