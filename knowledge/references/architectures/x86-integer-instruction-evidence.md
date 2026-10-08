---
id: architecture-x86-integer-instruction-evidence
title: x86 and x64 register widths, flags, addresses and integer instruction evidence
kind: reference
topics: [x86-instructions, registers, flags, conditions, addressing, arithmetic, string-instructions]
platforms: [windows, linux, macos, android, freebsd, firmware]
architectures: [x86, x64]
---
# x86 integer instruction interpretation

## Scope and decoding prerequisites
Reviewed 2026-10-02. Baseline scalar x86/Intel 64 semantics, not every extension
or vendor exception. Examples use Intel destination-first syntax and are
constructed. Preserve instruction bytes, execution mode, operand/address widths
and prefixes; a mnemonic alone is incomplete evidence. Register argument roles
come from an ABI, not the ISA: consult `abi-windows-x64`, `abi-sysv-amd64` or
`abi-windows-x86` separately.

Do not turn a plausible decode into a confirmed function or source type. Trace
actual inputs, implicit operands, defined flags and subsequent uses. A CPU rule
does not establish source-language defined behavior; see
`architecture-machine-representation` and
`reference-native-integer-size-buffer-arithmetic`.

## Partial general-purpose register writes in 64-bit mode
In 64-bit mode, a 32-bit general-purpose result clears the register's upper
32 bits. Ordinary 8/16-bit writes preserve the other bits. [1] These are
general-purpose register (GPR) rules, not a rule that a four-byte memory store
clears eight bytes.

Constructed example: starting with RAX=0x1122334455667788, `mov al,0` leaves
RAX=0x1122334455667700; `mov ax,0` leaves 0x1122334455660000; `mov eax,0` leaves
zero. Analyze each from the original value, not as a sequence. A low-byte Boolean
result does not itself define a clean full-width integer. Conversely, prior high
bits cannot survive a genuine EAX result write. Instruction-specific implicit
updates and vector-register rules require their own entries.

## Sign extension stops at the specified destination width
MOVSX/MOVSXD sign-extend and MOVZX zero-extends into the specified destination. [3]
The destination-register rule still matters in 64-bit mode: writing EAX clears
the upper half of RAX. [1] Do not replace the encoded width with the decompiler's
chosen type.

Constructed byte 0x80: `movsx eax,byte ptr [p]` leaves RAX=0x00000000ffffff80,
not 0xffffffffffffff80. `movsx rax,byte ptr [p]` produces the latter; `movzx
eax,byte ptr [p]` produces 0x80. A subsequent `movsxd rax,eax` can restore signed
32-to-64 interpretation, but it must actually occur. Follow which width a later
comparison or pointer calculation consumes before deciding that the input is
negative, bounded or a large positive index.

## Flag producers must be tracked individually
CMP sets subtraction flags without storing the difference. INC/DEC preserve CF
while changing other arithmetic flags. LEA does not change flags. [2] TEST sets
flags from bitwise AND without storing it, clearing CF/OF. [3]

Constructed sequence: `cmp eax,edx; inc ecx; jb label` uses carry from CMP, not
from INC. Replacing JB with JZ tests INC's zero result instead. Track the last
definition of every consumed flag along each predecessor path; the nearest
arithmetic instruction need not define all of them. An undefined flag is not a
documented zero and not a reliable retained prior value. Calls require a calling
contract or inspection, not an assumption that comparison flags survive.

## Integer condition codes are predicates on flags
After CMP a,b at the recovered width, these x86 predicates select comparisons.
They are not portable mappings for another ISA's carry convention. [1]
CF is the carry flag, ZF the zero flag, SF the sign flag and OF the signed-overflow
flag. Their combination matters; SF alone is not a signed less-than comparison.

| Branch | Predicate | Comparison after CMP a,b |
| --- | --- | --- |
| JE / JNE | ZF / not ZF | equal / unequal |
| JB / JAE | CF / not CF | unsigned below / at least |
| JBE / JA | CF or ZF / neither | unsigned at most / above |
| JL / JGE | SF differs from OF / same | signed less / at least |
| JLE / JG | ZF or SF differs from OF / neither | signed at most / greater |

Constructed a=0xffffffff, b=1 at 32 bits: JA is true, JL is true, and JE is false.
There is no contradiction: unsigned a is 4294967295, signed a is -1. A branch
name alone does not prove the source declaration's signedness or the caller's
allowed input range. Verify operand order and the flag-producing instruction.

## Effective addresses versus reads and pointer types
Ordinary base/index addressing combines base, scaled index (1/2/4/8) and
displacement. RIP-relative addressing uses the next instruction's RIP plus a
signed displacement. [1] LEA computes an effective address without reading its
referent; its output width matters. [2]

Constructed example: instruction at 0x1000, length 7, RIP displacement -0x20
selects 0xfe7, not 0xfe0. `lea eax,[rcx+rcx*4]` can implement low-32-bit 5*x
arithmetic; it does not prove an array dereference or pointer source type.
Record address-size truncation separately from data width. For actual memory
operands, retain applicable segment-base context, especially FS/GS, and validate
the full access range. Numerical address calculation alone proves neither mapping
nor lifetime nor object bounds.

## Scalar shift counts and flags
For baseline SHL/SAL/SHR/SAR, counts are masked to five bits, or six for a
64-bit operand. A zero effective count preserves flags; OF is undefined for
effective counts greater than one. SAR sign-fills; SHR zero-fills. [3]

Constructed 32-bit examples: SHL by 32 has effective count zero, whereas SHL by
33 has effective count one. Do not apply those scalar rules to packed SIMD shifts
or conclude a C/C++ shift by its type width is valid. SAR of -5 by one yields -3;
signed division by 2 truncates toward zero, yielding -2. A compiler can add bias
before a shift to implement division. Recover the entire sequence before naming
the expression, and do not use undefined OF as a dependable overflow check.

## Multiply result width and overflow interpretation
One-operand MUL/IMUL produce double-width results in implicit accumulator pairs
(for 64-bit operands, RDX:RAX). Two/three-operand IMUL retain the low half;
their CF/OF describe signed truncation, not unsigned high-half nonzero. [2][3]

Constructed unsigned operands 0xffffffff and 2 have product 0x1fffffffe, but
32-bit IMUL's signed interpretation is -1*2=-2, representable with CF=OF=0.
Testing those flags does not detect this unsigned overflow. Identify the product
width used for allocation and the width used later for indexing/copying.
The low product alone cannot distinguish signed from unsigned multiplication;
look for high-half consumption, checks and downstream interpretation.

## Division includes an implicit high dividend
DIV is unsigned; IDIV is signed. With a 32-bit divisor the dividend is EDX:EAX,
quotient EAX and remainder EDX; 64-bit uses RDX:RAX. IDIV truncates toward zero.
Zero divisor or unrepresentable quotient raises #DE, not an overflow flag. [2]

Constructed DIV: EDX=1, EAX=0, divisor=2 yields quotient 0x80000000; analyzing
EAX alone would incorrectly predict zero. Check preparation of the high half,
including intentional double-width inputs. A nonzero-divisor guard alone does
not rule out #DE: signed minimum divided by -1 is outside the signed quotient
range. Exception reachability and its security consequence remain separate
questions; a divide fault is not automatically memory corruption.

## String instructions use implicit state and element counts
MOVS copies, STOS stores the accumulator and CMPS/SCAS compare. String index
updates depend on element width and DF; REP counts elements using the address-size
selected count register. REPE/REPNE add a ZF termination condition. [3]

Constructed `rep movsq` with RCX=3 and ordinary 64-bit addressing attempts three
eight-byte transfers, not three bytes. DF=1 changes traversal direction; it does
not turn arbitrary overlapping ranges into a correct memmove implementation.
Track source/destination starting addresses, count, width and direction together.
Distinguish scan termination from exhausted count. A fault can leave partial
progress; neither the mnemonic nor a post-fault pointer proves the original
requested copy completed. Do not assume transactional rollback of earlier writes.

## Conditional move is not a conditional memory-access guard
For ordinary x86 CMOVcc with a memory source, the source is read before conditionally
assigning the destination. [2] Do not treat it like a branch that skips the read.

Constructed sequence: a null-pointer comparison followed by `cmovne rax,[rbx]`
does not make the memory read safe when RBX is null. Verify the actual encoding
and memory operand. Distinguish architectural fault behavior from speculative
execution questions; this rule already concerns the architectural source read.
Likewise, a decompiler's conditional expression may hide an unconditional load
performed before the condition was tested.

## Primary sources and version scope
Reviewed 2026-10-02. Inspected Intel SDM PDFs below identify revision 060US,
September 2016. These establish the selected baseline semantics, not current
extension coverage or every processor's errata. No target instruction execution
is claimed; numeric examples are independently checked arithmetic.

1. [Intel SDM volume 1](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-1-manual.pdf): sections 3.4.1.1, 3.5-3.7 and table 7-4.
2. [Intel SDM volume 2A](https://software.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2a-manual.pdf): CMP, INC/DEC, CMOVcc, LEA, DIV/IDIV and IMUL entries.
3. [Intel SDM volume 2B](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf): MOVSX/MOVSXD/MOVZX, MUL, TEST, SAL/SAR/SHL/SHR, MOVS, STOS, SCAS and REP entries.
