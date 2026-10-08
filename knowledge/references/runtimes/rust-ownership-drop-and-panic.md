---
id: reference-rust-ownership-drop-panic
title: Rust ownership moves, drop cleanup, partial initialization and panic handling
kind: reference
topics: [rust, ownership, drop, destructors, partial-initialization, manuallydrop, panic, unwind]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Rust ownership and cleanup evidence

## Moves and partial initialization: which value still needs Drop?
Rust destruction applies to initialized values. After a partial move, only the
remaining initialized fields need destruction. For a type implementing Drop,
destruction calls Drop::drop and then recursively destroys its fields. [1]
Compiler-generated recursive cleanup is often called drop glue.

Track ownership by path: creation, move, use and final destruction. A copied
pointer-shaped word in machine code does not establish two independent owners.
Conversely, an unsafe ownership reconstruction can create competing owners even
without a visible source-level clone. Multiple cleanup sites are not a double
free unless a feasible path destroys the same owned resource twice.

## Drop flags: conditional cleanup is not a universal hidden object field
Conditional initialization can require a logical flag recording whether a value
needs destruction. Statically known initialization states can eliminate that
runtime test. [2] The flag is a compiler bookkeeping mechanism, not a guaranteed
field at a fixed offset in every Rust object.

Constructed investigation: a failed constructor initializes field A but not B;
its error path cleans up A only. A later success path cleans up both. Preserve
the branch and initialization state before treating missing cleanup as a leak or
two cleanup blocks as duplicate destruction. Use target control flow to identify
the actual flag and update order when a flag remains.

## Drop order: structure fields differ from local variables
Rust structure fields and fields of the active enum variant are destroyed in
declaration order; array elements are destroyed first to last. In a drop scope,
local variables are destroyed in reverse declaration order, and temporaries in
reverse creation order. Closure capture destruction order is unspecified. [1]
Do not extend array order to Vec: Vec does not guarantee element drop order. [6]

Do not substitute physical field order for declaration order under repr(Rust),
or apply the local-variable rule to fields. Investigate callbacks and resource
dependencies during each destructor. A still-addressable allocation does not
prove every field remains live. Cleanup is also not an automatic reversal of
earlier file, network or authorization-state changes.

## mem::forget: safe code need not run every destructor
mem::forget consumes a value without invoking its destructor. Rust memory safety
does not require every destructor to run; forgotten values and reference cycles
can leak resources. Unsafe abstractions must account for safe callers being able
to suppress destruction. [3]

Do not infer a missing drop is necessarily corrupt control flow, or assume a
destructor will always perform a safety-critical revocation. A leak can still
matter for availability or resource policy. Establish repeatable input control,
resource retention and the relevant limit before claiming denial of service.
Forgetting a value does not itself validate every previously derived pointer.

## ManuallyDrop suppresses cleanup, not type validity or access rules
ManuallyDrop<T> inhibits automatic destruction while retaining T's layout and
valid-bit requirements. It is not storage for arbitrary uninitialized bytes.
For example, zero is still invalid for a reference inside ManuallyDrop. [4]

After manually dropping the contained value, do not expose it through a safe API
that reads it as live T; derived formatting or cloning can also read that field.
Track whether a manual drop or take already consumed the value. For uninitialized
storage use the separate MaybeUninit contract in `reference-rust-unsafe-memory`.
Do not generalize historical ManuallyDrop/Box move restrictions across releases.

## catch_unwind catches unwinding Rust panics, not process abortion
std::panic::catch_unwind returns Ok for normal completion and Err for a caught
unwinding panic. It cannot catch a panic configured to abort. A panic hook runs
before the panic is caught, and dropping an Err payload can itself panic. [5]

For an input-triggered panic, identify the build's panic strategy, catch boundary
and subsequent control flow. A panic-related string or imported helper alone
does not prove termination. A caught panic can leave earlier external effects
intact: returning an error is not proof of transactional rollback or authorization
state repair. Review what the caller does after the catch.

## Foreign exceptions are not portable catch_unwind errors
For a foreign exception reaching catch_unwind through an otherwise permitted
unwind path, its API documents an unspecified choice: abort after running the
closure's and its callees' destructors, or return Err with an opaque payload. [5]
Do not rely on it as a portable C++ exception-to-Rust error translator.

Whether the exception may cross the call boundary is a separate ABI question;
see `reference-rust-ffi-boundaries`. A panic catch cannot repair an already
violated pointer, aliasing or lifetime contract. Distinguish a recoverable domain
error, an unwinding panic, process abortion and undefined behavior.

## Primary sources and scope
Reviewed 2026-10-02 against the Rust Reference, Nomicon drop-flags explanation
and standard-library pages identifying Rust 1.99.0. Cleanup patterns in machine
code depend on the compiler and optimization. Scenarios above are constructed,
not target observations.

1. [Rust destructors](https://doc.rust-lang.org/reference/destructors.html): recursive destruction, partial initialization and scope order.
2. [Nomicon drop flags](https://doc.rust-lang.org/nomicon/drop-flags.html): conditional versus statically determined cleanup.
3. [mem::forget](https://doc.rust-lang.org/std/mem/fn.forget.html): destructor suppression and unsafe abstraction obligations.
4. [ManuallyDrop](https://doc.rust-lang.org/std/mem/struct.ManuallyDrop.html): validity and accessing already-dropped contents.
5. [catch_unwind](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html): aborting panics, hooks, payloads and foreign-unwind limits.
6. [Vec guarantees](https://doc.rust-lang.org/std/vec/struct.Vec.html#guarantees): no guaranteed element destruction order.
