---
id: reference-dotnet-unsafe-memory-lifetimes
title: .NET unsafe memory, pins, pools and SafeHandle lifetime evidence
kind: reference
topics: [dotnet, unsafe, span, pinning, safehandle, lifetime, memory-pools]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET unsafe memory and lifetimes

## Scope and independent obligations

Reviewed 2026-10-02. For each unsafe/native use establish backing storage,
actual extent, initialization, alignment, GC movement, logical ownership and
release time separately. A managed reference is not proof of a valid native
handle or an unexpired pool lease. Modern Span/Memory APIs are not automatically
available on every .NET Framework target. Representation facts:
reference-dotnet-interop-representations. Investigation workflow:
playbook-re-dotnet-native-boundaries.

## Rooting does not pin or prevent explicit disposal

Rooting keeps an object reachable by the garbage collector (GC); pinning also
prevents the managed storage from moving during the pin's lifetime. Neither
concept by itself grants logical ownership of a pooled buffer or native resource.

GCHandleType.Normal prevents collection but does not pin; Pinned additionally
prevents relocation and allows obtaining the pinned address. Weak handles permit
collection. [1] GC.KeepAlive extends GC reachability through the point of its
call; it has no other lifetime-management side effects. [2]

Inference: KeepAlive does not prevent another thread from calling Dispose,
returning an array to a pool or explicitly freeing a native allocation.
A GCHandle cookie passed through native code is an opaque managed-handle token,
not automatically a pointer to the object's bytes. Track handle kind and release.
Delegate retention has its own canonical rule in
reference-dotnet-delegates-async-lifetimes; a native function pointer is not a root.

## Fixed and Unsafe.AsPointer have different guarantees

A C# fixed statement prevents relocation of its pinned movable storage while
the statement executes. It does not promise a valid retained pointer after the
block ends. [3] Unsafe.AsPointer converts a managed by-reference value to an
unmanaged pointer that the GC does not track; for GC-managed storage the caller
must ensure pinning while that unmanaged pointer is used. [4]

Inference: follow pointer escape into native state, callbacks or asynchronous
requests. A fixed block around submission alone is insufficient when the callee
uses the pointer later. Conversely, a pointer into native or still-live stack
storage does not require GC pinning; it requires that storage's own lifetime.
Evidence of an escaped pointer still needs its use interval and the absence of
another mechanism preserving the storage's address and lifetime.

## Memory.Pin covers a pin lease, not completion or authorization

Memory<T>.Pin and related APIs return MemoryHandle for pinned memory. Disposing
that handle releases its pin/associated IPinnable ownership. [5]

Inference: a native asynchronous consumer must finish using the pointer before
the pin lease ends. A Memory<T> value surviving an await does not independently
pin its underlying storage, preserve a pool rental, or keep an external memory
manager undisposed. Establish backing owner, pin owner and terminal consumer.
Cancellation notification is not terminal completion; use
reference-dotnet-delegates-async-lifetimes for that separate contract.

## Pointer-backed Span bounds do not prove allocation bounds

Span<T>(void*, length) receives a caller-supplied element extent. It rejects a
negative length but does not validate that the pointer identifies a live
allocation containing that many elements. The array/start/length constructor,
in contrast, checks the specified range against the array. [6]
MemoryMarshal.CreateSpan(ref value, length) does not check the supplied length
or establish that the returned span's lifetime is safe. [7]

Inference: bounds checks on later span indexing are only as trustworthy as its
construction. A fabricated oversized extent can make an index pass the span
check while exceeding real storage. Recover pointer/ref provenance and actual
allocation independently; the word Span is not evidence of a safe boundary.

## MemoryMarshal.Cast reinterprets storage, not a wire schema

MemoryMarshal.Cast changes the element view and count over the same storage.
Managed-reference-containing element types are rejected. It requires a platform
supporting misaligned access or otherwise suitably aligned storage. Values
depend on the machine representation; this is not endian conversion. [8]

Constructed example: a five-byte span viewed as ushort contains two complete
ushort elements, not a validated two-element message with the fifth byte
consumed. Inference: enforce exact framing/remainder rules separately and use
explicit byte order for a wire format. A successfully constructed view does not
validate semantic field ranges, padding, discriminants or pointer fields.

## Stackalloc is method-lifetime storage, not zeroed managed heap storage

C# stackalloc storage lasts until the executing method returns, does not require
GC pinning, and cannot be explicitly freed. Its initial contents are undefined
unless initialized. Stack space is limited; repeated allocations inside loops
can exhaust it. [9]

Inference: an observed zero-filled run is not an initialization contract.
Recover which bytes are written before any output, including padding and unused
capacity, and bound allocation size and repetition. Span indexing and runtime
overrun mitigations do not make arbitrary escaped pointers safe after return.
For a finding, identify unbounded size/repetition or a read lacking a defining
write; one observed stack allocation does not establish either condition.

## ArrayPool capacity, initialized length and lease lifetime differ

ArrayPool<T>.Rent returns an array at least as long as requested, potentially
larger and not zero-initialized. [10] Return relinquishes ownership: the caller
must stop using it, return it only once and to the same pool. With clearArray=true,
clearing is promised if the pool retains the buffer for reuse; it is not a
blanket secure-erasure guarantee when the pool drops it. [11]

Inference: expose only the initialized logical slice, not rented.Length.
GC reachability or a ReadOnlyMemory view does not extend the rental after Return.
Trace queued consumers, completion and return order. A post-return access can be
a logical use-after-return/data-isolation bug without the GC freeing the array;
prove the reuse schedule rather than asserting an immediate native heap UAF.

## DangerousGetHandle is a value read, not a SafeHandle lease

SafeHandle.DangerousGetHandle returns the stored value, which can remain stale
after invalidation; native handle recycling can give that value a different
meaning. [12] DangerousAddRef increments the SafeHandle reference count, delaying
its ReleaseHandle while the reference is held. Initialize success=false; match
DangerousRelease only when success became true, including exceptional paths. [13]

Inference: protect the full raw-handle use interval, not just extraction.
KeepAlive addresses collection, not explicit Dispose. A successful add-reference
does not duplicate an OS handle, prevent unrelated native code closing it, or
extend an asynchronous use beyond the matching release. Reconstruct actual
ownership/borrowing and native quiescence instead of treating IsClosed or a
nonzero raw value as a durable validity check.

## Allocator families and ownership determine the release API

FreeHGlobal matches allocations made by AllocHGlobal/ReAllocHGlobal or an
equivalent compatible allocator. [14] FreeCoTaskMem matches
AllocCoTaskMem/ReAllocCoTaskMem or the compatible native task allocator. [15]
These names are not interchangeable declarations that any pointer can be freed.

Inference: recover the actual allocator and specified native release function
for each returned pointer. Borrowed/static storage must not be treated as an
owned result; a SafeHandle subclass is correct only if its invalid-value and
ReleaseHandle contracts match the resource. Record who frees on success,
conversion failure and cancellation. An allocator-mismatch finding needs the
incompatible allocation/release pair on a feasible path, not merely two different
API names: a wrapper may delegate to a compatible underlying allocator.


## Sources: GC, pins and unsafe views

1. [GCHandleType](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.gchandletype?view=net-10.0): Normal, Pinned and Weak.
2. [GC.KeepAlive](https://learn.microsoft.com/en-us/dotnet/api/system.gc.keepalive?view=net-10.0): reachability interval only.
3. [C# fixed statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/fixed): pin scope; no reliance on preview language changes.
4. [Unsafe.AsPointer](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.unsafe.aspointer?view=net-10.0): unmanaged pointer tracking.
5. [MemoryHandle](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.memoryhandle?view=net-10.0): Pin and Dispose.
6. [Span constructors](https://learn.microsoft.com/en-us/dotnet/api/system.span-1.-ctor?view=net-10.0): pointer extent versus array range.
7. [MemoryMarshal.CreateSpan](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.memorymarshal.createspan?view=net-10.0): unchecked extent/lifetime.
8. [MemoryMarshal.Cast](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.memorymarshal.cast?view=net-10.0): representation, length and alignment.

## Sources: storage and resource ownership

9. [C# stackalloc](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/stackalloc): method lifetime, initialization and bounded allocation.
10. [ArrayPool.Rent](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1.rent?view=net-10.0): minimum capacity and initialization.
11. [ArrayPool.Return](https://learn.microsoft.com/en-us/dotnet/api/system.buffers.arraypool-1.return?view=net-10.0): ownership transfer and conditional clearing.
12. [SafeHandle.DangerousGetHandle](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.safehandle.dangerousgethandle?view=net-10.0): stale/recycled values.
13. [SafeHandle.DangerousAddRef](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.safehandle.dangerousaddref?view=net-10.0): reference acquisition and matching release.
14. [Marshal.FreeHGlobal](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.freehglobal?view=net-10.0): compatible allocation family; not the page's unsafe post-free example.
15. [Marshal.FreeCoTaskMem](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.freecotaskmem?view=net-10.0): task allocation family.
