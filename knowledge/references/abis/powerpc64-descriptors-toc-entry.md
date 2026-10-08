---
id: abi-powerpc64-descriptors-toc-entry
title: PowerPC64 ELFv1 descriptors versus ELFv2 entry points and TOC linkage
kind: reference
topics: [powerpc, calling-conventions, function-descriptors, toc, elfv2, linkage]
platforms: [linux]
architectures: [powerpc]
---
# PowerPC64 ELF linkage evidence

## ABI revision and endianness are separate choices
Reviewed 2026-10-02. This reference distinguishes the historical descriptor-based
PowerPC64 ELF ABI from OpenPOWER ELFv2 revision 1.5, December 1, 2020. ELFv2
defines both byte orders. [1][2] Neither rule set is a generic 32-bit embedded,
AIX XCOFF, Apple Mach-O or console ABI.

Identify file format, ELF ABI flags, symbol/relocation conventions, object data
model and call sequences together. Little endian alone is not the definition of
ELFv2. A data-looking callable address and r2 manipulation can be ABI evidence,
not necessarily corrupt control data. Keep the target's actual ABI selection
distinct from the disassembler's generic PowerPC processor setting.

## ELFv1 function pointers address descriptors, not instruction bytes
In the inspected descriptor-based PowerPC64 ELF ABI, a function descriptor has
three doublewords: code entry, TOC base and environment pointer. A C function
pointer identifies the descriptor; dot-prefixed symbols identify code entries.
[1] GNU ld also documents compiler-produced compressed .opd entries that overlap
the otherwise unused third word and are spaced 16 bytes apart. [3]

Constructed descriptor at 0x4000 containing entry 0x8000 and TOC 0x12000 means
the callable pointer can be 0x4000 while execution starts at 0x8000. Disassembling
0x4000 as instructions or reporting its non-executable mapping as an invalid
callback is premature. Validate descriptor extent, relocation and the consuming
call sequence; do not impose a universal 24-byte table stride merely from the
standard descriptor's three-word layout.

## ELFv2 function pointers use global entry; local entry can skip setup
ELFv2 function pointers contain the global entry address. For symbols describing
a separate local entry, a global-entry caller supplies the function address in
r12 and the entry establishes r2's TOC; a local-entry caller supplies the correct
TOC already. Encoded st_other information describes the entry relationship. [2]

Constructed symbol at 0x8000 with local-entry offset 8 allows a matching local
call at 0x8008. That is not automatically an instruction-skipping attack or a
second function. Prove the TOC context and the symbol's entry contract. Conversely,
redirecting an arbitrary function-pointer call to 0x8008 can skip required setup.
Do not dereference an ELFv2 function pointer as an ELFv1 three-word descriptor.

## r2 preservation is not one unconditional rule for every ELFv2 call
ELFv2 distinguishes local/global and TOC-using/TOC-free call paths. Its entry
metadata includes a same-entry form preserving r2 and another treating it as
caller-saved. [2] GNU ld can add TOC-adjusting stubs between groups and optimize
eligible call sequences; localentry:0 permits particular save/restore omissions.
[3]

Investigation inference: absence of a post-call r2 reload does not by itself prove
wrong globals. Recover entry metadata, relocation, final stub and caller need
before judging preservation. Conversely, a stub-adjusted r2 must be propagated
when resolving subsequent TOC-relative accesses. An object's pre-link call code
is not proof of the final executable's sequence. Do not treat every linker stub
as an application authorization wrapper or attribute its scratch state to a
source-level object.

## ELFv2 scalar call registers do not define every recovered argument
In OpenPOWER ELFv2 revision 1.5, r3-r10 are volatile parameter registers,
r14-r31 are nonvolatile, r13 is the thread pointer and r1 is a 16-byte-aligned
stack pointer. CR2-CR4 are preserved; LR and CTR are volatile. [2]

Integer arguments shorter than 64 bits are sign- or zero-extended according to
their type. Constructed unsigned int 0x80000000 becomes 0x0000000080000000,
not MIPS n32's sign-extended representation. Register allocation still depends
on argument type, position and prototype; FP/vector values can leave integer
register positions unused. Recover those constraints before calling a hole an
uninitialized input. These are ELFv2 rules, not the embedded EABI's r13 data base.

## Sources and limits
Reviewed 2026-10-02. Selected linkage rules, not complete aggregate/FP/vector
allocation tables. Unknown target ABI variants require their own specification.
Constructed addresses were not compiled, linked or executed.

1. [PowerPC64 ELF ABI supplement](https://refspecs.linuxfoundation.org/ELF/ppc64/PPC-elf64abi-1.8.html): page title identifies 1.7.1 despite the URL; sections 3.2.5 and 3.5.11, descriptor-based ABI.
2. [OpenPOWER ELFv2 revision 1.5, 2020-12-01](https://kib.kiev.ua/x86docs/POWER/ABI/leabi-20201201.pdf): primary-author PDF on mirror, sections 2.2.1-2.2.4, 2.3.4 and 3.4.1. [Publisher catalogue](https://openpower.foundation/specifications/64bitelfabi/); its direct download endpoint was unavailable during review. Edition comes from the inspected PDF title, not the catalogue's differently formatted version label.
3. [GNU ld PowerPC64 ELF support](https://sourceware.org/binutils/docs/ld/PowerPC64-ELF64.html): rolling manual, compressed .opd, multi-TOC and localentry options.
