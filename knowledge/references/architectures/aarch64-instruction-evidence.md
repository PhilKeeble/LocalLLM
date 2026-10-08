---
id: architecture-aarch64-instruction-evidence
title: AArch64 register widths, control flow, addressing and atomic instruction evidence
kind: reference
topics: [aarch64-instructions, registers, flags, branches, addressing, atomics, instruction-semantics]
platforms: [linux, android, windows, macos, ios, freebsd, firmware]
architectures: [arm64]
---
# AArch64 instruction evidence

## Scope: select the instruction set before the ABI
Reviewed 2026-10-02. These are selected A64 scalar instruction rules, not A32/T32
rules or a complete extension catalogue. Record instruction bytes, supported
features, W/X widths and exact operands. Calling-convention evidence lives in
`abi-aarch64-platform-conventions`; an ISA register name does not establish a
parameter role, preserved value or Windows/Apple/generic ABI selection.

Examples are constructed. PAC, MTE, SVE/SME, memory-type constraints and OS fault
handling require additional target-specific evidence. Do not assume every image
on an Arm system is A64, nor decode inline data as code because words are aligned.

## W/X views and the zero-register distinction
W0..W30 are the low halves of X0..X30. A W-register write clears its X-register
upper half. WZR/XZR read as zero and discard writes; encoded register 31 means
SP or ZR according to the instruction/operand, not a general X31. [1][2]

Constructed X0=0x1234567880000000: a result write W0=0xffffffff leaves
X0=0x00000000ffffffff, not -1 as signed 64-bit. A later signed-32 interpretation
and signed-64 interpretation differ. Do not model W0 as independent storage from
X0, or assume a zero-register operand addresses the stack. Verify the decoder's
SP/ZR choice against the specific encoding before recovering stack operations.

## Extension is not saturation
A64 ADD with an extended-register operand extends that source, optionally shifts
it and adds it to the other source at destination width. SXTH means sign-extending
the source's low halfword; it does not clamp the result to a 16-bit range. [2]

Constructed `add w0,w1,w2,sxth` with W1=32767 and W2=1 produces W0=32768,
not the saturated value 32767. There is no implicit 16-bit bounds guard. If the
result is subsequently stored as a halfword, analyze that truncation separately.
Source caveat: introductory guide [1], section 7.4, describes this operand as
saturating; that conflicts with instruction definition [2], D2.5. This reference
uses the instruction definition. Do not generalize this correction to genuinely
saturating SIMD instructions.

## NZCV comparisons and carry are not x86 flags
NZCV names the negative, zero, carry and overflow condition flags. A branch
can consume one flag or a combination; recover their actual producer first.
A64 CMP subtracts its second operand from its first and updates NZCV without
retaining the result. SUBS updates flags; SUB does not. After integer subtraction,
C=1 means no borrow. Unsigned HS/CS tests C=1, LO/CC tests C=0; HI requires
C=1 and Z=0. Signed LT tests N different from V; GE tests N equal to V. [2]

Constructed CMP of W0=0 and W1=1 gives C=0, so B.LO is taken. Applying x86's
carry-as-borrow rule reverses this unsigned bounds decision. Trace the actual
flag producer at the same width as the branch's interpretation. An intervening
ordinary ADD/SUB need not replace NZCV, but a flag-setting form or call can change
the evidence; guessed pseudocode is not a substitute for that trace.

## Compare-and-branch versus conditional comparison
CBZ/CBNZ test a register directly; TBZ/TBNZ test a selected bit. They do not need
a preceding CMP; CBZ does not update NZCV. CCMP instead replaces NZCV with either
comparison flags or its immediate fallback flags according to the condition. [2]

Constructed `ccmp w0,#3,#0,eq`: when EQ is false, NZCV becomes zero, not the
old flags. A following B.EQ therefore does not inherit the preceding equality.
Recover both outcomes of conditional comparisons when reconstructing compound
guards. Similarly, `cbz w0,label` tests only the low 32 bits; a nonzero X0 with
zero W0 can branch. Do not silently widen the tested value to a pointer.

## Link branches versus tail transfers
BL and BLR write X30 with the following instruction address (PC+4); B/BR are
branches without that link update. BL is PC-relative, BLR uses a register. [2]
The link is not an automatic stack push. Recover explicit preservation and
restoration when reasoning about nested calls and unwind state.

Constructed investigation: BR at a function end may be a tail transfer, not an
ordinary return or a missing call. Conversely, a BL target can be a veneer or
runtime stub rather than the final implementation. Follow the target and ABI
boundary before assigning a prototype. A saved X30 value is return-flow evidence,
not proof that every path returns or that an exception uses the same return state.

## ADRP uses a fixed 4 KiB coordinate
ADR forms a PC-relative address. ADRP uses the instruction's PC rounded down
to 4096 bytes plus its signed page displacement scaled by 4096. [2] This
instruction coordinate is not the target OS's configurable memory-page size.

Constructed instruction PC=0x12345 and decoded displacement +2 pages gives
0x14000. Following ADD #0x678 yields 0x14678; using the unrounded PC would
incorrectly yield 0x149bd. Do not use x86 next-instruction RIP semantics here.
Track paired relocations and consumers: a following load may read a pointer slot,
whereas ADD may construct an object's address. An ADRP target alone is neither
the final object address nor proof of a data read.

## Memory operands include width, extension and writeback
A64 LDR/STR width follows the selected form; byte/halfword forms narrow memory
access, and signed-load forms extend into their destination width. Offset,
pre-indexed and post-indexed forms differ: pre-index updates the base and uses
the updated address; post-index uses the old base then updates it. [1][2]

Constructed X1=0x1000: `ldr x0,[x1,#8]!` reads at 0x1008, while
`ldr x0,[x1],#8` reads at 0x1000; both leave X1=0x1008 on normal completion.
That post-state alone cannot identify the accessed object. Recover full byte
ranges for pair/vector accesses and sign extension separately from address
extension. Alignment acceptance, device-memory behavior and atomicity need the
specific instruction and target configuration, not a blanket unaligned rule.

## Exclusive-store status is not the stored value
LDXR/STXR are the load/store-exclusive family; LDAXR/STLXR add acquire/release
semantics. STXR's W status result is 0 for an update and 1 when it does not update
memory. A synchronous Data Abort is a separate path that does not update that
status register. CLREX clears the executing processor's local monitor. [2]

Constructed `stxr w2,x1,[x0]; cbnz w2,retry`: W2 is success status, X1 is the
proposed value. Inverting that interpretation invents a successful update on the
retry path. A failed attempt does not itself prove another thread changed the
logical object; monitor state also matters. Trace retry, mismatch and abort paths,
and whether side effects performed before retry can repeat. Atomicity of the
updated location does not make surrounding multi-field invariants atomic.

## LSE atomics and outlined helpers
The A64 LSE family includes CAS variants. CAS conditionally replaces a matching
value atomically; CASA adds acquire semantics, CASL release, CASAL both. Plain
CAS must not be assumed to publish unrelated data with release ordering. [2]

GCC -moutline-atomics can generate helper calls choosing LSE at runtime when
available and load/store-exclusive sequences otherwise. Direct LSE generation
depends on target options/features. [3] Thus no visible retry loop at the call
site does not establish a non-atomic update. Inspect the selected helper and
instruction variant, object width/alignment, result interpretation and ordering.
Do not label a source operation relaxed or sequentially consistent from a symbol
name alone. See `reference-concurrency-memory-order-atomic-invariants` for the
separate publication, lifetime and language-model proof obligations.

## Primary sources and review limits
Reviewed 2026-10-02. Selected entries were inspected, not every instruction in
these manuals. Rules are baseline unless features are named; no target execution
is claimed. Numeric cases are constructed arithmetic checks. The source conflict
on SXTH is recorded above rather than propagated as competing evidence.

1. [Armv8-A Instruction Set Architecture, issue 1.1](https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/Learn%20the%20Architecture/Armv8-A%20Instruction%20Set%20Architecture.pdf?revision=818c7869-3849-4e5d-bde2-710e69defb57): sections 6-9; section 7.4 saturation wording is not adopted.
2. [Arm Instruction Set Reference Guide, 100076_0100_00_en](https://documentation-service.arm.com/static/6245c734b059dc5ff9a8bdab): A3 registers, D1 flags, D2 ADD/ADR/ADRP/branches/CCMP/CLREX and D3 load/store/CAS/exclusive entries. Inspected PDF carries 2018 copyright; not represented as the latest architecture specification.
3. [GCC AArch64 options](https://gcc.gnu.org/onlinedocs/gcc/AArch64-Options.html): -moutline-atomics and LSE target selection, rolling manual.
