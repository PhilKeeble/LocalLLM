---
id: abi-powerpc32-sysv-eabi-evidence
title: PowerPC32 System V and embedded EABI register, stack and small-data evidence
kind: reference
topics: [powerpc, calling-conventions, eabi, stack-alignment, small-data]
platforms: [linux, firmware]
architectures: [powerpc]
---
# Selected 32-bit PowerPC calling conventions

## Identify the ABI before interpreting preserved context
Reviewed 2026-10-02. These are the September 1995 System V PowerPC supplement
and PowerPC Embedded ABI version 1.0, which adopts that base with explicit
changes. They are not AIX, Apple, console, SPE or all RTOS contracts. [1][2]
Use `abi-powerpc64-descriptors-toc-entry` for selected 64-bit ELF conventions.

For the inspected 32-bit base, r3-r10 carry integer argument words; f1-f8 carry
eligible floating arguments. These registers are volatile. r14-r31 and CR2-CR4
are preserved; LR is volatile. [1] A reconstructed value surviving only in r5
across an unknown call therefore needs evidence, not a presumed preservation
rule. Saved nonvolatile registers are not automatically application parameters.

## Argument holes and indirect objects can resemble missing parameters
The inspected PowerPC32 System V allocation starts integer arguments at r3.
A supported long long uses an odd/even register pair; an even next register is
skipped. Aggregates are passed indirectly, with copies when needed for by-value
semantics. Ordinary integer/pointer results use r3. [1]

Constructed signature f(int, long long) uses r3, then r5/r6, leaving r4 unused.
An uninitialized r4 is not thereby a missing argument. Likewise, an argument
pointer can represent a by-value structure copy, not source-level pointer
ownership. Recover the full signature and copy before alleging aliasing or a
write-back defect. Do not transfer this pair numbering to Arm's register pairs
or to 64-bit PowerPC aggregate classification.

## Embedded EABI stack alignment differs from the System V base
The inspected System V base requires 16-byte SP alignment. EABI version 1.0
instead requires eight-byte alignment throughout calls and dynamic allocation.
EABI itself specifies no OS or exception interface. [1][2]

Constructed r1=0x7ff8 is eight-byte aligned but not 16-byte aligned. It can meet
this EABI rule while failing the System V rule. Record the compiler ABI and
boundary before diagnosing a malformed frame. A firmware ELF file or an EABI
claim does not establish Linux syscall numbers, interrupt entry layout or the
frame requirements of a separately specified vector extension.

## Embedded r2 and r13 bases are not ordinary object parameters
EABI version 1.0 dedicates r2 to the .sdata2/.sbss2 base when those sections
exist, analogous to r13's .sdata/.sbss small-data base. The bases support signed
16-bit displacements. An ELF shared-object routine must not use r2 this way. [2]

Investigation inference: resolving a negative r2-relative displacement as a
negative array index can fabricate an underflow. Establish the initialized base,
section bounds and relocation first. Conversely, a plausible base-register name
does not prove startup initialized it. Do not import the 64-bit ELFv2 thread
pointer meaning of r13 or its TOC meaning of r2 into this embedded convention.

## Sources and limits
Reviewed 2026-10-02. Historical normative ABI rules, not a claim about a specific
compiler build. Examples are constructed and were not compiled or executed.

1. [System V PowerPC supplement, September 1995](https://refspecs.linuxfoundation.org/elf/elfspec_ppc.pdf): printed pp. 3-14 to 3-22, registers, stack, argument allocation and returns.
2. [PowerPC Embedded ABI version 1.0](https://www.nxp.com/docs/en/application-note/PPCEABI.pdf): printed pp. 2, 5-6, adopted base, small-data registers, stack and OS-interface scope.
