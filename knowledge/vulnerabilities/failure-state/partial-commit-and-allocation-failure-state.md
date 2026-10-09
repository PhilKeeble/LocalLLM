---
id: vulnerability-failure-partial-commit-allocation-failure-state
title: Partial commit, incomplete rollback or allocation-failure state violation
kind: vulnerability
topics: [failure-path, rollback, partial-commit, allocation-failure, zero-size, cleanup]
platforms: [cross-platform]
architectures: [any]
---

# Partial commit, incomplete rollback or allocation-failure state violation

## Partial commit and incomplete rollback

This vulnerability occurs when an operation reports failure but leaves a security-sensitive side effect, authority change, resource publication, file/object replacement, reference, or partially updated invariant that later code treats as absent or complete. The invariant is explicit atomicity: either every required step commits, or failure leaves a documented recoverable state that callers correctly handle.

Trace effects in execution order through every failure, exception, timeout, cancellation, retry, and cleanup edge. Identify which effects are reversible, externally visible, durable, or observed concurrently. A failure return does not imply rollback, while partial completion is not a vulnerability if the API documents it and every consumer handles it safely.

## Cleanup ordering and publication

Cleanup can create a vulnerability when it releases ownership before excluding users, removes a temporary after publishing its name, restores identity too late, or destroys rollback information before all commits succeed. Prove the precise ordering and an observer or later path that consumes the inconsistent interval or residual effect.

A missing destructor-looking call or duplicate cleanup block is not sufficient. Establish the resource generation, ownership obligation, feasible path, and actual terminal state.

## Allocation failure and fallback

An allocation-failure vulnerability exists when failure, overflow rejection, zero-size behavior, reduced fallback capacity, or emergency allocation changes pointer, size, ownership, or initialization assumptions but later code proceeds under the normal-success contract. Recover requested size arithmetic, allocator result contract, returned capacity, initialization, fallback owner, and every consumer.

Do not assume a non-null zero-size allocation provides one usable byte, or that a null result always means the same condition across allocators. An out-of-memory process termination is availability impact; memory corruption requires a continuing path that misuses the failed or reduced result.

## Constructed source and representation

```c
if (count > SIZE_MAX / sizeof(struct item)) return ERROR;
size_t bytes = count * sizeof(struct item);
struct item *items = malloc(bytes);
if (!items) use_emergency_item(&items);   /* supplies space for one item */
for (size_t i = 0; i < count; ++i)
    initialize(&items[i]);
```

If fallback supplies one item while `count` remains greater than one, later iterations exceed the fallback extent. The explicit multiplication guard keeps this example about allocation failure rather than integer overflow. An emergency allocator that supplies `count` elements would disprove it.

```asm
call malloc
test rax, rax
jne  allocation_ready
lea  rcx, [rsp+28h]
call use_emergency_item
mov  rax, qword ptr [rsp+28h]
allocation_ready:
; later loop still compares its index with the original count
```

The assembly is a constructed Windows x64 control-flow shape for the fallback portion. Recover where `count`, actual capacity, and fallback pointer live in the target before claiming the loop can exceed the object.

## Primary sources and scope

Reviewed 2026-10-09 against C11 draft N1570 section 7.22.3 in the WG14 [committee document](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), POSIX [`malloc`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/malloc.html), and POSIX [`rename`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html) as one example of explicitly defined namespace atomicity. Transaction and durability guarantees are API- and storage-specific; `rename` does not make arbitrary multi-step updates durable or transactional.
