---
id: vulnerability-lifetime-allocator-deallocator-mismatch
title: Allocator and deallocator mismatch across heaps, modules, runtimes, or FFIs
kind: vulnerability
topics: [lifetime, allocators, heaps, ffi, modules, deallocation]
platforms: [cross-platform]
architectures: [any]
---

# Allocator and deallocator mismatch across heaps, modules, runtimes, or FFIs

## Definition and violated invariant

An allocator mismatch occurs when storage or a resource acquired from one allocation family, heap instance, runtime, module contract, or foreign interface is released through an incompatible operation. Matching names are insufficient: two heap instances can use the same API, while different exported function names can deliberately form one compatible ownership pair.

The invariant includes allocation family, instance or context handle, returned pointer form, object/array construction contract, and the component responsible for release.

## Conditions that establish the issue

Trace the allocation call and resolved implementation, heap or arena handle, module/runtime identity, returned base, ownership transfer, and final release. Prove the release contract does not accept that provenance. For FFI values, include marshalling copies and provider-supplied release callbacks.

For C++, distinguish `new` from `new[]`, placement allocation, class-specific deallocation, and destructor selection. For Windows heaps, the same `HeapFree` function still requires the heap handle that allocated the block.

## Evidence that is not sufficient

Crossing a DLL, shared-library, or language boundary is not sufficient. Components can share a compatible runtime or expose a matching release function. Likewise, different symbol names do not prove incompatibility when wrappers delegate to the same allocator.

An allocator diagnostic can be a symptom of earlier overwrite; corroborate provenance before assigning mismatch as root cause.

## Investigation sequence

Build an allocation ledger containing provider, family, instance, flags, size, base, constructed type, owner, and required release. Resolve imports and interposition to the selected implementations. Follow success, transfer, failure, and cleanup paths independently.

At binary calls, recover context or heap handles as well as the pointer. Compare allocation and release instances; do not infer a process-wide universal heap from one familiar API.

## Constructed Windows example

```c
void *allocate_record(HANDLE private_heap)
{
    return HeapAlloc(private_heap, 0, 64);
}

void destroy_record(void *record)
{
    free(record);
}
```

The release is mismatched when `record` is the direct result from that private Windows heap and `free` does not delegate to the same heap contract. The relevant call pattern is `HeapAlloc(heap,0,64)` returning `RAX`, followed later by that value in `RCX` to `free`; crossing functions alone is not proof, so resolve wrappers and heap provenance.

## Primitive and impact limits

The direct primitive is release through an incompatible provider. It may corrupt allocator state, leak the allocation, terminate the process, or appear to succeed while violating ownership. Exploitability depends on provider internals, subsequent operations, and mitigations.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling`, `reference-windows-heap-allocation-contracts`, and `reference-linux-libc-allocator-identity` provide platform contracts. This profile repeats provider and instance identity locally.

Reviewed 2026-10-09 against Microsoft [CRT objects across DLL boundaries](https://learn.microsoft.com/en-us/cpp/c-runtime-library/potential-errors-passing-crt-objects-across-dll-boundaries), Microsoft [`HeapFree`](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapfree), C++ [new expressions](https://eel.is/c++draft/expr.new) and [delete expressions](https://eel.is/c++draft/expr.delete), and [MITRE CWE-762](https://cwe.mitre.org/data/definitions/762.html). The example is constructed.
