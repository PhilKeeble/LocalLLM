---
id: vulnerability-lifetime-heap-use-after-free
title: Heap use-after-free
kind: vulnerability
topics: [memory-safety, use-after-free, dangling-pointer, heap, lifetime]
platforms: [cross-platform]
architectures: [any]
---

# Heap use-after-free

## Definition and violated invariant

A heap use-after-free occurs when code accesses an object through a pointer or reference after that allocation generation has been released. Object validity depends on lifetime, not whether the address remains mapped or still contains familiar bytes. If the allocator reuses the address, the stale pointer does not become valid for the new object merely because the numeric address is unchanged.

This profile covers a later read, write or dispatch through stale heap identity. Releasing the same generation twice is double free; using a local after its function returns is use-after-return; a valid live object accessed without synchronization is a race unless the race also permits destruction before the access.

## Conditions that establish the issue

Prove one allocation generation, the operation that ends its lifetime, a surviving alias, and a feasible later instruction that dereferences or otherwise consumes that alias. For concurrent or asynchronous paths, prove the ordering can place release before use and that no reference, lock, rundown protocol, cancellation completion or queue ownership keeps the object alive.

Attacker relevance requires influence over the path or timing and a consequence at the later use. Reallocation is not required to establish the invalid access, but it materially changes the possible bytes and object semantics observed through the stale pointer.

## Evidence that is not sufficient

A `free` call followed textually by the same variable name, a stale address in a log, allocator reuse elsewhere, or a crash in a virtual call is not sufficient. The paths may be mutually exclusive, the pointer may be reassigned to a new generation, the queue may retain ownership, or the later code may compare the address without accessing the expired object.

Nulling one owner does not clear independent aliases, while a non-null pointer does not prove its pointee is alive. Decompiler variables can merge different stack slots or allocation generations; reconstruct identity from definitions, releases and uses rather than names alone.

## Investigation sequence

Create a lifetime ledger containing allocation site, generation, owning references, borrowed aliases, transfers, refcount changes, queue or callback registrations, release sites and later uses. Follow normal, error, timeout, cancellation and teardown edges. For each release/use pair, determine whether synchronization or ownership establishes a happens-before order that excludes the stale use.

At the consuming instruction, classify the operation: data read, data write, virtual or callback dispatch, deallocation, length lookup or pointer arithmetic. Recover any intervening reuse and the new object's layout separately. Check whether the stale value can be refreshed, validated or protected before use; an address-equality check cannot establish generation identity.

## Constructed source example

This hypothetical queue stores a borrowed pointer but cancellation frees the object without removing that queued entry:

```c
struct job {
    void (*run)(struct job *);
    unsigned int state;
};

void cancel_job(struct job *job)
{
    free(job);
}

void run_one(void)
{
    struct job *job = dequeue_job();
    job->run(job);
}
```

The later call is use-after-free only if `dequeue_job` can return the same allocation generation after `cancel_job` releases it and no queue ownership or synchronization prevents that ordering. If cancellation removes the entry and waits for in-flight consumers, or enqueue retains a reference released after dispatch, the shown fragments do not establish the issue.

## Constructed Windows x64 representation

For the constructed layout, the callback pointer is the first field. This abbreviated Windows x64 dispatch receives the queued pointer from `dequeue_job`; no compiler-specific object layout beyond that stated field is assumed:

```asm
call dequeue_job
test rax, rax
je   no_job
mov  rcx, rax             ; first argument = stale job candidate
call qword ptr [rax]      ; read callback field, then transfer control
```

The indirect call proves a read and dispatch through the returned address, not that the address was freed. Establish the earlier release and missing lifetime protection on a feasible path. If storage was reused, also prove which bytes now occupy `[RAX]`; a crash target or attacker-chosen callback requires more evidence than the stale dispatch itself.

## Primitive and impact limits

The direct primitive depends on the stale operation: read can expose or consume replacement data, write can corrupt a new object, and indirect dispatch can use replacement control data. Record reuse control, stale offset, operation width, timing reliability and subsequent use. A fault on unmapped or poisoned storage supports denial of service for the exercised path.

Code execution requires a controlled replacement or corruption that reaches an invoked control-bearing value under the target allocator and mitigations. Do not infer attacker-controlled reuse from the mere possibility that a freed chunk can be allocated again.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling` owns the detailed C/C++ lifetime, callback, `realloc` and allocator-family contracts. `reference-concurrency-refcounts-reuse` owns concurrent reference-count and generation reasoning. The release-before-use proof is repeated here because it is decisive to this vulnerability classification.

Reviewed 2026-10-09 against [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html), the C allocation rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), the C++ [object lifetime rules](https://eel.is/c++draft/basic.life), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The queue and assembly are constructed examples.
