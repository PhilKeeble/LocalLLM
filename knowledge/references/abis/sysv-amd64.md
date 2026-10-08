---
id: abi-sysv-amd64
title: System V AMD64 argument classes, red zone and aggregate returns
kind: reference
topics: [abi, sysv, amd64, calling-convention, red-zone, aggregates, varargs]
platforms: [linux, freebsd]
architectures: [x64]
---
# System V AMD64 ABI

## System V AMD64 scope

Use for ordinary System V AMD64 user-space interfaces after verifying the
target ABI. This is not Windows x64 or the Linux kernel syscall convention.
The core rules below concern LP64 and baseline scalar/aggregate calls, not
every vector extension or private compiler convention. [1]

## System V AMD64 compact argument and result rules

INTEGER arguments use RDI, RSI, RDX, RCX, R8, R9; SSE arguments use XMM0..XMM7
with independent allocation. An eightbyte is an eight-byte classification unit,
not necessarily one source field or one whole object. Aggregate eightbytes are
classified; unaligned members or classification rules can force memory passing. Register exhaustion
reverts an aggregate's partial assignments and puts the whole argument on the
stack. Nontrivial C++ call objects can instead use invisible references. [1]

INTEGER results use RAX then RDX; SSE results XMM0 then XMM1. MEMORY results use
caller storage supplied in RDI, with its address returned in RAX. For varargs,
AL supplies an upper bound from 0..8 on vector-register usage, not an argument
count. Narrow integer excess bits are unspecified. [1]

## System V AMD64 stack and preservation

Before an ordinary call the stack is at least 16-byte aligned; at callee entry
`RSP+8` has that alignment. Stacked over-aligned/vector arguments can require
more. There is no mandatory Windows shadow space. The user-space red zone is
128 bytes below RSP, usable for temporaries not live across calls. Do not apply
it to kernel/interrupt code. RBX, RBP, R12..R15 and RSP are preserved; vector
registers are call-clobbered. [1]

## Constructed System V mixed-argument example

Hypothetical declaration: `f(void *p, double x, unsigned n, double y)`.
Under the ordinary System V AMD64 rules, observe p in RDI, x in XMM0, n in ESI
and y in XMM1. The two register sequences progress independently. A Windows
x64 interpretation would instead assign shared argument positions and produce
a different data-flow reconstruction.

Investigation: establish the prototype at both sides; mark each consumed width;
follow a narrow argument through extension before treating it as a size. The
register holding a bit pattern does not establish that the source type was
signed, unsigned, pointer or enumeration.

## Constructed System V aggregate investigation

For a hypothetical naturally aligned trivial C structure with two `uint64_t`
fields, consider two INTEGER eightbytes. If only one integer argument register
remains, look for the entire object in stack argument storage, not one field in
a register plus one field on the stack. Recover stack alignment and the other
arguments before calculating offsets. This example is not a general rule that
every 16-byte object has the same classification.

If a returned object appears to be an input pointer, test the hidden-result
hypothesis: caller allocates storage, callee initializes it, caller consumes it
after return. A correct mapping prevents a false report of a missing bounds
check on what is actually an internally supplied result object.

## System V AMD64 aggregate classification detail

For ordinary trivial aggregates/unions, classify rounded eightbytes recursively.
Over 64 bytes or unaligned fields force MEMORY. Scalars: integers/pointers→INTEGER;
float/double→SSE; __int128→two INTEGER; long double→X87/X87UP;
__m128→SSE/SSEUP. SSEUP continues the preceding vector register. [1]

Merge order: equal classes stay; NO_CLASS yields the other; MEMORY dominates;
then INTEGER dominates; remaining x87 mixtures become MEMORY; otherwise SSE.
Cleanup: any MEMORY or orphan X87UP forces memory; over two eightbytes requires
SSE followed entirely by SSEUP; orphan SSEUP becomes SSE. Vector-extension
support still matters. x87-class arguments go on stack; long-double results use
ST0, complex-long-double results ST0/ST1. [1]

Constructed naturally aligned trivial record {double d; uint64_t n;} therefore
uses one SSE and one INTEGER class, not two floating registers. Classification
is by layout and fields, not aggregate size alone.

## System V AMD64 va_list recovery

The baseline va_list is a one-element array containing gp_offset, fp_offset,
overflow_arg_area and reg_save_area. GP saves occupy offsets 0..40 in 8-byte
steps; XMM saves 48..160 in 16-byte steps. Exhaustion offsets are 48 and 176.
va_arg selects available register classes or aligned stack storage; save areas
may omit unused registers. [1] A contiguous stack-only varargs reconstruction
can therefore invent missing arguments. Named and unnamed arguments share
register allocation; AL is not the number of unnamed arguments.

## Evidence limits and source

Reviewed 2026-10-02. Specification-derived examples; no particular target was
executed. Packed objects, unions, vectors, x87 types, x32 and compiler-specific
interfaces require their full classification and data-model rules. Do not
guess a prototype from one call or assume all ELF files use this ABI.

1. [x86-64 psABI, low-level system information](https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex): Registers, Stack Frame, Parameter Passing, Classification and Returning of Values; living source inspected on the review date.

Related: `abi-windows-x64` for Windows distinctions; `reference-native-integer-size-buffer-arithmetic`
for size-flow analysis after argument recovery.
