---
id: reference-windows-arm-hybrid-images
title: Windows ARM64EC and ARM64X image identity, loader views and mixed-code entry evidence
kind: reference
topics: [arm64ec, arm64x, pe, hybrid-images, code-ranges, thunks, symbol-decoration]
platforms: [windows]
architectures: [arm64, x64]
---
# Windows on Arm hybrid image interpretation

## Process compatibility is not one instruction set per image

On Windows 11 on Arm, x64/ARM64EC processes can use x64 and ARM64EC modules;
classic ARM64 processes use the classic ABI. ARM64EC cannot simply link/load
ordinary ARM64 dependencies as though their conventions were compatible. [1]
ARM64EC interoperation is not a general WOW64 permission to load arbitrary
32-bit libraries into a 64-bit process.

Investigative consequence: identify the process, each loaded module and the
instruction range containing the current address. A process label alone cannot
choose a decoder for every byte. A failure to load an incompatible module is
not automatically an authorization failure. Calling-convention reconstruction
belongs to abi-windows-arm64ec-boundaries, separately from loader evidence.

## Final PE and intermediate object machine evidence differ

Microsoft's ARM64EC identification guidance shows a final image as machine 8664
(x64) with an ARM64X annotation in link /dump /headers output. Its intermediate
MSVC OBJ/LIB example instead shows A641 (ARM64EC). [1] Do not assume every
instruction in a final 8664 image is x64, or classify an executable solely from
an intermediate object's machine field.

Preserve raw headers, hybrid metadata, tool/version and whether the artifact
is an object, archive member, final image or loaded view. An annotation is
interpreted metadata, not an extra machine number concatenated onto 0x8664.
Reject neither a legitimate hybrid nor an inconsistent malformed image solely
by applying an oversimplified two-entry machine-name table.

## ARM64X contains loader-selected views, not a runtime ABI free-for-all

ARM64X can combine classic ARM64 and ARM64EC content. Windows applies
transformations exposing the appropriate code/entry information to the loading
process. Its default classic ARM64 appearance lets Windows 10 on Arm load that
view without recognizing the newer transformation scheme. [2]

Inference: disk and loaded headers/entry targets can differ legitimately.
Keep the original bytes, process architecture and transformed view separate;
do not call every difference a patch or tampering. Neither dual packaging nor
one shared filename permits an arbitrary classic ARM64-to-EC function call
without the compatible ABI view. A reverse-engineering tool needs to retain
the relevant code-range and relocation context rather than globally changing
all bytes to one disassembly mode.

## System32 on Windows 11 Arm need not contain pure x64 copies

Microsoft describes ARM64X system binaries serving classic ARM64 and x64/EC
processes from System32 on Windows 11 on Arm, without a separate pure-x64 system
directory analogous to x86 SysWOW64. ARM64X pure forwarders can select another
architecture-appropriate DLL without containing the full implementation. [2]

Investigation: follow the selected export/forwarding target and loaded module,
not just the facade path. A missing body in a forwarder is not proof that an API
does nothing. Conversely, an API name shared by views does not establish equal
instruction bytes or patch state; inspect the relevant implementation. WOW64
filesystem redirection facts live in reference-windows-wow64-layouts-views.

## Function decoration is attribution evidence, not proof of a call contract

MSVC documents an ARM64EC $$h tag in decorated C++ names and a leading # for
C-linkage ARM64EC names. Decoration depends on compiler/target and can encode
signature information. [3]

Preserve raw and demangled names separately. Export aliases, forwarding and
stripped symbols can hide the internal spelling; absence of a marker is not
proof of pure x64 code. A guessed name is not evidence that a runtime transition
preserves all registers. Match byte ranges and call-site behavior before using
a recovered signature to analyze bounds, callbacks or hidden result storage.

## Fast-forward export thunks can coexist with ARM function bodies

LLVM's 2024-08-21 PR #105499 publication adds x64 fast-forward thunks for ARM64EC
exports and patchable functions. Its regression input/output shows two export
aliases with distinct thunk RVAs leading to the same ARM64EC body, and a code
map distinguishing EC and x64 ranges. [4] This is upstream implementation/test
evidence, not a test executed in this repository or a universal linker layout.

Inference: an x64-looking prologue at an export does not prove the target body
is emulated x64, maliciously hooked or a separate application function. Follow
the thunk with the correct hybrid metadata/decoder. Do not count export aliases
as independent implementations. Historical byte sequences and section names
are not standalone signatures for every toolchain version.

## Sources and scope

Reviewed 2026-10-02. These are Windows hybrid images, not Apple Mach-O universal
files or Apple's arm64e pointer-authentication ABI. No ARM loader reproduction
was performed locally.

1. [ARM64EC overview and identification](https://learn.microsoft.com/en-us/windows/arm/arm64ec): compatibility matrix and object/final-image examples.
2. [ARM64X PE files](https://learn.microsoft.com/en-us/windows/arm/arm64x-pe): default view, loader transformation, System32 and pure forwarders.
3. [MSVC decorated names](https://learn.microsoft.com/en-us/cpp/build/reference/decorated-names?view=msvc-170): ARM64EC markers and naming scope.
4. [LLVM PR #105499 publication](https://lists.llvm.org/pipermail/llvm-commits/Week-of-Mon-20240819/1433940.html): author patch description and export-thunk regression expectations, dated 2024-08-21.
