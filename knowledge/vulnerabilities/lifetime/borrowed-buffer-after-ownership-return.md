---
id: vulnerability-lifetime-borrowed-buffer-after-ownership-return
title: Borrowed buffer used after unpinning, unmapping, dequeue, or ownership return
kind: vulnerability
topics: [lifetime, buffers, pinning, mappings, pools, ownership]
platforms: [cross-platform]
architectures: [any]
---

# Borrowed buffer used after unpinning, unmapping, dequeue, or ownership return

## Definition and violated invariant

This vulnerability occurs when a pointer, slice, span, mapping address, or native view outlives the lease that kept its backing storage stable and owned. Ending a pin can permit GC movement, unmapping removes address validity, returning a pooled buffer permits reuse, dequeue or release can transfer ownership, and completing a callback can end a borrowed argument's scope.

Reachability, address stability, logical ownership, and mapping lifetime are separate. Keeping a managed object reachable does not pin it, while closing a file descriptor does not necessarily unmap an existing mapping.

## Conditions that establish the issue

Identify backing owner, borrow or pin acquisition, accessible extent, lease end, asynchronous or retained consumer, and actual later dereference. Prove no independent pin, mapping, rental, or owning copy covers the full use interval.

For pooled buffers, establish reuse or unauthorized post-return access rather than claiming native deallocation. For pins, establish movable managed storage and native use after the pin ends.

## Evidence that is not sufficient

A raw pointer, pool return, unpin, unmap, dequeue, or asynchronous call is not sufficient. The callee may copy synchronously, native storage may not require pinning, another lease may remain, or the operation may have completed before release.

A surviving view object does not itself extend the external lease unless its contract explicitly owns it.

## Investigation sequence

Build a lease timeline: acquire, pointer extraction, submission, terminal completion, last access, and release. Trace cancellation separately from completion. Record whether the pointer targets managed, native, mapped, shared, or pooled storage and which actor can move or reuse it.

At binary or IL boundaries, find pin/unpin or handle-dispose points and the native retention path. Confirm the later access uses the escaped address rather than a copied buffer.

## Constructed .NET example

```csharp
unsafe void Start(byte[] data)
{
    fixed (byte* pointer = data)
    {
        NativeBeginAsync(pointer, data.Length);
    }
}
```

The `fixed` block pins `data` only until block exit. If `NativeBeginAsync` retains the pointer and uses it later, the pointer is no longer protected from GC movement after return. A synchronous copy, a pin retained until terminal completion, or native-owned storage would change the conclusion.

## Primitive and impact limits

The direct primitive is access through an expired buffer lease. Results can include stale or cross-tenant data access, native memory corruption, incorrect I/O, or a fault. Impact depends on movement or reuse, direction, contents, and observability.

## Related knowledge and primary sources

`reference-dotnet-unsafe-memory-lifetimes` defines pin, pool, and handle leases, while `reference-native-resource-lifetimes-results` distinguishes mappings from descriptors. This profile repeats the lease interval locally.

Reviewed 2026-10-09 against Microsoft [C# `fixed`](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/fixed), Microsoft [`MemoryHandle`](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.memoryhandle), Microsoft [`ArrayPool.Return`](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1.return), Linux [`munmap`](https://man7.org/linux/man-pages/man2/munmap.2.html), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The example is constructed.
