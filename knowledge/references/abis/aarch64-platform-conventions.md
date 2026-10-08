---
id: abi-aarch64-platform-conventions
title: AArch64 AAPCS64, Apple ARM64 and Windows ARM64 calling-convention differences
kind: reference
topics: [abi, aapcs64, aarch64, arm64, calling-convention, varargs, hidden-return]
platforms: [linux, android, windows, macos, ios]
architectures: [arm64]
---
# AArch64 calling-convention selection

## AAPCS64 baseline registers and stack

For baseline hard-float AAPCS64, integer/pointer arguments draw from X0..X7
and floating/SIMD arguments from V0..V7. X19..X29 and SP are preserved; X16/X17
can be clobbered by call veneers. X18 is platform-defined. Only the low 64 bits
of V8..V15 are preserved under the baseline convention. SP is 16-byte aligned
at public interfaces and when used for memory accesses. [1]

This is an ABI rule, not proof of a private function's prototype. AArch64 SVE,
SME, soft-float and platform-specific conventions need additional rules.

## AAPCS64 aggregates and indirect results

After applicable language-ABI transformations, baseline AAPCS64 treats homogeneous floating/vector aggregates specially;
other composites above 16 bytes are passed indirectly. Required registers,
alignment and available register counts affect smaller aggregates. A result
not returnable in the prescribed registers uses caller storage addressed by
X8. Unused argument bits are unspecified; named narrow integers are interpreted
at their declared width. [1]

Constructed investigation: before labeling X0 as a destination buffer, inspect
X8 and stores through it. A caller-owned return object can coexist with an
ordinary first input in X0. Check the platform's C++ return rules before applying
this reasoning to all class types.

## AAPCS64 homogeneous aggregates and register exhaustion

For ABI-eligible trivial aggregates in baseline hard-float AAPCS64, a homogeneous
floating-point aggregate (HFA) or homogeneous short-vector aggregate (HVA) has at
most four uniquely addressable members of the same ABI fundamental type, assessed
after layout. For short vectors, homogeneity distinguishes 64-bit from 128-bit
vectors but ignores their lane element types. One V register holds each member
if enough remain; otherwise the whole aggregate is stacked and
that register sequence is exhausted. HFA/HVA classification precedes the
ordinary over-16-byte indirect rule. [1]

Constructed trivial record {double a,b,c,d;} can use D0..D3 despite its 32-byte
size. A mixed record is not an HFA merely because its size matches.
Ordinary small composites use consecutive X registers if all fit; otherwise
the whole composite goes on the aligned stack, not split across X7 and memory.
Generic 16-byte argument alignment can skip an odd X register. [1]

## Generic AAPCS64 variable-argument state

Generic AAPCS64 va_list contains __stack, __gr_top, __vr_top, __gr_offs and
__vr_offs. Signed negative offsets address remaining saved registers below
the corresponding top; GP slots advance by 8 bytes, SIMD slots by 16.
Exhaustion selects aligned stack storage. HFA reconstruction may gather members
from separate SIMD-save slots. [1]

This is not Apple's stack-oriented va_list or Windows ARM64's variadic scheme.
Misreading a negative save-area offset as an unsigned buffer length can invent
a bounds defect. Confirm ABI selection before naming fields.

## Apple ARM64 differences

On Apple's ARM64 ABI, X18 is reserved. `long` and pointers are 64-bit; `wchar_t`
is signed 32-bit and `long double` has double precision. For named arguments
smaller than 32 bits the caller performs the documented sign/zero extension to
32 bits. Stack arguments need not each consume eight bytes. Apple also relaxes
the generic even-register requirement for a 16-byte aligned integer argument. [2]

Apple ARM64 unnamed variadic arguments are placed in stack slots after normal
processing of named arguments; `va_list` differs from generic AAPCS64. Apple's
128-byte red zone below SP is a platform contract, not a general AArch64 fact.
Do not preserve live values there across calls that may use it. [2]

Investigation: recover whether a call is variadic before using floating argument
registers to infer the payload. A copied generic Linux AAPCS64 prototype can
misidentify Apple arguments without any defect in the target.

## Apple ARM64 stack packing and variadic boundary

Apple named stack arguments can use only their required size/alignment instead
of one eight-byte slot each. Unnamed variadic arguments instead use the documented
eight-byte-slot scheme, after named-argument processing. Apple va_list is a char
pointer rather than generic AAPCS64's register-save descriptor. [2]

Constructed investigation: adjacent small named stack fields do not establish
the spacing of unnamed arguments in the same call. Identify the ellipsis boundary
and default argument promotions before computing a va_arg load address; promoted
float is not still a four-byte unnamed float. A function consuming a va_list
receives already constructed argument state, not necessarily the original
caller registers.

## Windows ARM64 differences

Windows ARM64 uses LLP64 widths and reserves X18 for platform use. For variadic
calls, SIMD/FP registers are not argument carriers; allocation follows the
Windows general-register/stack scheme, without HFA/HVA special treatment. [3]

Windows ARM64 result storage is not universally in X8. Qualifying ordinary
aggregate returns use AAPCS-style registers or X8 storage. Other C++ return
types use a hidden pointer in X0, or X1 when `this` occupies X0, and return that
pointer in X0. Establish type eligibility and member status from both caller
and callee. [3]

Constructed investigation: an apparent extra pointer in X1 at a Windows member
call may be result storage. Track writes and the caller's post-call use before
declaring an extra attacker-controlled argument. ARM64EC is a separate ABI;
these rules are for ordinary Windows ARM64.

Use `abi-windows-arm64ec-boundaries` for EC signature thunks, saved-context
mapping, register restrictions and its four-register variadic convention.

## Windows ARM64 variadic allocation model

Windows ARM64 describes variadic allocation as an imaginary argument stack whose
first 64 bytes feed X0..X7; remaining arguments are actually stacked. HFA/HVA
special treatment and SIMD argument registers are disabled for such calls. [3]
Do not confuse this conceptual allocation with a mandatory caller-populated
64-byte memory home area or with Windows x64's 32-byte shadow space.

Constructed example: a variadic double can be carried as bits in a general
register even though the same named type in a nonvariadic function uses a V
register. Establish whether the function itself is variadic, not only whether
one observed argument happens to follow an ellipsis in guessed pseudocode.

## Cross-platform ABI evidence record

For an AArch64 call record: object format, target OS, ABI variant, compiler if
known, named/variadic boundary, widths, aggregate layout, hidden arguments and
the exact stop relative to the call. Check register values before clobbering
instructions and account for the link register and prologue changes.

Useful disconfirmation: a pointer inferred from a decompiler is not consumed
as a pointer in instructions; a supposed missing argument is delivered through
hidden result storage; or the decoder applied another platform's variadic ABI.
Resolve the ABI mismatch before evaluating a vulnerability hypothesis.

## Sources and scope

Reviewed 2026-10-02. Specification/documentation checks, not runtime validation.

1. [Arm AAPCS64, 2025Q4](https://github.com/ARM-software/abi-aa/blob/2025Q4/aapcs64/aapcs64.rst): sections 6.1, 6.4, 6.8 and 6.9. Baseline rules only; extensions have separate interfaces.
2. [Apple ARM64 ABI](https://developer.apple.com/documentation/xcode/writing-arm64-code-for-apple-platforms): register roles, types, red zone, argument and variadic differences.
3. [Windows ARM64 ABI](https://learn.microsoft.com/en-us/cpp/build/arm64-windows-abi-conventions?view=msvc-170): parameter passing, variadic addendum and return values.

Related: `abi-windows-x64` and `abi-sysv-amd64` are different instruction-set
interfaces, not substitute ARM64 argument maps.
