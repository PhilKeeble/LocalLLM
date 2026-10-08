---
id: format-pe-directories-loader-metadata
title: PE directory coordinates, relocations, TLS, delay loading and runtime metadata
kind: reference
topics: [pe, directories, relocations, tls, delay-imports, resources, load-config, clr, signatures]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# PE directory evidence

## PE data directories: RVA, VA and file-offset bounds
Reviewed 2026-10-02. Validate optional-header magic/size and NumberOfRvaAndSizes
before accessing a directory. Bound both directory extent and every referenced
child against the actual image/file mapping. Directory size is not proof that
an arbitrary pointer embedded in its records stays inside that directory.

An RVA is relative to the image base; a VA is a virtual address. A file offset
is relative to the first byte on disk. Most directory locations are RVAs;
the security/certificate directory location is a file offset. TLS pointer fields
and some load-configuration fields are VAs;
resource-tree offsets have another base. [1][2][3] Label the coordinate at each
step. Use `pe-headers-sections` for complete-range translation, not native host
pointer casts or one uniform base-addition rule.

## Base-relocation block decoding
A PE base-relocation block has PageRVA and BlockSize followed by 16-bit entries:
upper four bits select type; lower twelve select offset within that page. [2]
Compute each site from PageRVA plus offset, then bound the affected width.
Reject undersized, nonprogressing or truncated blocks in the analysis parser;
do not infer target-loader behavior from that parser's policy.

ABSOLUTE entries are skipped; HIGHLOW adjusts a 32-bit field and DIR64 a 64-bit
field by actual base minus preferred base. HIGHADJ consumes an additional slot.
Other type numbers can be machine-dependent. [1] Do not add the base delta to
every pointer-shaped word, decode ARM64 relocations as x86 HIGHLOW by habit,
or confuse image base relocations with COFF object-file linker relocations.

## PE thread-local storage: TLS template, index and callback entry paths
TLS here means thread-local storage, not network encryption. The PE TLS
directory supplies template addresses, an index-storage address,
callback-array address, zero-fill size and alignment information. Pointer-field
width changes between PE32 and PE32+; SizeOfZeroFill remains 32-bit. [1][2]
The TLS address fields are VAs, not RVAs. Account for relocation before mapping
a captured runtime pointer back to disk. A template is not one shared instance
of the variable across every thread.

TLS callbacks form a null-terminated pointer array with DLL-style reason
parameters. [1] Bound pointer reads and record every reachable callback, not
only AddressOfEntryPoint. Distinguish process/thread attach and detach paths;
a callback address in metadata does not prove that a particular notification
occurred. Trace thread-specific state and lifecycle when interpreting accesses.

## Delay-import descriptors and alternate resolution
PE delay-load descriptors use RVA fields when the RvaBased/dlattrRva low bit
is set; the older form uses VAs. Select the form before translating names,
IAT/INT and handle-storage locations. [1][4] The handle field locates storage;
it is not itself necessarily an already loaded module handle.

Microsoft's delay helper updates an IAT slot with the resolved function. Hooks
can supply another module or function and handle lookup failures; failures can
raise structured exceptions. [4] Therefore a delay-import name is not proof
of either startup loading or the eventual executed target. Trace hooks, failure
paths and observed slot values, including optional unload restoration, before
ascribing a call to the DLL named on disk.

## Load configuration and mitigation evidence
PE load configuration is size/version dependent. The 32-bit and 64-bit layouts
are distinct; do not read later fields beyond the available structure and
directory extent. SecurityCookie is a pointer to cookie storage, not the cookie
value itself. Microsoft's SEHandlerTable/Count contract is x86-specific;
GuardCF-related fields are separate control-flow metadata. [2][3]

Constructed case: a nonzero GuardCFFunctionTable points to data, but this alone
does not establish that every indirect call is instrumented or the running OS
enforces CFG. Preserve the table/flags, actual call sequence and runtime policy
as separate evidence. Absent fields in an older short structure are unavailable,
not permission to decode adjacent bytes using the newest SDK definition.
Runtime policy and call-site interpretation: reference-windows-dep-aslr-policy,
reference-windows-cfg-instrumentation-targets and reference-windows-cet-shadow-stack.

## PE exception directory: architecture-specific unwind metadata
For Windows x64, runtime-function records identify begin/end RVAs and unwind
information; the unwind format is not interchangeable with x86 SEH or ARM64
records. [2][5] Use `abi-windows-x64` for slot counts, chained information and
partial-prologue interpretation. Absence of one record is not proof that all
adjacent bytes are data: leaf functions and dynamic registration need separate
consideration under the relevant platform contract.

## PE debug directory: file coordinates and CodeView identity
PE debug entries have a type and separate file/memory coordinates. A CodeView
record needs its kind decoded before PDB matching. Use
`format-debug-information-build-matching` for GUID/age and
`format-disk-versus-loaded-image` for unmapped debug data. A timestamp or path
alone does not establish symbol identity or a trustworthy producer.

## Resource tree offsets versus leaf data RVAs
PE resource directory entries identify names/IDs and subdirectories or leaves;
tree offsets are relative to the resource directory base. The high subdirectory
bit distinguishes a child directory; the remaining bits carry its offset.
Leaf data entries instead contain a data RVA and byte size. [1][2]

Constructed case: adding the resource root to a leaf's DataRVA a second time
selects unrelated bytes. Track coordinate kinds while bounding names, child
tables, recursion and leaf payloads. Type/name/language describes the resource
path, not execution or trust: a manifest, icon or embedded binary still requires
its own consumer and parser. Finding an executable-looking resource does not
prove that the application extracts or runs it.

## Embedded certificate presence versus trust result
The PE certificate directory is file-based metadata, not a loaded code address.
Its presence does not establish a valid signature, accepted publisher, revocation
status or application authorization. WinVerifyTrust evaluates a specified object
under the requested provider/action and policy. Its successful result is exactly
zero; it returns LONG, not HRESULT, so SUCCEEDED is not the correct success test. [6]

Record the verified object, action, flags, environment and result separately
from locating certificate bytes. A signature check on one path does not bind a
later reopened replacement; see `reference-logic-update-verification-installation`.
Authenticity also does not imply absence of vulnerabilities or suitability for
a different product. Offline verification must state unavailable trust evidence.

## CLR header and managed/native entry distinction
The PE COM descriptor identifies IMAGE_COR20_HEADER. In .NET runtime v9.0.0's
definition, it includes metadata/resource directories, flags, entry-point union,
strong-name signature and ManagedNativeHeader. COMIMAGE_FLAGS_NATIVE_ENTRYPOINT
selects native EntryPointRVA rather than managed EntryPointToken; ReadyToRun
uses ManagedNativeHeader for its additional header. [7]

Do not disassemble a metadata token as an RVA. Discover managed methods and
native transitions separately; a CLR directory does not prove all code is IL
or all execution is JIT-generated. A strong-name signature field is not the
same object as an Authenticode certificate directory. This section establishes
format routing, not a complete CLR execution or signature-verification contract.

## Primary sources: format and helpers
Reviewed 2026-10-02. LLVM 21.1.0 is corroborating parser-layout evidence, not a
Windows loader implementation. Do not treat current documentation as a guarantee
that every historical Windows version accepts the same metadata.

1. [Microsoft PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): directories, TLS, relocation kinds, resource coordinates and delay attributes.
2. [LLVM 21.1.0 COFF object structures](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-21.1.0/llvm/include/llvm/Object/COFF.h): TLS, base relocations, load config, runtime functions and resources.
3. [Microsoft load configuration](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_load_config_directory64).
4. [Microsoft delay helper and hooks](https://learn.microsoft.com/en-us/cpp/build/reference/understanding-the-helper-function?view=msvc-170).

## Primary sources: unwind, trust and CLR
Reviewed 2026-10-02. Runtime source pinned to .NET v9.0.0; this is a header
interpretation observation, not a claim that a target runs that version.

5. [Microsoft x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170).
6. [Microsoft WinVerifyTrust](https://learn.microsoft.com/en-us/windows/win32/api/wintrust/nf-wintrust-winverifytrust).
7. [.NET v9.0.0 corhdr.h](https://raw.githubusercontent.com/dotnet/runtime/v9.0.0/src/coreclr/inc/corhdr.h): IMAGE_COR20_HEADER and native-entry flag.
