---
id: reference-windows-heap-allocation-contracts
title: Windows heap allocation, reallocation, identity, sizes and lifetime contracts
kind: reference
topics: [heap, allocation, heaprealloc, heapsize, ownership, lifetime, initialization]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# Windows user-mode heap contracts

## Heap handle identifies an instance, not every allocation in the process

GetProcessHeap supplies the default process heap; HeapCreate creates a private
heap. HeapCreate's zero maximum permits growth; a nonzero maximum limits growth.
Reserved heap capacity includes allocator overhead, not just application blocks.
A private heap belongs to the process, not exclusively to the DLL that creates
it. [1] Therefore a heap is not a security boundary between in-process plugins.

Investigation: record the actual handle reaching allocation, resize and release,
including wrapper state. Equal API names do not establish equal heap instances.
HeapCreate failure is NULL with GetLastError available. [1] A failed creation
must not silently become a request to use an unrelated heap. Allocator internals
and diagnostics live in reference-windows-heap-identity-diagnostics.

## HeapAlloc byte count, initialization and alignment

HeapAlloc takes a SIZE_T byte count and a heap handle. HEAP_ZERO_MEMORY (0x8)
requests zeroed storage; otherwise the allocation is uninitialized. Documented
alignment is MEMORY_ALLOCATION_ALIGNMENT: 16 bytes for _WIN64, otherwise 8 for
the x86/ARM targets here. This is not a guarantee of arbitrary over-alignment.
Failure returns NULL unless heap/call flags request exceptions. HeapAlloc does
not set last error for failure. [2]

Constructed investigation: a caller requests 24 bytes then publishes a 32-byte
record. Recover the size expression, stores and actual consumer range; alignment
does not authorize the extra bytes. Zero-filled bytes alone do not establish a
constructed C++ object, valid tagged union or initialized resource handle.
Treat arithmetic overflow separately from whether the allocator accepted the
already-computed byte count.

## HeapReAlloc failure preserves the old block; success may move it

For HeapReAlloc with a valid block from the specified heap and without exception
failure mode, failure returns NULL without freeing the original allocation. Without
HEAP_REALLOC_IN_PLACE_ONLY (0x10), successful resizing may move the block; that
flag forbids movement and causes failure when in-place resizing is impossible.
The API does not set last error for failure. [3]

Direct assignment `p = HeapReAlloc(h,0,p,n)` can lose the only owner on failure.
Check premature size updates and stale aliases after movement. Do not import
C realloc's NULL-input or zero-size rules; lpMem denotes an existing allocation.

## HeapReAlloc zeroing is growth-only, not sanitization of existing bytes

For HeapReAlloc growth with HEAP_ZERO_MEMORY, only the added region is zeroed;
existing contents are preserved. The flag does not clear the old prefix. [3]
Constructed example: successfully grow 24 bytes of 0xA5 to 40 bytes with that
flag. The original [0,24) remains 0xA5; added [24,40) is zero. New capacity is
not a newly empty record or meaningful payload length. Verify the success branch
before using the new extent; failure preserves the previous allocation.

## Exception allocation mode changes the failure edge

HEAP_GENERATE_EXCEPTIONS (0x4), selected at heap creation or allocation, changes
HeapAlloc/HeapReAlloc failure handling from NULL return to an exception. [1,2,3]
Recover creation flags as well as per-call flags: testing the returned pointer
does not by itself cover a raised exception. Follow cleanup and partially
published state through the applicable exception model; see
reference-windows-msvc-exception-cleanup-evidence.

Investigative distinction: an exception or NULL can result from resource failure;
neither alone demonstrates an attacker-controlled overflow. Conversely, catching
an allocation exception does not undo prior writes or reservations. Record which
operation failed and which obligations had already been acquired.

## HeapFree requires matching provenance and does not invalidate every alias

HeapFree expects the returned allocation pointer from the indicated heap;
lpMem may be NULL. A repeated free can corrupt the heap. After release, neither
payload access nor HeapSize is a valid way to use the old allocation. Success
is nonzero; zero indicates failure with GetLastError available. [4]

Investigation: trace the allocation base separately from an interior view,
borrowed callback context or adjusted C++ pointer. The correct release contract
may be an exported owner function, not direct HeapFree. Do not free a CRT/debug
wrapper's user pointer through a guessed underlying heap. Nulling one field
does not revoke copied aliases. Use reference-native-ownership-release-dangling
for generic ownership and C++ deletion rules; a heap API contract does not
replace language-specific destruction requirements.

## HeapSize is not an arbitrary-pointer validator or initialized length

HeapSize requires a live HeapAlloc/HeapReAlloc block from the supplied heap.
Microsoft documents success as the requested allocation size in bytes, failure
as (SIZE_T)-1, and no last-error information. Passing a block from another heap
has undefined behavior. [5] Do not search for an owner by calling HeapSize with
guessed handles on a suspect pointer.

For a 64-bit SIZE_T, failure is 0xFFFFFFFFFFFFFFFF, not 0x00000000FFFFFFFF.
A debugger's rounded storage extent is a different measurement. Neither it nor
HeapSize proves initialized payload length, nested object bounds or lifetime.
Constructed case: a 64-byte allocation contains a 20-byte message; returning 64
bytes can disclose data even though every access lies inside the allocation.
Read the producer's meaningful-length contract, not just the storage size.

## Heap serialization protects allocator operations, not object ownership

Heap allocation/free operations normally serialize access. HEAP_NO_SERIALIZE
(0x1) removes this allocator mutual exclusion and must not be used with the
default process heap. It requires exclusive heap use or external synchronization
for concurrent access. A heap created with that option cannot be locked using
HeapLock/HeapUnlock. [1,4]

Investigative inference: successful serialized HeapAlloc and HeapFree calls
do not protect an application's lookup-to-dereference interval. A second thread
can release an object after a first thread obtains its raw pointer. Recover
the owner/refcount/lock protocol separately. Conversely, HEAP_NO_SERIALIZE is
not alone proof of a race when the application establishes exclusive access.

## Private heap destruction is bulk storage release, not language cleanup

Microsoft describes HeapDestroy as releasing a private heap's pages and
invalidating its handle. Its enumeration example destroys only its own private
heap; Application Verifier identifies destroying the default process heap as
an error. [6,7] Do not apply HeapDestroy to GetProcessHeap's handle.

Investigative consequence: callers must account for outstanding blocks, aliases
and queued work before private heap teardown. Releasing backing pages is not
evidence that application destructors, handle closes or callback deregistration
ran. Recover those operations explicitly. A private-heap arena intentionally
reclaimed as a unit is not automatically a per-block leak; determine whether
the lifetime design also handles non-memory resources.


## Sources and scope: allocation API contracts

Reviewed 2026-10-02. These are Windows user-mode API contracts, not private heap
layouts or kernel pool rules. Exact large-allocation thresholds are intentionally
not inferred from generic fixed-heap limits across all architectures/builds.

1. [HeapCreate](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapcreate): flags, growable/fixed heaps, overhead and serialization.
2. [HeapAlloc](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapalloc): bytes, alignment, initialization and failure.
3. [HeapReAlloc](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heaprealloc): move restriction, retained block on failure, growth zeroing.
4. [HeapFree](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapfree): matching heap, release and results.

## Sources and scope: size and teardown

5. [HeapSize](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapsize): required provenance, size and failure sentinel.
6. [Enumerating a Heap](https://learn.microsoft.com/en-us/windows/win32/memory/enumerating-a-heap): private-heap lifecycle example and linked HeapDestroy contract summary.
7. [Application Verifier basic stops](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/application-verifier-stop-codes-basics): DESTROY_PROCESS_HEAP, not a guarantee of a particular uninstrumented failure mode.

Constructed examples illustrate contract reasoning, not discovered vulnerabilities.
