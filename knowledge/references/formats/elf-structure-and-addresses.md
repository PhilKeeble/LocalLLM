---
id: format-elf-structure-addresses
title: ELF headers, segments, sections, symbols and checked address mapping
kind: reference
topics: [elf, headers, segments, sections, load-bias, address-mapping, symbols]
platforms: [linux, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# ELF structural evidence

## ELF identity and header bounds

Decode ELF magic, EI_CLASS, EI_DATA, e_machine, e_type and e_flags before
reading architecture-dependent structures. EI_DATA selects byte order;
e_machine identifies the instruction-set family. EI_CLASS selects container widths;
it does not alone prove the program's C data model. EI_OSABI zero is not proof
of a particular operating system. ET_REL is relocatable, ET_EXEC executable,
ET_DYN shared-object format and ET_CORE a core image; establish actual loader
role from additional evidence. [1]

For each header table, validate offset, entry size, count and remaining file
bytes without overflowing arithmetic. Extended section counts/indexes use
section zero; zero e_shnum does not by itself distinguish absent sections from
extended numbering. Validate the escape case before indexing. [1,3]

Investigation: reject a decoder's selected architecture if it contradicts the
header and instructions. Malformed metadata is an observation; it does not by
itself prove that a deployed loader accepts or executes the image.

## ELF table coordinates and extended numbering

ELF e_entry is a virtual address, not a file offset; e_phoff and e_shoff are
file offsets. A zero entry indicates no associated entry point. Extended
numbering uses fields in section-header entry zero, which must itself be
present and bounded before dereference. [1,3,6]

| Header escape | Actual value from section zero |
| --- | --- |
| e_shnum=0 for extended section count | sh_size |
| e_shstrndx=SHN_XINDEX | sh_link |
| e_phnum=PN_XNUM (0xffff) | sh_info |

Do not interpret e_shnum=0 alone as an extended count: e_shoff=0 can identify
an absent section table. Extended numbering is a format interpretation rule,
not a promise that every OS executable loader accepts those counts. Preserve
the raw escape and decoded count separately in parser evidence.

## ELF segments versus sections

Program headers describe loading; section headers organize linking and other
file information. PT_LOAD supplies file offset p_offset, virtual address p_vaddr,
file-backed byte count p_filesz and memory byte count p_memsz;
p_filesz must not exceed p_memsz. A larger memory extent has a zero-filled
tail at initial loading. PT_INTERP names an interpreter, PT_DYNAMIC points to
dynamic information and PT_TLS describes the thread-local storage template. [2]

SHT_NOBITS sections consume memory extent without occupying corresponding file
bytes. SHT_SYMTAB and SHT_DYNSYM have different purposes; removing ordinary
symbols/debug data need not remove dynamic-linking information. Section names
are not security or code-execution evidence. [3]

For a stripped executable, preserve the complete program-header and dynamic
view before concluding that missing section names imply missing functionality.
Consult `format-elf-dynamic-linking` for dependency and relocation evidence.

## ELF virtual address to file offset

For a nonempty byte length n at link-time virtual address v within one PT_LOAD,
derive d = v - p_vaddr only after proving v >= p_vaddr. File backing requires
d <= p_filesz and n <= p_filesz - d; then file offset = p_offset + d. Also
validate that full range against actual file length with checked arithmetic.
For memory extent use p_memsz instead. A zero-filled tail has no file bytes
through this mapping. Segment permissions PF_R/PF_W/PF_X are 4/2/1. [2]

Do not choose arbitrarily between conflicting mappings in a malformed image.
Record all candidates and the relevant loader's observed choice if execution
is permitted. Declared segment flags are not a runtime memory query.

## Constructed ELF mapping and load-bias example

Hypothetical PT_LOAD: p_offset=0x1000, p_vaddr=0x4000, p_filesz=0x500,
p_memsz=0x900. An access at v=0x4120 of length 0x10 maps to file offset 0x1120.
An access at v=0x4600 lies in the memory-only tail. A read starting at 0x44f0
of length 0x20 crosses the file-backed boundary and cannot be read as one fully
file-backed range, even though the starting byte is backed.

Load bias is the difference between corresponding runtime and link-time virtual
addresses. For this example, an independently established bias of 0x70000000 maps
v=0x4120 to live VA 0x70004120. Subtract bias before file mapping. Derive bias
from corresponding mapped PT_LOAD pages; the start of an arbitrary executable
mapping is not automatically the bias. ELF mapping semantics are defined in [2].

## ELF symbol values, notes and debug identity

For an ordinary defined ET_REL symbol, st_value is section-relative. For
ordinary defined ET_EXEC/ET_DYN symbols it is a virtual address; special
symbols such as TLS, absolute, common or undefined require their own rules.
Keep st_info binding/type, st_other visibility, st_shndx and st_size together
when interpreting a symbol. A symbol name alone does not prove a call. [4]

Notes are typed records whose meaning depends on their owner/type; do not
interpret all note payloads as build IDs. GDB can associate separate symbols
using a matching build ID or a .gnu_debuglink filename plus CRC. Preserve the
binary hash too: debug association is not authentication of the specimen. [2,5]

## Sources and verification scope

Reviewed 2026-10-02. Format rules from ELF 4.3 DRAFT; platform extensions and
loader acceptance require matching psABI/implementation evidence. Numerical
examples are constructed, not observations of a loaded target.

1. [ELF header](https://gabi.xinuos.com/elf/02-eheader.html): identification, object types and table coordinates.
2. [ELF program loading](https://gabi.xinuos.com/elf/07-pheader.html): PT_LOAD, base address, permissions, notes and TLS.
3. [ELF sections](https://gabi.xinuos.com/elf/03-sheader.html): extended indexes, NOBITS, SYMTAB and DYNSYM.
4. [ELF symbols](https://gabi.xinuos.com/elf/05-symtab.html): binding, type, visibility and symbol-value interpretation.
5. [GDB separate debug files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html): debug-link and build-ID matching.
6. [Linux elf(5)](https://man7.org/linux/man-pages/man5/elf.5.html): extended program/section counts and indexes.
