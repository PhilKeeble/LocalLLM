---
id: reference-rust-ffi-boundaries
title: Rust FFI calling conventions, native ownership, callbacks and unwind boundaries
kind: reference
topics: [rust, ffi, abi, extern, box, cstring, callbacks, unwind, ownership]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Rust foreign-function interface evidence

## Rust, C and system ABIs: recover the boundary, not just its name
FFI means foreign-function interface. Rust's native ABI has no stability guarantee.
extern "C" uses the target's C convention; extern "system" normally agrees with C,
but uses stdcall for nonvariadic functions on 32-bit x86 Windows. Its variadic
functions use C. An -unwind ABI variant changes unwind permission, not ordinary
argument placement. [1]

Recover each side's signature, widths, aggregate layout, return convention and
callback convention. An exported spelling or repr(C) object alone does not
establish these. C-compatible aggregate representation is a separate rule from
whether its pointed-to storage remains live. Use `reference-rust-layout-dispatch`
and the relevant architecture ABI reference together.

## Box::into_raw and Box::from_raw: one owner and a compatible allocation
Box::into_raw transfers responsibility for an allocation to the caller without
automatically destroying it. Box::from_raw creates an owning Box; subsequent
destruction drops T and releases its allocation, if any. [2] For default Box<T>
with nonzero-sized T, storage must come from Rust's global allocator with layout
appropriate for T and contain a valid T. A zero-sized T still requires a non-null,
suitably aligned pointer and valid value. [5]

It is not enough that a pointer is non-null or came from some malloc-like API.
Reconstructing two owners for the same allocation can cause repeated destruction.
Conversely, Box::from_raw is not restricted solely to pointers previously returned
by into_raw: other origins must meet its full allocation contract. Establish
allocation origin, exact base, allocator and transfer count; distinguish borrowed
native use from ownership transfer.

## CString ownership: Rust allocation is not arbitrary C malloc storage
CString owns a NUL-terminated C-compatible string without interior NUL bytes.
Its into_raw transfers ownership; CString::from_raw may reclaim only a pointer
previously produced by that transfer, not an arbitrary foreign string. Returning
ownership twice or freeing the allocation with an unrelated foreign deallocator
violates the contract. [3]

When reclaiming, the recomputed string length must match the original length;
foreign code must not change where the terminating NUL establishes that length.
For a borrowed foreign string, use a borrowing contract such as CStr, not an
invented CString owner. Check whether native code retains the pointer after the
Rust owner is dropped; a NUL terminator alone provides no lifetime guarantee.

## Native callbacks: code pointer, context and retained storage
Investigation guidance: record the callback function ABI separately from its
context pointer. Establish whether the registration borrows or owns context,
whether callbacks are synchronous or retained, which threads invoke them, and
what proves no further callback can run. These are contracts of the native API,
not guarantees supplied by the Rust syntax of the callback.

Connect callback accesses to Rust reference/aliasing rules and actual ownership.
Cancellation is not proof of completed rundown; dropping context before the last
callback can create a use-after-free. A callback into Rust can also panic, so
inspect its unwind boundary. Use `reference-rust-unsafe-memory` and
`reference-rust-ownership-drop-panic` for those independent obligations.

## extern C versus C-unwind: Rust panics crossing native calls
A Rust panic reaching a non-unwinding ABI boundary such as extern "C" aborts
the process. With panic=unwind, cleanup before that boundary abort is not a
portable guarantee: the Reference permits either no destructors or all relevant
destructors up to the boundary. panic=abort aborts without unwinding. [4]

An extern "C-unwind" boundary permits unwinding when the panic strategy unwinds;
it does not convert a panic into an error return or make foreign frames safe by
itself. Trace the complete intervening call chain and foreign runtime contract.
A callback's C-looking symbol does not establish that the exported ABI allows
its panic to propagate.

## Foreign exceptions: boundary permission and panic strategy are separate
For native unforced unwinding, crossing a non-unwinding Rust ABI boundary is
undefined behavior. At an unwinding ABI boundary, the documented behavior is
unwinding with panic=unwind and process abort with panic=abort. These rules explicitly
exclude forced unwinding mechanisms. [4]

Do not apply these boundary rules to every longjmp or thread-exit mechanism, or assume
catch_unwind provides a portable foreign-exception handler. Its separate API
limits are in `reference-rust-ownership-drop-panic`. Identify the actual exception
origin, ABI and panic strategy before attributing missing cleanup or process exit
to a vulnerability.

## Primary sources and scope
Reviewed 2026-10-02 against the living Rust Reference and standard-library pages
identifying Rust 1.99.0. ABI/ownership contracts are not evidence that a particular
binary used them correctly. Callback review is derived investigation guidance;
the specific registration API still supplies its retention and threading contract.

1. [External blocks and ABI conventions](https://doc.rust-lang.org/reference/items/external-blocks.html): Rust/C/system and unwind variants.
2. [Box raw conversions](https://doc.rust-lang.org/std/boxed/struct.Box.html): into_raw/from_raw allocation and ownership requirements.
3. [CString raw conversions](https://doc.rust-lang.org/std/ffi/struct.CString.html): NUL invariant, allocation origin and reclamation length.
4. [Function ABIs and unwinding](https://doc.rust-lang.org/reference/items/functions.html#unwinding): Rust/native unwind behavior and forced-unwind exclusion.
5. [Box memory layout](https://doc.rust-lang.org/std/boxed/index.html#memory-layout): global allocator, valid T and zero-sized-value requirements.
