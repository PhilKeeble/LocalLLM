---
id: abi-mips-o32-n32-n64-evidence
title: MIPS o32, n32 and n64 argument, stack, gp and relocation evidence
kind: reference
topics: [mips, calling-conventions, data-models, global-pointer, relocations]
platforms: [linux, irix, firmware]
architectures: [mips]
---
# Selected MIPS ABI evidence

## n32 is not o32 and does not imply eight-byte pointers
Reviewed 2026-10-02. The SGI MIPSpro n32 handbook distinguishes o32 and n32
ILP32 from n64 LP64. n32 uses 64-bit registers with 32-bit pointers. [1]
GCC has separate o32/n32/n64/EABI and floating-register variants. [2]

Investigation inference: seeing doubleword register saves does not establish
eight-byte pointer fields in an n32 object. Recover data widths from the selected
ABI and actual accesses. These references describe the System V/SGI families;
they are not a default convention for every bare-metal image, RTOS, EABI or
private helper. Hard/soft-float and register-width variants need their own match.

## Argument count and extension can change the recovered prototype
The inspected SGI conventions allow o32 integer arguments in $4-$7, versus
$4-$11 for n32/n64. In n32/n64, ordinary 32-bit int arguments are sign-extended
in registers even when unsigned. Variadic FP values use the integer argument
path rather than the normal named-FP path. [1]

Constructed unsigned int 0x80000000 can therefore appear as
0xffffffff80000000 at an n32 call. Upper ones do not by themselves prove a
negative source length. Treating $8 as always an o32 temporary can also lose
an n32 argument. Decode argument positions, named-versus-variadic status and
use widths before reporting an uninitialized parameter or signedness defect.
The register ranges are allocation resources, not a rule that every aggregate
or FP value occupies exactly one integer register.

## o32 caller argument area and n32 stack slots have different contracts
The System V MIPS supplement requires eight-byte stack-frame alignment and a
non-leaf outgoing argument area of at least four words, even for fewer arguments.
[3] SGI n32 uses 16-byte stack alignment and eight-byte parameter slots. [1]

Constructed o32 caller reserving 16 outgoing bytes for a one-argument call has
not thereby created four actual arguments. Conversely, an n32 four-byte int in
an eight-byte slot does not prove an eight-byte source integer. Distinguish frame
extent, slot extent and live object width before declaring an overread. The SGI
handbook's summary table says 16 for o32 too, conflicting with its own detailed
text and the o32 supplement; use the latter's explicit eight-byte o32 contract,
not that inconsistent summary row.

## gp and t9 can be linkage context, not application state
For the inspected System V o32 PIC convention, callers place the callee address
in t9/$25; the callee uses linkage context to establish gp for its GOT. gp is
caller-saved across such calls. [3] SGI's n32/n64 convention instead makes gp
callee-saved. [1]

Investigation inference: a gp-relative load is not necessarily a structure field
of a hidden object parameter. Establish the applicable GOT base before resolving
its address. An o32 caller's gp reload after a call is not automatically recovery
from corruption; omitting it from a decompiler model can fabricate bad accesses.
Do not apply that preservation rule to n32/n64, or assume a t9 value is a user
callback without checking the ordinary PIC call sequence and relocation.

## HI16 and LO16 address construction includes a signed-low correction
The inspected MIPS ELF HI16 relocation accounts for the signed low half used
with its paired LO16; simply concatenating unadjusted halves can be wrong. [3]

Constructed 32-bit target 0x12348000 with a signed-low add needs upper 0x1235
and low -0x8000: 0x12350000-0x8000=0x12348000. Using upper 0x1234 with that
same signed low yields 0x12338000. Record symbol, addend, relocation kind and
the consuming operation before labeling a recovered address out of range.
This example is not a generic formula for GOT, gp-relative or all MIPS64
relocations. An OR-immediate consumer and a signed-add consumer must not be
silently assigned identical immediate-combination semantics.

## Sources and limits
Reviewed 2026-10-02. Original factual synthesis, not imported book text.
Constructed examples have no claimed target compilation, linking or execution.

1. [SGI MIPSpro N32 ABI Handbook, 007-2816-003](https://www.infania.net/misc1/sgi_techpubs/techpubs/007-2816-003.pdf): chapters 1-3, printed pp. 2, 5-8, 13 and 20-21; mirrored primary handbook. Detailed o32 alignment and summary-table discrepancy distinguished.
2. [GCC 15.1 MIPS options](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/MIPS-Options.html): ABI and FP variants; source is not proof of a target's selected options.
3. [System V MIPS ABI supplement](https://refspecs.linuxfoundation.org/elf/mipsabi.pdf): stack pp. 3-15/3-16, PIC pp. 3-38/3-42, relocation table p. 4-19. Historical o32 scope, not a blanket modern MIPS contract.
