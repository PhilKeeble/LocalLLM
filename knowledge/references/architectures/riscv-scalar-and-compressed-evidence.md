---
id: architecture-riscv-scalar-compressed-evidence
title: RISC-V RV32 and RV64 scalar operations, compressed decoding and control flow
kind: reference
topics: [riscv, instruction-semantics, compressed-instructions, signedness, control-flow]
platforms: [linux, firmware]
architectures: [riscv32, riscv64]
---
# RISC-V instruction evidence

## Fix XLEN, extensions and execution environment first
Reviewed 2026-10-02. RV32I and RV64I have 32- and 64-bit integer registers
respectively; XLEN names that integer-register width in bits. The E variants
have a reduced register set. This reference covers
selected I/C/M/A rules, not arbitrary vendor extensions. Instruction width is
not register width. See `abi-riscv-integer-float-boundaries` for call contracts
and `format-riscv-relocation-relaxation` for linked address recovery.

Record the target ISA string, supported extensions, privilege environment, data
endianness, loaded image and actual instruction bytes. File declarations and
reachable instructions are different evidence. A decoder accepting a mnemonic
does not establish that the processor supports it or that the bytes are code.
Examples below are constructed, not observed target failures.

## RV64 word results sign-extend instead of clearing the upper half
RV64 ADDIW/ADDW and word shifts calculate a 32-bit result and sign-extend it.
LW sign-extends a loaded word; LWU zero-extends it. LD loads 64 bits. [1]

Constructed value 0x80000000: LW or ADDIW with zero immediate produces
0xffffffff80000000, whereas LWU produces 0x0000000080000000. This differs from
the x86-64 EAX-write rule. The upper ones do not establish that the source object
was signed: RV64's documented 32-bit register convention also sign-extends
unsigned 32-bit values. Check the later operation's width and comparison, not
just a decompiler cast. Truncating to 32 bits makes these examples equal; a
64-bit address calculation need not.

## Arithmetic does not produce x86-style condition flags
RISC-V base branches compare register values directly: BLT/BGE are signed,
BLTU/BGEU unsigned, and BEQ/BNE compare equality. ADD/SUB retain low XLEN bits
on overflow. Base control transfers have no architectural delay slot. [2]

Constructed RV32 pair 0xffffffff and 1: BLT sees -1<1, while BLTU sees
4294967295<1 as false. Do not invent an overflow flag or borrow flag for a later
branch; trace the actual compared registers and any SLT/SLTU result. Likewise,
an instruction following an unconditional jump is not automatically executed
as a delay slot. Machine wraparound does not establish defined signed-overflow
behavior in a reconstructed C expression.

## Register shift counts and word-result widths
RV64 SLL/SRL/SRA use six count bits; SLLW/SRLW/SRAW use five and sign-extend
their word result. RV32 register shifts use five count bits. Immediate encodings
have separate legality constraints. [1][2]

Constructed RV64 source=1, register count=32: SLL produces 0x100000000, whereas
SLLW uses count zero and produces 1. A source-level shift by 32 on a 32-bit
operand is not made defined by this machine rule. Identify whether the count
was checked before masking, whether a word operation is present, and which
result width feeds the allocation, bounds check or pointer calculation.

## JALR target normalization is not a Thumb state switch
JALR adds a signed byte immediate to rs1, then clears result bit zero. JAL/JALR
write PC+4 to rd; rd=x0 discards the link. Base I requires four-byte instruction
alignment, while C permits two-byte alignment. [2][3]

Constructed rs1=0x1003, immediate=0: JALR targets 0x1002, not 0x1000. This is
misaligned for a base-I-only target but satisfies C's alignment requirement.
Alignment alone does not prove a valid instruction boundary or permitted target.
The low bit is not an Arm Thumb mode bit. A jump with rd=x0 may be a return,
tail call or intra-function transfer; recover its source register and context
before inventing a call/return edge.

## Compressed instructions change boundaries and link increments
With C, 16- and 32-bit instructions can be mixed at halfword boundaries. Some
encodings differ by XLEN: RV32 C.JAL shares its encoding space with RV64 C.ADDIW.
C.JALR writes PC+2 to x1, not PC+4; C.JAL is RV32-only. [3]

Constructed C.JALR at 0x2002 returns to 0x2004. Replacing its decoded spelling
with an uncompressed JALR while retaining PC+4 incorrectly points to 0x2006.
Preserve instruction length when reconstructing link values, patch coordinates
and stack traces. A plausible RV32 disassembly of RV64 compressed bytes can
invent a call where arithmetic actually occurs. This is not a guarantee that
every extension's instruction length or encoding is covered by C.

## A discarded load result can still fault or affect a device
A base load targeting x0 still performs its exceptions and side effects.
Misaligned load/store handling depends on the execution environment; successful
misaligned accesses need not be atomic. [2]

Investigation implication: deleting an apparent dead load from a model can erase
a faulting access or MMIO read. Conversely, lack of a misalignment trap in one
environment does not prove that the access is indivisible or portable. Recover
width, address, memory attributes and platform access rules before treating a
load-to-zero as a no-op or an unaligned shared field as race-free.

## M-extension divide-by-zero is a value result, not the x86 divide fault
M-extension integer division by zero produces an all-ones quotient and a remainder
equal to the dividend. Signed minimum/-1 returns that minimum and remainder zero.
RV64 word division/remainder results are sign-extended. [4]

Constructed RV32 DIVU of 7 by 0 produces 0xffffffff; REMU produces 7. An analysis
that terminates the path at an assumed hardware divide exception can miss a
subsequent huge-size use. Check any software guard/trap and actual destination
use. This ISA rule does not legalize C/C++ division by zero, prove that an M
instruction is supported, or describe floating-point division exceptions.

## LR/SC status, reservation and ordering are distinct
SC reports zero on a successful store and nonzero on failure; software must not
assume every failure code is exactly one. LR/SC require their specified natural
alignment, and eventual-progress guarantees have constrained-loop conditions. [5]

Constructed retry path: a nonzero SC result is not a stored payload value and
does not alone prove a competing thread changed the exact addressed word.
Inspect the reservation context, intervening instructions and retry side effects.
Atomic success still does not publish unrelated data or keep an object alive.
Ordering/domain and FENCE.I facts have their primary home in
`architecture-memory-ordering-barrier-evidence`.

## Primary sources and verification limits
Reviewed 2026-10-02. ISA sources select release v20260120. RV64I's HTML endpoint
was unavailable; its rules were checked in the official release PDF, chapter 4
(printed pages 41-43). No emulator or target instruction was executed.

1. [RISC-V unprivileged ISA PDF](https://docs.riscv.org/reference/isa/v20260120/_attachments/riscv-unprivileged.pdf): RV64I 2.1, chapter 4, register/word/load/shift rules.
2. [RV32I 2.1](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html): integer operations, control transfers and load/store effects.
3. [C extension 2.0](https://docs.riscv.org/reference/isa/v20260120/unpriv/c-st-ext.html): mixed widths, XLEN-dependent encoding and compressed links.
4. [M extension 2.0](https://docs.riscv.org/reference/isa/v20260120/unpriv/m-st-ext.html): division result table and word operations.
5. [A extension 2.1](https://docs.riscv.org/reference/isa/v20260120/unpriv/a-st-ext.html): LR/SC status, alignment and forward-progress limits.
