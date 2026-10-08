---
id: architecture-aarch32-thumb-state-decoding
title: AArch32 A32 and Thumb decoding, interworking, literal pools and predication
kind: reference
topics: [aarch32, thumb, interworking, literal-pools, predication, code-data]
platforms: [linux, android, windows, firmware]
architectures: [arm]
---
# AArch32 and Thumb evidence

## Instruction state is part of the address interpretation
Reviewed 2026-10-02. This reference concerns A32/T32 decoding, not A64 or a
universal firmware execution model. A32 uses word-aligned 32-bit instructions;
T32 has halfword-aligned 16- and 32-bit encodings. [1] Thumb-2 is not an instruction
stream of uniformly two-byte operations. Processor profile, revision and enabled
extensions still determine which encodings are valid.

Constructed boundary check: a four-byte T32 instruction at 0x1002 occupies bytes
0x1002 through 0x1005; the next instruction begins at 0x1006, not 0x1004. A decoder
starting at its second halfword can invent a different control-flow graph.
Record the state and validated boundary with every entry point. Plausible
mnemonics alone do not establish executable code. ABI argument rules are in
`abi-aapcs32-base-vfp-platforms`, not implied by the instruction-state label.

## Odd Thumb pointers and interworking are not unaligned instruction fetches
Arm ELF STT_FUNC values for Thumb have bit zero set; mapping to the instruction
address removes that bit. [2] BX selects A32/T32 from its register operand's low
bit on processors supporting both. M-profile versions listed in [1] support
T32 only; an attempted A32 switch faults. BX is not an AArch32-to-AArch64 switch.

Constructed normal code-pointer case: 0x2001 denotes Thumb instructions at 0x2000,
not a byte-offset entry at 0x2001. Preserve both the encoded pointer and normalized
fetch address; clearing the bit in the actual callback value changes its meaning.
Do not treat an arbitrary odd integer as a valid function pointer without type,
mapping and use evidence. Exception-return operands require their separate
architecture contract; this normalization is not a universal rule for BX operands.

## Mixed ELF sections and mapping symbols
Arm ELF mapping symbols identify intervals: $a for A32, $t for Thumb and $d for
data, including literal pools. Suffixed forms such as $t.name also exist. Each
interval extends to the next mapping symbol or section end; these are not
function boundaries. [2]

Constructed section: $t at 0x1000, $d at 0x1010, $t at 0x1018. Decoding the middle
eight bytes as instructions contradicts that metadata. Follow the actual branch
around the pool and data references to it. Stripped or conflicting metadata needs
independent boundary evidence, not an assumption that all bytes in an executable
section are code. A data marker is neither proof of immutability nor proof that
malformed control flow cannot enter the interval.

## Literal-load address, loaded value and pseudo-instruction are distinct
Arm armasm's LDR Rd,=constant is a pseudo-instruction: it may become a MOV/MVN or
a PC-relative read from a literal pool. ADR forms an address without that data
read. [3] A disassembler's symbolic presentation need not reproduce the original
assembler source.

For the ordinary word literal-load forms discussed here, A32 uses instruction
address+8; T32 uses (instruction address+4) rounded down to a four-byte boundary
before applying the byte displacement. [3] Constructed T32 LDR at 0x1002 with
displayed displacement +0x20 reads at 0x1024, not 0x1026. If that word contains
0x3001, distinguish instruction location 0x1002, pool location 0x1024 and loaded
value 0x3001. Only a subsequent use establishes whether the value is a code pointer,
data pointer or integer. Do not apply this aligned base to every PC-using opcode.

## Predication is control flow even without a branch instruction
For T32 IT blocks, T uses the initial condition and E its inverse. The inspected
Armv8 guide deprecates multi-instruction IT forms; that does not erase their
meaning in older code. Flag updates depend on the exact encoding and IT context;
many narrow instructions suppress updates inside IT. [1]

Constructed case: a valid IT EQ followed by an ordinary conditional store does
not mean the store occurs on every fall-through path. Recover the flag producer,
intervening flag writes and IT state before asserting an unchecked write. Equally,
an isolated instruction decoded without its preceding IT can hide the guard.
Do not make every instruction inside IT conditional by assumption: the inspected
entry explicitly treats BKPT specially. Architectural legality, debugger stepping
and decompiler rendering are separate evidence.

## Calls, linker veneers and local register assumptions
In AAPCS32, BL records the return address in LR rather than implicitly pushing it
onto the stack. LR's low bit records return instruction state. Linker veneers
may clobber r12/IP and condition flags at eligible relocated branches. [4]

Investigation implication: a small branch stub may be interworking or range
extension, not a separate security check. Follow it to the actual callee before
propagating a prototype. A value held only in r12 across such a transfer is not
protected merely because the source-level callee appears not to touch it. A saved
LR is return-state evidence, not proof of a complete frame or a user-controlled
return address. Distinguish ordinary calls from exception entry/return.

## Primary sources and limits
Reviewed 2026-10-02. No target instructions were executed; examples are constructed
decoding/address checks. Arm instruction guide 100076_0100_00_en (2018) supplies
selected baseline entries, not all subsequent extensions. armasm guide is
100069_0611_00_en (2018). ABI references are pinned to release 2025Q4.

1. [Arm instruction reference](https://documentation-service.arm.com/static/6245c734b059dc5ff9a8bdab): A2.14, C2.21 BX and C2.44 IT, including profile/deprecation limits.
2. [Arm ELF ABI](https://github.com/ARM-software/abi-aa/blob/2025Q4/aaelf32/aaelf32.rst): Symbol Values, Mapping symbols, Addends and PC-bias compensation.
3. [Arm armasm guide](https://documentation-service.arm.com/static/5f75fe0b0ccfbc33efcab7d8?token=): 3.7-3.10, 6.5 and 8.5, pools versus pseudo-instructions and PC-relative expressions.
4. [AAPCS32](https://github.com/ARM-software/abi-aa/blob/2025Q4/aapcs32/aapcs32.rst): Subroutine Calls and Use of IP by the linker.
