---
id: architecture-mips-decoding-delay-slots
title: MIPS decoding variants, delay-slot guards, arithmetic and macro evidence
kind: reference
topics: [mips, instruction-semantics, delay-slots, compressed-instructions, macros]
platforms: [linux, firmware, irix]
architectures: [mips]
---
# MIPS instruction evidence

## Identify encoding, ISA revision and endianness independently
Reviewed 2026-10-02. GCC 15.1 distinguishes ISA selection, big/little endian,
MIPS16/microMIPS and ABI selection; compressed/uncompressed interworking can
require different control-transfer forms. [1] A decoder producing plausible
mnemonics does not independently establish any of those choices.

Record CPU/SoC, firmware region, execution mode, ELF flags where available and
caller/callee transitions. Compare several known addresses and data constants
before accepting a raw-image byte order. Do not equate an ELF32 container with
32-bit-only registers: n32 is a counterexample, covered in
`abi-mips-o32-n32-n64-evidence`. The instruction examples here use classic
four-byte MIPS32 encodings, not MIPS16, microMIPS or arbitrary later revisions.

## BEQ and BEQL do not guard their delay slots the same way
Classic MIPS32 BEQ executes its delay-slot instruction before transfer, whether
the branch is taken or not. BEQL executes the slot only on the taken path. [2]

Constructed investigation: a store immediately after BEQ still happens on the
not-taken path; treating it as part of only the taken block can hide an unwanted
write. Replacing that reasoning with BEQL's annulled not-taken slot can instead
invent a write that never executes. Establish exact opcode and ISA support before
building the guarded-write path. Do not interpret a control transfer in a classic
delay slot as an ordinary nested branch; the inspected manual marks such cases
UNPREDICTABLE. Exception paths still require separate analysis.

## Branch target base and call return address are different coordinates
Classic MIPS32 BEQ uses branch-PC+4 plus the signed 16-bit displacement scaled
by four. Classic JALR links to jump-PC+8, after its delay slot. [2]

Constructed branch at 0x1000 with encoded displacement 3 targets 0x1010, not
0x100c. A classic JALR at 0x2000 returns to 0x2008, not its slot at 0x2004.
Keep instruction address, slot address, target and link value separate in a
call graph or stack reconstruction. This is not a universal rule for compressed
forms, Release 6 compact branches, firmware exception returns or a custom ABI.
The presence of a link register write does not alone prove an ordinary function
call; establish the target and subsequent use of the link.

## Compact branches must not inherit the classic delay-slot model
GCC 15.1's MIPS options can select compact branches on Release 6 where available,
or a delay-slot form otherwise. The documented selection depends on ISA and
whether a useful delay-slot instruction can be scheduled. [1]

Investigation consequence: do not annotate every instruction after a MIPS branch
as an unconditional delay-slot operation. Classify the actual encoding with the
matching ISA manual before assigning execution to a path. A family name or
compiler option is insufficient evidence for a specific branch's semantics.
This reference does not enumerate Release 6 forbidden-slot restrictions; when
legality depends on one, require the applicable revision rather than importing
the older manual's restriction unchanged.

## ADDIU does not zero-extend its immediate or trap on signed overflow
For classic MIPS32 ADDIU, the immediate is sign-extended and arithmetic wraps
to 32 bits without Integer Overflow. ADDI instead traps on signed overflow. [2]

Constructed source value 1 and immediate bits 0xffff produce zero with ADDIU,
not 0x10000. Constructed 0x7fffffff plus 1 wraps to 0x80000000 with ADDIU;
assuming it traps can wrongly remove a later negative-size path. Conversely,
ignoring ADDI's exception can invent an ordinary fallthrough value. The mnemonic's
unsigned suffix is not evidence that the source variable was unsigned. Machine
wrap also does not establish that corresponding signed C arithmetic was defined.

## Assembler macro spelling is not a one-instruction execution trace
GNU as supports MIPS macros that expand to multiple instructions, including
comparisons, large offsets and unaligned-access operations. Expansion may use
a temporary register, normally $1/$at. Its .set nomacro warns about multi-op
expansion; it does not mean every accepted mnemonic is a native opcode. [3]

Investigation inference: a source-level bgt or a symbolic load is insufficient to
locate the actual compare, branch, scratch clobber or memory accesses. Inspect
assembled bytes, selected ISA, relocation records and scheduling. Do not attribute
all accesses of a macro expansion to one indivisible load. A scratch register
introduced by expansion need not represent a source variable or hidden argument.

## Sources and limits
Reviewed 2026-10-02. Facts are scoped to the inspected editions; examples are
constructed arithmetic/control-flow cases, not assembler output or CPU runs.
Primary-author manuals on mirrors are cited as such; no manual chapters imported.

1. [GCC 15.1 MIPS options](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/MIPS-Options.html): endian/ISA/ABI, interlink-compressed and compact-branches options.
2. [MIPS Technologies MIPS32 Volume II, revision 0.95, 2001-03-12](https://www.ece.lsu.edu/ee4720/mips32v2.pdf): printed pp. 34-35 ADDI/ADDIU, 55-57 BEQ/BEQL and 117-118 JALR; LSU-hosted copy.
3. [GNU as MIPS macros](https://sourceware.org/binutils/docs/as/MIPS-Macros.html): rolling assembler manual, expansion and temporary-register behavior.
