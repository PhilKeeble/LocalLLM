---
id: reference-go-cgo-and-unsafe
title: Go cgo pointer retention, native ownership and unsafe representations
kind: reference
topics: [go, cgo, ffi, unsafe, pinning, callbacks, ownership]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm, arm64, riscv64]
---

# Go native and unsafe boundaries

## Scope and call identity

Reviewed 2026-10-02 against official cgo, runtime and unsafe documentation.
cgo connects Go and C code. GC means garbage collection; pinning prevents the
collector from moving or reclaiming an object during a specified lifetime.
This reference supplements, rather than replaces, the native library's ABI and
ownership contract. Trace the actual wrapper and exported declaration; a Go
function's internal ABI is not automatically the C-facing signature. Establish
which side allocates, retains, calls back and releases each resource.

## Go-pointer classification and reachable storage

cgo classifies a pointer by allocation origin, not its declared type. Go storage
passed to C must be pinned and contain no pointers to unpinned Go storage.
Argument pinning lasts through the call, not arbitrary later retention. For a
field pointer, the relevant region is that field; for an array/slice element,
it is the whole array/backing array. [cgo pointer rules](https://pkg.go.dev/cmd/cgo#hdr-Passing_pointers).

Investigative consequence: recover the allocation and reachable pointer graph.
A cast to a C pointer type is not proof of C ownership. Passing one element does
not make other Go pointers in the backing array irrelevant.

## Pinning and reachability solve different problems

runtime.Pinner, available since Go 1.21, pins objects against GC movement/freeing.
Referenced Go objects needed by C require separate pinning. Keep the Pinner alive
and preserve the pin until C no longer retains the pointer; Unpin removes the pins
held by that Pinner, not the objects themselves. [Pinner](https://pkg.go.dev/runtime#Pinner).

runtime.KeepAlive preserves reachability through its call site; it does not
waive unsafe.Pointer rules. [KeepAlive](https://pkg.go.dev/runtime#KeepAlive).

Investigative consequence: a lexical variable or KeepAlive after submission is
not an asynchronous pin lease. Neither pinning nor reachability prevents an
application from explicitly closing a separate native handle or reusing storage.
Identify the last native access, not just the return from registration/cancel.

## Copies, counts and native deallocation

C.CString and C.CBytes allocate copies in C memory that the caller must arrange
to free. C.GoStringN and C.GoBytes copy using explicit C.int lengths. For cgo's
two-result C calls, inspect the native success result before errno: errno may
remain nonzero after success. [cgo conversions and calls](https://pkg.go.dev/cmd/cgo).

Investigative consequence: check count narrowing, embedded-NUL interpretation,
allocator pairing and the actual last borrower. A copied buffer is distinct from
the original Go storage, but is not automatically safe after a premature C free.

## cgo.Handle is an opaque token, not a dereferenceable pointer

cgo.NewHandle retains an association between an integer token and a Go value.
Zero is invalid. Delete invalidates the handle and must wait until C no longer
holds it; invalid Value or Delete calls panic. Coercing the integer to
unsafe.Pointer is not a valid substitute for passing it as an integer. Passing
the address of a handle variable introduces ordinary pointer-retention rules.
[runtime/cgo Handle](https://pkg.go.dev/runtime/cgo#Handle).

Investigative consequence: reconstruct creation, callback use and deletion as
one lifetime. Unregistering without excluding in-flight callbacks can leave a
late token use; failure to delete can retain resources. Do not confuse handle
identity with a native object address or permission to access a resource.

## uintptr is not a GC-visible reference

uintptr contains an integer address, not ownership or GC pointer semantics.
The documented arithmetic conversion back to unsafe.Pointer must stay within
the original allocation and occur in the same expression; it does not permit a
C-style one-past pointer. Other supported conversion patterns have their own
conditions. [unsafe.Pointer](https://pkg.go.dev/unsafe#Pointer).

Investigative consequence: distinguish an opaque external token from a retained
Go address. A currently nonmoving heap or apparently valid numeric address is
not sufficient lifetime evidence. Follow the original storage, not only the
integer's data flow.

## Unsafe views inherit caller-supplied extent and lifetime

unsafe.Slice constructs a view using the supplied pointer and count, not an
allocation-size lookup. unsafe.String requires the underlying bytes to remain
unmodified while the returned string exists. [unsafe views](https://pkg.go.dev/unsafe).

Investigative consequence: indexing checks against an invented length do not
establish real storage bounds. Check allocation extent, alignment, mutation and
retention independently. A zero-copy string backed by a recycled input buffer
can invalidate a previously checked value without any ordinary string assignment.

## Finding threshold

An unsafe import or cgo transition is a review surface, not a vulnerability.
A finding needs a feasible producer/consumer path and a specific violated extent,
representation, ownership or authorization contract. Trace native callbacks as
possible reentrancy boundaries and retain unresolved lifetime edges explicitly.
Workflow: playbook-re-go-boundary.
