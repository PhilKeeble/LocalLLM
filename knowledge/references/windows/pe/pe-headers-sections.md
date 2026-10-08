---
id: pe-headers-sections
title: PE headers sections addresses imports and Windows protection values
kind: reference
topics: [pe, exe, dll, headers, sections, permissions, rva, imports, exports, virtualprotect]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# PE technical reference

Reviewed 2026-10-02 against the Microsoft format and protection contracts below.

## PE headers: PE32, PE32+ and section-table bounds
Validate MZ, e_lfanew, the PE signature, COFF header, optional-header size/magic and section-table bounds. PE32 and PE32+ differ; do not assume native structure layout matches the file.

A structurally readable header does not prove the Windows loader accepts the
image or that an analysis tool safely handles every referenced range. For parser
vulnerabilities, follow each untrusted size/offset into the actual read or copy.

## PE address mapping: RVA, file offset and runtime VA

An RVA (relative virtual address) is measured from the loaded image's base; a
file offset is measured from the first byte on disk. Runtime VA = actual load
base + RVA. For a file-backed section, offset = PointerToRawData +
(RVA - VirtualAddress), only after proving the entire requested range fits raw
data and the actual file.
Validate header RVAs separately. Overlapping mappings can be ambiguous. The certificate-table directory uses a file offset, not an RVA.

## Constructed PE mapping and boundary example
Hypothetical section: VirtualAddress=0x2000, PointerToRawData=0x600,
SizeOfRawData=0x400, VirtualSize=0x900. RVA 0x2120 maps to file offset 0x720;
RVA 0x2500 is in a virtual tail without bytes in that section's raw extent.
RVA 0x23f0 with length 0x20 crosses the raw boundary at RVA 0x2400: checking
only the first byte would incorrectly accept the complete range.

With independently observed actual load base 0x180000000, RVA 0x2120 is live
VA 0x180002120. The preferred ImageBase from disk is not necessarily the actual
base. For unsigned range checks, establish RVA >= VirtualAddress, then
d = RVA - VirtualAddress; require d <= SizeOfRawData and length <= SizeOfRawData - d.
Check PointerToRawData + d and the complete length against the actual file too.
Virtual extent, raw extent and file length are distinct bounds, not substitutes.
These are constructed arithmetic examples, not observations of a loaded image.

## Typical sections
Names are conventions, never proof. .text commonly holds instructions (RX); .rdata constants/tables (R); .data initialized writable globals (RW); .bss zero-filled globals (RW). .idata contains import metadata/tables; .rsrc resources; .reloc base relocations; .pdata/.xdata architecture-dependent unwind/exception data; .tls thread-local data. Inspect actual flags, bytes and directories. Runtime permissions can differ after loading or protection changes.

## PE section Characteristics: code content and R/W/X access bits

These masks apply to IMAGE_SECTION_HEADER.Characteristics, not VirtualProtect
or VirtualQuery PAGE_* values. R/W/X means read/write/execute.

| Mask | Flag |
| --- | --- |
| 0x00000020 | IMAGE_SCN_CNT_CODE |
| 0x00000040 | IMAGE_SCN_CNT_INITIALIZED_DATA |
| 0x00000080 | IMAGE_SCN_CNT_UNINITIALIZED_DATA |
| 0x20000000 | IMAGE_SCN_MEM_EXECUTE |
| 0x40000000 | IMAGE_SCN_MEM_READ |
| 0x80000000 | IMAGE_SCN_MEM_WRITE |

Content flags do not grant access. Test access masks independently and preserve other flags. 0x60000020 declares code + RX; 0xC0000040 initialized data + RW; 0xE0000020 code + RWX. A section named .text with 0xC0000040 is not declared executable merely because of its name.

## Windows PAGE_* protections: VirtualProtect and current memory

Windows PAGE_* values describe memory protection, not PE section Characteristics.
Decode the complete API field in this domain:

| Base value | Constant |
| --- | --- |
| 0x01 | PAGE_NOACCESS |
| 0x02 | PAGE_READONLY |
| 0x04 | PAGE_READWRITE |
| 0x08 | PAGE_WRITECOPY |
| 0x10 | PAGE_EXECUTE |
| 0x20 | PAGE_EXECUTE_READ |
| 0x40 | PAGE_EXECUTE_READWRITE |
| 0x80 | PAGE_EXECUTE_WRITECOPY |

PAGE values are base enumerations, not independent R/W/X bits. Decode modifiers separately: PAGE_GUARD=0x100, PAGE_NOCACHE=0x200, PAGE_WRITECOMBINE=0x400; combinations depend on the API. 0x120 is execute/read plus guard. A requested VirtualProtect value is not proof of success; check results or current mapping.

Executable or RWX memory alone does not prove malicious execution. For a claimed
code-loading path, connect the producing write, affected range and control
transfer. For a vulnerability, establish the invalid operation separately from
the protection state that may constrain its consequence.

## Ambiguous permission observations
An isolated "permission 0x20" leaves actual writability UNKNOWN. Obtain its field/API, complete value, any masking and whether it describes disk or current memory. In section Characteristics 0x20 is code content; in the PAGE domain it is execute/read. A partial content flag says nothing about omitted write bits. Do not conclude "non-writable in either domain." Hex 0x20 equals decimal 32, not decimal 20. File declarations do not establish live access.

## PE imports: name, ordinal, IAT and actual call targets
Imports can be by name or ordinal. Validate descriptor, thunk and string bounds; thunk width depends on PE32/PE32+. Distinguish lookup metadata from the IAT and disk values from resolved runtime addresses.
IAT means import address table. Recover the call site and its arguments rather
than assigning behavior from an imported function name alone.
An imported API suggests capability, not a proven call path; inspect callers and arguments. Missing static imports do not rule out runtime resolution or delay loading.

## PE exports: ordinal indexes and forwarded exports

Export names map through ordinal indexes into the export address table; unnamed
exports exist. An export address within the export-directory range identifies a
forwarder string, not an instruction address. Bound that string. Follow the
forwarded destination before attributing implementation behavior to the exporting
module; an export name alone neither identifies its instructions nor proves use.

## Primary PE and protection sources

Sources: [PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), [IMAGE_SECTION_HEADER](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_section_header), [memory protection constants](https://learn.microsoft.com/en-us/windows/win32/memory/memory-protection-constants).
