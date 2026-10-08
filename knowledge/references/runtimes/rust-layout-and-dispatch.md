---
id: reference-rust-layout-dispatch
title: Rust binary layout, enums, trait objects and monomorphized dispatch
kind: reference
topics: [rust, repr, enums, option, vec, trait-objects, vtables, monomorphization, symbols]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Rust layout and dispatch evidence

## repr(Rust): field order is not a portable structure layout
Rust's default representation guarantees suitable field alignment and no overlap
of nonzero-sized fields, but not declaration-order offsets. Zero-sized fields can
share addresses. A type's layout alone does not determine its function-call ABI
(argument/return convention). [1]

Recover offsets from actual accesses and matching type evidence. Do not copy
another build's structure layout into the specimen solely because type names
match. An apparently missing field can be zero-sized or optimized away; neither
observation proves obfuscation. Keep inferred layout separate from language rules.

## repr(C) and repr(transparent): representation has a limited scope
repr(C) gives a structure C-style field ordering and target-dependent padding.
It does not change the representation of a nested repr(Rust) field.
repr(transparent) allows any number of size-zero, alignment-one fields and at
most one other field. The wrapper has that other field's layout and ABI, or
unit's if there is no such field. [1]

For native calls, establish both aggregate representation and calling convention.
repr(C) on an object does not make every method an extern "C" function or make
Rust-owned pointers safe for arbitrary foreign deallocation. See
`reference-rust-ffi-boundaries` for separate ownership and ABI obligations.

## Rust enums: logical discriminant versus stored tag
An enum value selects one variant. Its discriminant is the logical integer used
to distinguish variants; default representation need not store that integer in
an isize field, or even use a separate tag. [2] A repr(C) fieldless enum still
permits only declared discriminants, unlike a C enum used for arbitrary integers
or flags. [1]

Trace construction and discriminating branches before naming tag/payload fields.
A decompiler's pointer test may select a variant rather than validate an ordinary
nullable pointer. For vulnerability analysis, identify how invalid input could
become a typed enum value; an unknown integer in a raw input buffer is not yet
an invalid enum value in use.

## Option niches: None can reuse an otherwise invalid representation
A niche is an otherwise invalid representation reused to distinguish an enum
variant. The standard library guarantees Option<T> has T's size, alignment and
call ABI for specified types, including references to sized pointees, function pointers,
NonZero integers, NonNull with a sized pointee and Box with a sized pointee and
the global allocator. Qualifying transparent wrappers inherit the guarantee. [3]

For those listed sized-pointee, function-pointer and NonZero cases, an all-zero
representation denotes None; a transparent wrapper inherits this when its inner
type does. This is not a rule for all Option<T>, raw pointers or Result<T,E>.
Converting None into T is not justified by equal sizes.
Recover which variant reaches a dereference or destructor, not just the bytes
shared by an enum and its payload.

## Vec<T>: pointer, capacity, initialized length and no fixed field order
For the default allocator, Vec<T> consists of a non-null pointer, capacity and
length, but their field order is unspecified. Length counts initialized elements;
spare capacity is logically uninitialized T storage. Zero capacity or zero-sized elements
can mean no allocation despite a non-null pointer. [4]

In a decompiler, distinguish element count from byte size and allocation capacity
from readable length. Infer roles from bounds checks, allocation and writes,
not a universal three-word offset template. Vec::set_len requires the new length
to fit capacity and newly included elements to be initialized; it does not
initialize them. A native output count trusted by set_len is a useful audit edge.

## dyn Trait objects: data pointer, vtable and indirect methods
A trait object erases the concrete implementing type behind a pointer such as
&dyn Trait or Box<dyn Trait>. Its pointer carries the instance pointer and a
virtual method table used for indirect dispatch. [5] A vtable is a table of
implementation addresses, not the application object itself.

Recover the selected method, concrete data argument and ownership together.
Do not assign universal vtable slot offsets from another compiler build.
A borrowed &dyn Trait and an owning Box<dyn Trait> do not confer identical
destruction rights. A method-table call is normal language infrastructure;
its arguments, reachable implementation and effect establish the behavior.

## Monomorphization: generic code specialized for concrete types
rustc monomorphization creates specialized code for concrete generic type uses. [6]
Investigation inference: related functions can be ordinary specializations rather
than duplicated malicious logic. Different type arguments can change element
widths, called methods and required cleanup.

Specialization does not promise one distinct final machine-code body per source
instantiation: inlining and other optimizer/linker transformations still apply.
Identify the executed body and operations. A generic function name alone does
not establish the vulnerable type combination or a reachable input path. Shared
compiler transformations: `reference-native-compiler-transformations`.

## Rust symbols: attribution clues, not ABI or malicious intent
rustc symbol mangling encodes names according to the selected scheme. no_mangle
can suppress mangling; export_name can supply a chosen exported spelling. [7]
An unmangled name therefore does not by itself prove a C calling convention.

Preserve raw and demangled names; correlate them with instructions and call sites.
Names can help separate runtime/library helpers from application dispatch, but
stripping or absent recognizable names does not rule out Rust. Shared crate code
does not identify a malware operator, and a Rust attribution does not establish
memory safety of native dependencies or correctness of authorization logic.

## Primary sources and scope
Reviewed 2026-10-02. Living Rust Reference/rustc documentation and standard-library
pages identifying Rust 1.99.0 were inspected. These are broadly useful contracts,
not a claim that the specimen was built with that release. Private layouts require
target evidence. No compiler specimen was built or executed.

1. [Rust type layout](https://doc.rust-lang.org/reference/type-layout.html): Rust, C and transparent representations; layout versus ABI.
2. [Rust enumerations](https://doc.rust-lang.org/reference/items/enumerations.html): logical discriminants and representation freedom.
3. [Option representation](https://doc.rust-lang.org/std/option/index.html#representation): enumerated niche guarantees and invalid conversions.
4. [Vec guarantees and set_len](https://doc.rust-lang.org/std/vec/struct.Vec.html): initialized extent, allocation caveats and field-order limits.
5. [Trait objects](https://doc.rust-lang.org/reference/types/trait-object.html): instance and vtable dispatch.
6. [rustc monomorphization](https://rustc-dev-guide.rust-lang.org/backend/monomorph.html): specialization as compiler implementation.
7. [rustc symbol mangling](https://doc.rust-lang.org/rustc/symbol-mangling/index.html): mangling controls and export names.
