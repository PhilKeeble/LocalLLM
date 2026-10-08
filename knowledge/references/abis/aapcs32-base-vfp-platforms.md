---
id: abi-aapcs32-base-vfp-platforms
title: AAPCS32 base and VFP calling conventions, hidden results and platform differences
kind: reference
topics: [aapcs32, calling-conventions, hard-float, softfp, hidden-arguments, variadic]
platforms: [linux, android, windows, firmware]
architectures: [arm]
---
# AAPCS32 call-boundary evidence

## Identify the public interface variant
Reviewed 2026-10-02. AAPCS32 release 2025Q4 is the baseline here. Platform rules,
language lowering, function attributes and hand-written/private conventions can
change a particular interface. A32 versus Thumb selects decoding, not the
floating-point procedure-call variant. See `architecture-aarch32-thumb-state-decoding`.

For an indirect-call mismatch investigation, record the caller's actual argument
placement, the destination's actual consumption and the expected return channel.
Do not diagnose a bug from a decompiler prototype alone. Distinguish unavailable
metadata from demonstrated incompatibility; an interface shim can deliberately
translate conventions. These rules do not describe OS system-call entry.

## Core registers, stack and preservation
AAPCS32 uses r0-r3 then stack for base-PCS arguments. r4-r8, r10-r11 and SP are
preserved; r9 is platform-defined, r12 scratch. SP alignment is four bytes
generally and eight at public interfaces. [1]

Constructed check: an interior SP of 0x7ffc satisfies the four-byte constraint
but is not an eight-byte-aligned public call boundary. It is not sufficient to
label the whole function ABI-invalid from that one interior snapshot. Conversely,
an intact saved r11 does not prove every callee-preserved register was restored.
Track SP deltas and the actual return path, including exceptional exits. Do not
assume all targets reserve r9 for the same purpose or all functions maintain an
identical frame chain.

## Argument holes, split aggregates and hidden results
Base PCS eight-byte-aligned arguments start at even core registers. A suitable
aggregate can split across remaining registers and stack before earlier stack
allocation. Composite results larger than four bytes use caller storage via r0;
explicit arguments then start from r1. [1]

Constructed base-PCS C examples, with ordinary type layout and no hidden arguments:
f(int a, long long b, int c) uses r0 for a, skips r1, places b in r2/r3 and c on
the stack. The hole is not a missing argument. For g(int a, struct {int x,y,z;} b),
b fits r1-r3; after two int arguments, the same b can use r2/r3 plus one stack word.
For a function returning struct {int x,y;}, r0 can instead be the hidden output
address, not the first source-level input. Verify pointee extent and caller
allocation before treating callee stores through it as arbitrary writes.

## Return classification is not just the number of bytes
In base PCS, a word scalar returns in r0 and a doubleword scalar in r0/r1;
a composite of at most four bytes returns in r0. Larger composites use memory.
In the VFP variant, eligible FP/vector results use VFP registers instead. [1]

Constructed contrast: a 64-bit integer and struct {int x,y;} both occupy eight
bytes but have different base-PCS result channels. A prototype inferred only from
size can shift every explicit argument and misidentify the output buffer as input.
Check both sides of a call and downstream use. Register-pair byte significance
must match target data endianness; do not silently import a little-endian layout
into big-endian firmware. No general rule here permits reading aggregate padding
as a defined field value.

## VFP allocation, homogeneous aggregates and variadic exceptions
The AAPCS32 VFP variant allocates eligible arguments through s0-s15/d0-d7;
one-to-four-element homogeneous FP/vector aggregates can qualify. Exhausted
candidates go to stack, not automatically core registers. Variadic functions use
base PCS for arguments and return. d8-d15 are call-preserved. [1]

Constructed prototype check: under the VFP variant, a non-variadic function taking
one double can consume d0. Reinterpreting a variadic call as that signature can
invent an uninitialized d0 input when the real argument was supplied through the
base convention. Likewise, two floating members and one integer member are not
automatically a homogeneous FP aggregate. Recover layout and classification before
concluding that missing core-register loads mean missing arguments. Do not count
overlapping s/d register names as independent storage.

## GCC soft, softfp and hard describe different choices
GCC ARM -mfloat-abi=soft uses library calls for floating arithmetic; softfp permits
hardware arithmetic while retaining the soft-float call convention; hard uses
the FP-specific convention. The configured target determines the default. [2]

Investigation implication: a VADD or VMUL inside a function does not establish
that its callers pass doubles in d0/d1. Conversely, a helper call does not establish
that the whole object lacks hardware FP support. Separate ISA capability from
interface convention. Match object attributes, actual call sites and selected
libraries; suppressing a linker compatibility diagnostic is not evidence that
the two sides agree on register contents.

## Android armeabi-v7a and Windows ARM32 are not one float ABI
Android's documented armeabi-v7a uses softfp and ordinarily generates Thumb-2;
hardware floating arithmetic remains available. [3] Microsoft's Windows ARM32
ABI requires Thumb-2 code and uses VFP argument passing for eligible non-variadic
interfaces; variadic functions exclude VFP argument allocation. [4]

Constructed cross-platform analysis: a non-variadic double argument passed in
core registers by an Android binary is not evidence of a broken Windows-style
call. Apply the target platform's rule. Windows code pointers retain the Thumb
bit; hardware's ability to decode A32 is not proof that Windows supports running
it. These are ARM32 rules, not ARM64, old Windows CE, or every historical Android
toolchain. Inspect the binary's actual build/runtime contract when they differ.

## Standard FP helpers can have a different convention from surrounding code
RTABI32's specified floating-point helper functions use base-PCS core-register
arguments and results even when implemented with FP hardware. Tag_ABI_VFP_args
records interface intentions; a generic instruction-presence heuristic does not. [5]

Constructed investigation: a hard-float caller moves a double to core registers
before an __aeabi_* floating helper. Do not automatically label this as a corrupt
prototype or an integer reinterpretation bug. Identify the exact helper and
contract, including whether its return is an FP bit pattern, integer comparison
result or another helper-specific shape. A symbol-looking name alone is weaker
evidence than a matched runtime implementation and call sequence; custom symbols
can reuse familiar names.

## Primary sources and verification limits
Reviewed 2026-10-02. Examples are constructed ABI applications, not compiler
disassembly captures. Source revisions and public-interface scope must match the
target. No universal proprietary C++ object ABI or complete platform unwind model
is claimed by this reference.

1. [AAPCS32 release 2025Q4](https://github.com/ARM-software/abi-aa/blob/2025Q4/aapcs32/aapcs32.rst): core/VFP preservation, stack constraints, base result/parameter rules A.4/C.3-C.8 and VFP variant.
2. [GCC ARM options](https://gcc.gnu.org/onlinedocs/gcc/ARM-Options.html): -mfloat-abi, rolling documentation.
3. [Android NDK ABI guide](https://developer.android.com/ndk/guides/abis): armeabi-v7a, rolling documentation.
4. [Microsoft ARM32 ABI](https://learn.microsoft.com/en-us/cpp/build/overview-of-arm-abi-conventions?view=msvc-170): instruction set, VFP registers and parameter passing.
5. [RTABI32 release 2025Q4](https://github.com/ARM-software/abi-aa/blob/2025Q4/rtabi32/rtabi32.rst): floating-point helper convention and interface-intention attributes.
