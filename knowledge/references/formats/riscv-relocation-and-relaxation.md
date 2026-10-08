---
id: format-riscv-relocation-relaxation
title: RISC-V ELF PC-relative relocation pairs, linker relaxation and global pointer
kind: reference
topics: [riscv, elf, relocations, linker-relaxation, global-pointer]
platforms: [linux, firmware]
architectures: [riscv32, riscv64]
---
# RISC-V linked-address evidence

## Separate relocatable instructions from linked instructions
Reviewed 2026-10-02. Scope: selected RISC-V ELF relocation and relaxation rules
from the dated psABI and GNU assembler manual, not a complete dynamic-loader
model. See `architecture-riscv-scalar-compressed-evidence` for actual instruction
semantics and `abi-riscv-integer-float-boundaries` for function arguments.

Record artifact stage: relocatable object, final executable/shared object or
loaded memory. Compare bytes, relocation records, symbol resolution and image
coordinates from that same stage. A placeholder immediate in an object is not
the final runtime destination. After link-time shrinking, copying offsets from
the object into the final image can identify a different instruction entirely.

## PCREL_LO12 refers to the high-part site, not simply the target symbol
R_RISCV_PCREL_HI20 identifies an AUIPC-relative high part. PCREL_LO12_I/S refers
to a label at the associated high-part relocation; the linker follows that entry
to the target symbol. The instructions need not be adjacent, and multiple low
uses can share the high part. [1]

Investigation implication: do not pair each low relocation with the nearest
preceding AUIPC by position alone. Resolve the label, relocation association and
register data flow. A load with the resulting address is not equivalent to ADDI
forming that address: one reads the pointed-to content. If relocation metadata
is absent, distinguish a data-flow hypothesis from a recovered association.

## Signed low immediates require high-part rounding
For a representable PC-relative delta D from the AUIPC site, the relocated high
part uses (D+0x800)>>12; the low part is interpreted as a signed 12-bit immediate.
The base is the AUIPC instruction address, not a page-aligned PC. [1][3]

Constructed AUIPC at 0x1000, target 0x2800: D=0x1800; high=2 and low=-0x800.
The result is 0x1000+0x2000-0x800=0x2800. Taking high=1 and low=-0x800 instead
produces 0x1800. Do not concatenate unsigned printed fields or borrow AArch64
ADRP's page-base rule. Validate encoded range, sign extension and relocation type
before applying this arithmetic; it is not a universal formula for GOT/TLS values.

## A call pair can become one instruction during linking
RISC-V call relaxation can replace an eligible AUIPC+JALR with JAL; compressed
call relaxation can produce C.JAL on RV32 under its additional constraints.
R_RISCV_RELAX marks eligible sequences in conjunction with their relocation. [1]

Constructed binary comparison: an object has an eight-byte call sequence while
the linked file has a four-byte call to the same resolved destination. The
missing AUIPC is not evidence that validation was removed or that the call was
inlined. Recompute subsequent coordinates and link values from final bytes.
Eligibility is not proof that a particular linker performed the transformation;
verify options, target distance, symbols and actual output. A tail call that
discards the link is a different control-flow role from an ordinary call.

## GP setup must not be reduced to a use of uninitialized GP
GNU as documents disabling relaxation around initial gp setup because a
GP-relative relaxation can otherwise turn that initialization into addi gp,gp,0.
It also allows local ISA-extension options without changing whole-file
architecture attributes. [2]

Constructed startup investigation: an apparent gp self-copy cannot establish
__global_pointer$ unless gp was already supplied correctly by the entry contract.
Trace startup before diagnosing later small-data accesses. Conversely, a valid
platform-provided gp can make a redundant local copy harmless. A local optimized
function using an extra extension is not necessarily inconsistent with the file's
baseline attribute; establish dispatch and runtime capability checks separately.

## Sources and verification limits
Reviewed 2026-10-02. psABI inspected version: 1.1, September 24, 2026-draft.
No linker was run; examples are constructed relocation arithmetic and artifact
comparisons. Dynamic binding, symbol interposition and TLS require their own
relocation/model contracts, not this ordinary PC-relative example.

1. [RISC-V psABI](https://riscv-non-isa.github.io/riscv-elf-psabi-doc/): PC-relative symbol addresses, procedure calls and linker relaxation.
2. [GNU as RISC-V directives](https://sourceware.org/binutils/docs/as/RISC_002dV_002dDirectives.html): .option norelax, gp initialization and local architecture options, rolling manual.
3. [RV32I instruction specification](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html): AUIPC and signed immediate semantics.
