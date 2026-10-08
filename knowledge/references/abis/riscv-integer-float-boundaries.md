---
id: abi-riscv-integer-float-boundaries
title: RISC-V integer and floating-point ABI arguments, returns, stack and variants
kind: reference
topics: [riscv, calling-conventions, variadic, aggregates, register-preservation]
platforms: [linux, firmware]
architectures: [riscv32, riscv64]
---
# RISC-V call-boundary evidence

## ABI names and ISA capability answer different questions
Reviewed 2026-10-02. The inspected psABI is version 1.1, September 24, 2026
pre-release, with individual ABI statuses distinguished. The standard ILP32/LP64
families below must not be applied automatically to E variants, experimental
RV64ILP32, private conventions or big-endian targets. [1]

GCC -march selects instructions; -mabi selects data/calling convention. RV64IFD
can use LP64, LP64F or LP64D: hardware double arithmetic does not require double
arguments in FP registers. LP64 uses no FP argument registers; LP64F's FP argument
width is at most 32, LP64D's at most 64. Defaults are target-dependent. [2]
Confirm the caller/callee contract before treating register placement as corrupt.

## Integer register roles and stack extent
Standard integer PCS uses a0-a7 (x10-x17) for arguments and a0-a1 for returns;
s0-s11 are preserved. sp=x2 is preserved, ra=x1 is not; gp=x3 and tp=x4 are
fixed/unallocatable under the standard contract. A frame pointer, if used, is s0.
Standard SP alignment is 16 bytes throughout execution; data below SP is not a
persistent red zone. [1]

Constructed investigation: a leaf keeps a temporary below SP, then calls an
unknown routine. Do not justify its lifetime using the SysV AMD64 red-zone rule.
An absent s0 frame chain does not prove a malformed function; a0 after a call
cannot be assumed to retain an input just because the decompiler omitted a return.
Record the actual stack allocation and preservation path, not a familiar prologue.

## RV64 narrow integer arguments can have upper ones without being signed
For ordinary integer scalars narrower than XLEN, the psABI widens according to
type up to 32 bits, then sign-extends to XLEN. This is a boundary representation
rule, not a declaration that every value is signed. [1]

Constructed RV64 unsigned int argument 0x80000000 is represented as
0xffffffff80000000. Treating the register as unsigned long changes the value;
recovering unsigned int then converting to unsigned long must preserve the
32-bit value instead. Compare caller setup, callee truncation and downstream
use before reporting a negative length. Do not use this ordinary-scalar rule as
a blanket description of aggregate padding or every _BitInt variant.

## Split arguments and indirect return storage
In integer PCS, ordinary scalars/aggregates up to two XLEN words can use two
argument registers; with one left, the remainder can be on stack. Larger or
qualifying nontrivial C++ aggregates pass indirectly. An indirect result uses
an implicit first pointer; the callee need not return that pointer in a0. [1]

Constructed RV32 case: seven int arguments consume a0-a6; a final named
64-bit scalar uses a7 for its low word and the stack for its high word. Do not
invent a second scalar from the stack half. For an indirect result, an a0 value
different from the original buffer on return does not alone prove corruption.
Check stores to caller-owned result memory and the actual language classification,
including nontrivial C++ cases that override a simple size heuristic.

## Variadic alignment can leave an argument register unused
Unnamed variadic values needing 2*XLEN alignment and no more than two words use
an even-numbered argument-register pair or stack. Once a variadic value goes to
stack, subsequent variadic values also go there. [1]

Constructed RV32 call: seven named int arguments occupy a0-a6; the next unnamed
eight-byte-aligned long long cannot start at odd a7 and goes to stack. A following
unnamed int also stays on stack. The unused a7 is not evidence of a missing
argument. This differs from a final named scalar split between a7 and stack.
Recover named-versus-unnamed positions and language default promotions before
interpreting a va_list walk or diagnosing an overread.

## Hardware FP convention still has integer and variadic paths
Hardware FP PCS adds fa0-fa7 for eligible named arguments. ABI_FLEN may be smaller
than the hardware register width. Variadic values use integer PCS. Certain mixed
FP/integer structs can split between FP and integer registers; unions do not
receive struct flattening. [1]

Constructed LP64D function with one named double and an unnamed double: the
named value can use fa0, but treating the variadic value as the next fa register
misreads the contract. FP instructions in the body do not settle this question.
Check allocation availability and exact aggregate shape rather than copying an
AArch64 homogeneous-aggregate rule. Register preservation also follows ABI_FLEN,
not simply the widest value the hardware can hold.

## Reduced-register and vector conventions need explicit evidence
The inspected psABI's ILP32E description has six argument registers, a0-a5,
two preserved s registers and four-byte stack alignment; it is marked draft.
The standard vector convention does not pass ordinary arguments in vector
registers; an explicitly selected vector variant has different allocation and
preservation rules. [1]

Do not generalize eight argument registers or 16-byte alignment to every E
firmware image, or infer vector argument passing from vector arithmetic alone.
Match the toolchain version and any variant-CC marking. The psABI's syscall
chapter explicitly delegates service entry to the execution environment; an
ECALL interface is not defined by the ordinary procedure-call register table.

## Sources and limits
Reviewed 2026-10-02. Constructed cases apply selected documented rules; they are
not compiler output or target executions. The psABI page is a dated development
document, not a claim that every section or experimental ABI is ratified.

1. [RISC-V psABI](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/): version 1.1, September 24, 2026-draft, sections 1-3 and ABI status table. Core/integer/FP/variadic and variant distinctions inspected.
2. [GCC RISC-V options](https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html): -march/-mabi and E-ABI caveats, rolling manual.
