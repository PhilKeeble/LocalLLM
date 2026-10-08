---
id: reference-rust-unsafe-memory
title: Rust unsafe memory, validity, aliasing, raw slices and initialization
kind: reference
topics: [rust, unsafe, undefined-behavior, aliasing, unsafecell, maybeuninit, raw-pointers, utf8]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Rust unsafe memory contracts

## unsafe is permission to perform operations, not proof they are valid
Rust's unsafe operations still have safety requirements. Undefined behavior can
arise from invalid values, dangling or misaligned accesses, aliasing violations
and data races. Producing a typed value includes reading, assigning, passing or
returning it; a later explicit dereference is not always required. [1]

For a finding, identify the operation and violated contract on a feasible path.
An unsafe block alone proves no defect. Safe-looking callers can depend on an
unsound unsafe implementation or foreign routine, so investigate across those
boundaries. Language attribution does not establish correctness of access-control
checks, protocol state, resource accounting or other logical invariants.

## Typed values: arbitrary bytes are not arbitrary valid Rust objects
A Rust bool admits 0 or 1; char admits Unicode scalar values, excluding surrogates.
References must satisfy non-nullness, alignment and validity requirements.
Raw pointers do not have the same validity requirements as references. [1]

Investigate the point at which external bytes become a typed value. A raw pointer
holding a suspicious address is not equivalent to constructing a reference to
it. Do not accept a forged enum, reference or owner merely because its size fits
the input buffer. Initialization of bytes, validity of T and application/library
invariants are separate questions.

## References, aliasing and UnsafeCell interior mutation
Rust shared references normally disallow mutation of the referenced data;
UnsafeCell permits interior mutation through shared references. It does not
waive the uniqueness requirements of mutable references and does not prevent
data races. Synchronization is still necessary for conflicting concurrent access. [2]

Trace overlapping borrows, native writes and callbacks over their actual lifetimes.
Do not treat a raw-pointer cast as ending an existing borrow. The Rust Reference
explicitly says exact aliasing rules are not fully determined. [1] A proposed
model such as Stacked Borrows is not a universal normative ABI contract; explain
the concrete supported violation rather than asserting an unqualified model rule.

## MaybeUninit and assume_init: initialized storage versus valid T
MaybeUninit<T> can hold storage not yet containing a valid T. assume_init asserts
the obligation has been met; it does not initialize or validate the contents.
Zeroing is not sufficient for every type, notably references. Validity does not
require arbitrary padding bytes to be initialized. [3]

For native output buffers, trace which elements or fields were actually written
on each success/error path before assume_init or an equivalent typed read.
Dropping MaybeUninit does not automatically drop an initialized contained T.
Partial initialization can therefore require explicit cleanup of the completed
portion. Neither full capacity nor a non-null buffer proves valid initialized data.

## slice::from_raw_parts: element count, one allocation and borrow lifetime
The unsafe slice constructor takes a pointer and a count of T elements, not
bytes. The range must hold initialized T values in one allocation; total bytes
must not exceed isize::MAX or wrap the address space. Even an empty slice requires
a non-null, suitably aligned pointer. [4]

The resulting shared slice must not outlive its backing storage or permit
conflicting mutation, except through UnsafeCell. A foreign convention allowing
(NULL, 0) therefore needs explicit handling before constructing a Rust slice.
Adjacent allocations are not one permitted slice simply because their addresses
are consecutive. Trace real allocation extent, count conversion and lifetime,
not only the arithmetic endpoint.

## read_unaligned and packed fields: alignment relief has limits
ptr::read_unaligned permits an unaligned source, but still requires readable,
properly initialized T. It performs a bitwise copy even for a non-Copy type;
using both copies as owners can violate safety. [5]

If a packed field is not suitably aligned, taking &field and then casting to a
raw pointer first creates an invalid reference. Raw-address formation avoids that intermediate
reference; it does not establish bounds, initialization or ownership. Hardware
support for unaligned loads is not proof that a Rust reference was valid.
Track copied ownership-bearing values to their later use and destruction.

## from_utf8_unchecked: decoded bytes must satisfy the string contract
str::from_utf8_unchecked requires valid UTF-8 input; it does not check that
precondition. The safe from_utf8 alternative validates the byte sequence. [6]

For a recovered parser or malware configuration decoder, follow the exact output
bytes into the unchecked conversion. A prior check of a different buffer, a
prefix, or data before mutation does not establish validity of this slice.
Keep raw bytes and interpreted text distinct when reporting extracted indicators;
a successful extraction is not evidence that the program reached a network or
process-launch operation using them.

## Primary sources and scope
Reviewed 2026-10-02. Rust Reference and standard/core library pages identifying
Rust 1.99.0 supply the contracts. Exact unsettled aliasing details remain unsettled;
this document does not present a memory-model experiment as a language guarantee.
Use `reference-rust-layout-dispatch` for representations and
`reference-rust-ffi-boundaries` for native ownership transfer.

1. [Behavior considered undefined](https://doc.rust-lang.org/reference/behavior-considered-undefined.html): invalid values, pointers, races and aliasing qualifications.
2. [UnsafeCell](https://doc.rust-lang.org/std/cell/struct.UnsafeCell.html): interior mutation, mutable-reference uniqueness and synchronization.
3. [MaybeUninit](https://doc.rust-lang.org/core/mem/union.MaybeUninit.html): initialization, validity, padding and destruction.
4. [slice::from_raw_parts](https://doc.rust-lang.org/std/slice/fn.from_raw_parts.html): full safety contract and foreign empty buffers.
5. [ptr::read_unaligned](https://doc.rust-lang.org/std/ptr/fn.read_unaligned.html): packed fields and ownership-bearing copies.
6. [str::from_utf8_unchecked](https://doc.rust-lang.org/std/str/fn.from_utf8_unchecked.html): UTF-8 precondition.
