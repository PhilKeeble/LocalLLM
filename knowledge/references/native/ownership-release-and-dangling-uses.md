---
id: reference-native-ownership-release-dangling
title: Native ownership, use-after-free, invalid free, realloc and dangling captures
kind: reference
topics: [lifetime, ownership, use-after-free, double-free, realloc, callbacks, dangling]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Ownership, release and dangling uses

## Object lifetime is not storage lifetime

C++ object lifetime depends on suitable storage and initialization; it can end
at destructor entry, storage release or storage reuse as specified by the object
model. Still-mapped storage does not grant permission to access an object whose
lifetime ended. Construction/destruction and transparent replacement have
special rules; do not treat every access in a destructor as automatically
invalid. [1]

For a binary finding, record allocation identity/generation, owning fields,
borrowed aliases, release operation and later consuming instruction. Address
equality is not object identity when storage can be reused. Nulling one owner
does not update independent aliases. Conversely, an address appearing only in
saved diagnostic evidence is not proof of a later target memory access.

## Use-after-free through callbacks and asynchronous work

Constructed sequence: owner registers callback with a raw context pointer;
shutdown releases the owner; an already queued callback reads its fields.
The candidate requires evidence that registration did not retain ownership,
shutdown did not wait for quiescence, and the callback can run after release.
A cancellation request is not by itself evidence of completed cancellation;
read the actual API's completion/lifetime contract.

Trace every ownership edge through registration, enqueue, dequeue, callback,
error and teardown. Check refcount increments occur while a valid reference
still protects the object. For C++ weak_ptr, lock atomically attempts to obtain
shared ownership; a separate expired check is not equivalent. [2] Keeping an
owner alive does not automatically synchronize access to its mutable fields.
Raw intrusive-refcount and OS callback protocols require their own rules.

## Use-after-return, scope and temporary views

A borrowed pointer/view or reference does not become an owner merely because
it is copied. Temporary destruction normally occurs at the end of the full
expression; specified reference-binding contexts can extend lifetime, with
exceptions. A temporary bound to a reference parameter survives the containing
full expression, not arbitrary later work. [3]

Constructed example: storing a string_view into a temporary string for a queued
operation leaves the underlying character storage unprotected after the
temporary ends. A copied view copies its range, not that string. [4] Recover
the destructor point and actual later dereference; do not infer a bug if the
consumer synchronously copies the bytes before the temporary ends.

## Lambda capture does not imply ownership of the pointee

For C++ reference captures, validity depends on the referred object's lifetime,
not merely the closure or intermediate reference variable. [5] Capturing a raw
pointer by value preserves the pointer value, not ownership of its pointee.
Capturing an owning object by value can have a different contract; inspect the
selected copy/move operation, as described by
`reference-native-cpp-lifetime-move-decompiler`.

Constructed investigation: a closure outlives the creating function. Determine
whether each field contains copied scalar state, an owner, a view or a reference
to a local. Trace closure copies and final destruction. Returning a closure
capturing a reference parameter is not inherently invalid if the actual referred
object outlives all invocations; establish that lifetime rather than flagging
every escaping reference capture.

## Double free, invalid free and deallocator identity

Ordinary C free requires the allocation's returned pointer, not an arbitrary
interior pointer or a pointer already freed; free(NULL) does nothing. [7]
C++ delete/delete[] have distinct allocation matching and dynamic-type rules;
a base-subobject pointer can be valid for appropriate single-object deletion,
so the blanket rule "all interior pointers are invalid for every deallocator"
is wrong. Check virtual/destructing-deallocation semantics. [6]

For repeated cleanup calls, prove they release the same allocation generation
twice on a feasible path, without a new acquisition that justifies the later
release. Include
exception edges and constructor failure. Two mutually exclusive cleanup blocks
are not such a path. Identify actual allocator family, heap instance and
module-supplied release callback; do not equate all functions named free.

## realloc success, failure and zero-size scope

For documented GNU libc realloc of a valid block to a nonzero size: failure
returns NULL and leaves the original block unchanged; success can move it.
GNU libc's non-null-pointer zero-size case frees and returns NULL, but other
implementations/language editions differ. Separate zero-size handling from
ordinary allocation failure. [8]

Investigation: direct assignment `p = realloc(p,n)` can lose the only original
pointer on nonzero failure. On successful movement, update aliases and interior
offsets; keeping an old borrowed pointer is unsafe. Track whether success was
tested before metadata size changes and whether copying used the old/new extent.
Do not infer rollback from NULL without the implementation and n value.

When reasoning about failed acquisition, preserve the selected allocator's error
channel and surviving ownership. A forced null result from an allocation form
specified to throw is not its ordinary failure contract. See
reference-validation-failure-models-partial-effects for the scoped C++ distinction
and playbook-validation-error-path-investigation for partial-initialization exits.

## DLL and allocator ownership boundaries

Microsoft documents corruption risks when a block allocated by one CRT/heap is
released through another. Crossing a DLL boundary alone is not the defect:
shared compatible runtime/heap contracts or a matching exported release function
can make it valid. Identical CRT code does not make distinct heap instances
interchangeable. [9]

Investigate imports, allocator handles, runtime linkage and API ownership
documentation. Preserve the allocating component and exact release path in a
lifetime trace. A failed deallocation may be the first detected symptom of an
earlier overwrite; compare allocator diagnostics with the allocation history.

Windows HeapAlloc/HeapReAlloc/HeapFree contracts have their primary home in
`reference-windows-heap-allocation-contracts`; allocator identity, CRT debug
wrappers and diagnostic limits are in `reference-windows-heap-identity-diagnostics`.
For the acquisition-to-use evidence workflow, use
`playbook-validation-allocation-lifetime-trace`.

## Sources: lifetime and language contracts

Reviewed 2026-10-02. Current C++ working draft, scoped libc/CRT documentation and
constructed scenarios; no target reproduction. Apply the shipped runtime and
language edition when exception, replacement or zero-size behavior matters.

1. [C++ object lifetime](https://eel.is/c++draft/basic.life).
2. [weak_ptr observers](https://eel.is/c++draft/util.smartptr.weak.obs): atomic lock.
3. [Temporary lifetime](https://eel.is/c++draft/class.temporary).
4. [string_view](https://eel.is/c++draft/string.view.template): borrowed range invalidation.
5. [Lambda captures](https://eel.is/c++draft/expr.prim.lambda.capture).
6. [Delete expressions](https://eel.is/c++draft/expr.delete).

## Sources: allocation implementations

7. [Linux malloc/free](https://man7.org/linux/man-pages/man3/malloc.3.html): allocation matching and free behavior, man-pages 6.19.
8. [GNU libc changing block size](https://sourceware.org/glibc/manual/latest/html_node/Changing-Block-Size.html).
9. [Microsoft CRT objects across DLL boundaries](https://learn.microsoft.com/en-us/cpp/c-runtime-library/potential-errors-passing-crt-objects-across-dll-boundaries?view=msvc-170).
