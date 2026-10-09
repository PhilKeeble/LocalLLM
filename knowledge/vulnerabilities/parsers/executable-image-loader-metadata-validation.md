---
id: vulnerability-parser-executable-image-loader-metadata-validation
title: Executable-image and loader-metadata validation failure
kind: vulnerability
topics: [parsers, loaders, executable-formats, pe, elf, macho, metadata, coordinates]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---

# Executable-image and loader-metadata validation failure

## Definition and violated invariant

An executable-image metadata vulnerability occurs when a loader, analyzer, verifier, unpacker, debugger, signer, or other consumer reads or acts on image metadata without enforcing the selected format, architecture, coordinate system, full-range bounds, graph structure, and semantic relationships. Every header, table, child reference, relocation, import, load command, callback, signature structure, unwind record, and mapped range must be interpreted under its actual PE, ELF, Mach-O, bytecode, or firmware-container contract.

File offsets, relative virtual addresses, preferred virtual addresses, runtime addresses, slice-relative offsets, and container offsets are different coordinates. Successful parsing by one tool does not prove format validity, target-loader acceptance, mapping, or execution. The consumer and selected architecture must be named.

## Conditions that establish the issue

Recover container and architecture selection, byte order and word size, header and table extents, entry sizes and counts, checked arithmetic, sections or segments, file-backed versus zero-filled ranges, overlap policy, address translation, load bias or slide, directories or load commands, imports and exports, relocations or fixups, TLS and initialization callbacks, signatures, exception or unwind metadata, and every nested offset. Prove attacker-controlled metadata violates a required invariant and reaches an out-of-bounds access, wrong-byte interpretation, unsafe allocation, unintended mapping, verifier/consumer disagreement, or security-relevant callback or target.

For PE, most data-directory locations are RVAs, but the security/certificate directory uses a file offset; TLS pointer fields include VAs. For ELF, program headers govern loading while section headers serve different file/linking roles. For Mach-O universal files, container offsets select slices whose internal offsets use the slice as their base. Apply the selected rule rather than one universal base addition.

## Evidence that is not sufficient

Malformed metadata, overlapping extents, an executable section, an unusual entry point, a TLS or initializer callback, stripped symbols, a signature blob, parser disagreement, tool crash, or successful load is not sufficient. The target consumer may reject or ignore the field, and metadata presence does not prove a callback ran or code executed.

A bounded parent table does not validate its child offsets. Conversely, a raw file trailer or section table may be irrelevant to the executable-loading path. Establish the actual consumer and consequence.

## Investigation sequence

Record exact file identity, container member and architecture. Build a coordinate ledger for each referenced range containing raw field, coordinate type, base, translated start, length, owning extent, file backing, runtime mapping, and arithmetic proof. Preserve all candidate mappings when malformed overlap makes interpretation ambiguous.

Walk entry paths beyond the nominal entry point, including format-defined initializers, TLS callbacks, import resolvers, dynamic-linker metadata, bytecode initializers, firmware dispatch tables, and exception-driven control data where applicable. Compare analyzer, verifier, signer, and loader interpretations without treating any one tool as the format oracle. Connect a suspicious target to an accepted mapping and reachable control flow before claiming execution.

## Constructed PE coordinate-confusion example

```c
uint32_t rva = optional_header.import_directory.VirtualAddress;
uint32_t size = optional_header.import_directory.Size;
if (rva > file_length || size > file_length - rva)
    reject();
parse_import_descriptors(file_bytes + rva, size); /* RVA incorrectly used as file offset */
```

An import-directory RVA normally requires translation through the PE headers or a section's virtual and raw coordinates before disk bytes can be read. The subtraction check avoids arithmetic wrap but proves the wrong coordinate relation; `file_bytes + rva` can select unrelated bytes even while it remains inside the file. The PE certificate directory is a documented file-offset exception, so this conclusion must not be applied to every data-directory entry.

## Constructed System V AMD64 coordinate shape

```asm
; Illustrative System V AMD64 shape. r12 = file base, r14 = file length, eax = import-directory RVA.
cmp     rax, r14
ja      .reject
mov     ecx, dword ptr [import_size]
mov     rdx, r14
sub     rdx, rax
cmp     rcx, rdx
ja      .reject
lea     rdi, [r12+rax]           ; direct file_base + RVA: no section/header translation
mov     esi, ecx
call    parse_import_descriptors
```

This addition is evidence of coordinate confusion only after proving `eax` is the selected import RVA and `r12` addresses raw file bytes. In a loaded-image view, image-base plus RVA is expected; in a file view, a helper may already have translated the value. The excerpt also does not prove the complete range is unchecked because surrounding blocks may contain additional validation.

## Primitive and impact limits

The direct primitive can be out-of-bounds read or write, integer-driven underallocation, wrong-byte parsing, uncontrolled traversal, unintended mapping or protection, verifier/loader disagreement, or attacker-selected initialization or resolution target. Loader acceptance can make a metadata target reachable, but code execution still requires an accepted control-transfer path. An analyzer-only defect may affect the analyst or analysis service without affecting the operating-system loader.

## Related knowledge and primary sources

`pe-headers-sections`, `format-pe-directories-loader-metadata`, `format-elf-structure-addresses`, `format-macho-mapping-dyld`, `format-malformed-files-loader-acceptance`, and `format-disk-versus-loaded-image` define the separate format coordinates and evidence limits. This profile repeats their critical distinctions locally.

Reviewed 2026-10-09 against Microsoft [PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), the System V ABI [ELF header](https://gabi.xinuos.com/elf/02-eheader.html) and [program loading](https://gabi.xinuos.com/elf/07-pheader.html), and Apple [`loader.h`](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/loader.h) and [`fat.h`](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/fat.h). The code and assembly are constructed and do not assert acceptance by a particular loader release.
