---
id: format-disk-versus-loaded-image
title: Disk bytes versus loaded images, fixups and observed protections
kind: reference
topics: [loaders, memory-mapping, relocations, protections, image-comparison, evidence]
platforms: [windows, linux, android, freebsd, macos, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Disk and loaded-image evidence

## Comparison coordinates and identity
Reviewed 2026-10-02. A file offset, relative/link-time address and runtime address
are different coordinates. Record binary hash, selected architecture/slice,
process/module identity, actual mapping base or slide, capture time and complete
range before comparing bytes. A dump is not automatically an executable file
with its original raw layout.

Use `pe-headers-sections`, `format-elf-structure-addresses` and
`format-macho-mapping-dyld` for their distinct mapping formulas. A virtual byte
without file backing cannot be compared to the byte at an invented file offset.
An uncollected page is unknown, not evidence that its contents were zero. A
module name or matching symbol ID alone does not prove identical code bytes.

## Initial zero fill versus later state
ELF PT_LOAD with p_memsz greater than p_filesz has an initially zero-filled
memory tail; SHT_NOBITS does not occupy corresponding file bytes. PE section
VirtualSize greater than SizeOfRawData similarly describes zero-filled excess
on loading. [1][2] These initial-image rules are not promises about later values:
initializers and application writes may have changed the storage before capture.

Constructed case: a global counter begins in a zero-filled tail and is 9 in a
dump. This difference alone is not evidence of a patched executable or an
uninitialized read. Establish when initialization, writes and observation occurred.
Conversely, zero-filled storage does not imply a live C++ object of any arbitrary
type; object lifetime remains a separate language/ABI question.

## Relocations, binding and ordinary mutations
PE base relocations can adjust specified image locations when loading away from
the preferred base; the IAT can contain resolved addresses instead of its disk
lookup values. ELF relocations and dynamic symbol binding likewise modify
designated locations. [1][2] Mach-O rebasing/binding and encoded chained fixups
are covered by `format-macho-mapping-dyld`, not a universal add-slide-to-every-word
rule.

For comparison, keep a transformation ledger: affected range, relocation/fixup
kind, symbol/addend or base, expected result and actual observed bytes. Do not
mask a whole section merely because it contains one legitimate fixup. Different
addresses can be expected; an unexplained target remains unresolved. Breakpoints,
instrumentation and application writes are hypotheses requiring their own evidence.

## File metadata need not remain mapped
PE IMAGE_SCN_MEM_DISCARDABLE permits a section to be discarded as needed; it
does not prove when or whether a particular mapping was discarded. PE debug
information can be outside mapped sections: a debug directory's AddressOfRawData
may be zero for unmapped data while PointerToRawData locates it in the file. [1]

Thus missing debug bytes in a memory capture do not establish disk corruption.
Similarly, a raw file trailer is not necessarily mapped executable content.
Record whether the range was absent from the mapping, inaccessible to the reader,
omitted by the dump format or simply not requested. Those observations have
different implications; none by itself establishes deliberate concealment.

## Windows current protection and copy-on-write
Windows VirtualQuery reports regions of pages with matching attributes in the
calling process; VirtualQueryEx addresses another process. Current protection
is not the same field as PE section Characteristics or initial allocation
protection. Query success, region range and observation time matter. [3]

A modified copy-on-write page can still be reported as MEM_IMAGE or MEM_MAPPED,
not MEM_PRIVATE. [3] Therefore MEM_IMAGE is not proof that bytes equal the
backing image. Conversely, current executable permission does not prove that
execution occurred. Preserve permissions and byte comparisons as distinct
observations; do not derive one from the other.

## Linux maps evidence and its limits
Linux /proc/pid/maps reports address ranges, permissions, file offset, device,
inode and optional pathname. The p permission denotes private copy-on-write;
s denotes shared. Anonymous regions can lack a pathname and inode association.
The appended deleted marker can be ambiguous, as can escaped newlines. [4]

Use address, offset and object identity together rather than reopening a displayed
pathname and assuming the same bytes. The displayed mapping permissions are
an observation, not a guarantee about a future access or unchanged process.
Constructed case: a path is replaced after mapping; hashing the new path alone
does not authenticate the already mapped object. Preserve the captured mapping
and any accessible backing-object evidence without asserting unavailable identity.

## Sources and investigation boundary
Reviewed 2026-10-02. Mapping/protection contracts below are platform-specific;
the comparison ledger is investigation guidance, not a universal loader algorithm.
No target process or untrusted executable was run to establish these examples.

1. [Microsoft PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): section sizes/flags, debug directory, relocations and imports.
2. [ELF program loading](https://gabi.xinuos.com/elf/07-pheader.html) and [dynamic linking](https://gabi.xinuos.com/elf/08-dynamic.html).
3. [Microsoft VirtualQuery](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualquery): region attributes and copy-on-write reporting.
4. [Linux proc_pid_maps(5)](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html): mapping fields and pathname caveats.
