---
id: reference-windows-dep-aslr-policy
title: Windows DEP, ASLR, dynamic-code restrictions and runtime policy evidence
kind: reference
topics: [windows, mitigations, dep, aslr, memory-protection, runtime-policy]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Separate image declarations, process policy and mapped-page state

An image flag describes that image; a successful policy query describes a
particular process; a memory query describes pages at an observation point.
None alone establishes that an identified coding defect is absent or exploitable.
These are user-process contracts, not a complete kernel mitigation inventory.

## DEP blocks execution from protected data pages, not data corruption
Reviewed 2026-10-02. Windows Data Execution Prevention (DEP) makes protected data
pages non-executable; attempted execution raises STATUS_ACCESS_VIOLATION. Explicitly executable
allocations remain possible under DEP, including dynamic-code applications.
DEP is not a comprehensive defense against exploitation. [1]

Investigative consequence: separate the corrupting read/write from a subsequent
execute fault. NX (no-execute protection) does not establish object bounds,
ownership, authorization or the integrity of data used by existing executable code. An executable allocation
is not proof that DEP is disabled. Record the faulting access and actual page
protection rather than infer execution permission from a section name.

## NX_COMPAT is a declaration; a failed query is not DEP disabled
MSVC /NXCOMPAT marks DEP compatibility; /NXCOMPAT:NO declares incompatibility. [2]
Hardware DEP is always enabled for native 64-bit programs on 64-bit Windows;
32-bit program behavior depends on configuration. [3] Therefore absence of an
NX-compatible marker is not sufficient evidence that a 64-bit process lacks DEP.

GetProcessDEPPolicy is documented for 32-bit targets, with ERROR_NOT_SUPPORTED
for 64-bit targets. Treat this as the documented support boundary, not an
architecture-detection method. Its output flags describe enablement,
while its lpPermanent describes whether that setting can change. [4]
Do not reinterpret a failed query's untouched zeroed buffer as a measured
disabled policy. The different PROCESS_MITIGATION_DEP_POLICY structure has its
own Enable and Permanent members; do not substitute its layout for this API. [5]


## DYNAMICBASE and HIGHENTROPYVA have architecture and dependency conditions
Address space layout randomization (ASLR) randomizes virtual address placement;
it does not establish application object bounds. MSVC /DYNAMICBASE requests
randomized image rebasing and allocation randomization on supported Windows;
it applies to 32- and 64-bit images. /DYNAMICBASE:NO is
unsupported for ARM, ARM64 and ARM64EC targets. [6]
/HIGHENTROPYVA is ignored for 32-bit images. For 64-bit images it requires
/DYNAMICBASE and /LARGEADDRESSAWARE; the documented build guidance applies it to
the executable and dependent modules. [7]

Investigative consequence: inspect the exact module and machine type, not just
the main executable's label. A preferred ImageBase is not its measured load
address. Do not assign a universal entropy-bit count from one flag or extrapolate
a single process's placement to every module, boot or architecture.

## Mandatory rebasing and randomized placement are different evidence
Exploit Protection can force relocation of images that did not opt in. Microsoft
warns that forced rebasing alone adds no entropy; bottom-up randomization supplies
the additional randomization. Its stripped-image option can reject images lacking
relocation information rather than allowing their preferred-base placement. [8]

PROCESS_MITIGATION_ASLR_POLICY exposes EnableBottomUpRandomization,
EnableForceRelocateImages, EnableHighEntropy and DisallowStrippedImages as
separate fields. [9] A zero force-relocate bit is not proof that opted-in images
have no ASLR. Conversely, a nonpreferred load address proves displacement, not
its unpredictability. Relocation parsing remains in the PE-format references.

## Query success and target identity precede interpreting policy bits
GetProcessMitigationPolicy takes a process handle, a policy selector, a matching
output structure and its byte size. It requires PROCESS_QUERY_INFORMATION and
returns BOOL success; FALSE requires error interpretation. Windows 8 introduced
the API, but later policy classes have their own support requirements. [10]

Record PID/process generation, architecture, OS/build, selector, buffer size,
success/error and returned fields. A failed or unsupported query means unknown,
not disabled. Do not label a debugger/helper's self-query as target evidence.
Stored Exploit Protection application settings take effect on program restart;
a configuration snapshot is not by itself a measurement of an already-running
instance's policy. [8] No policy mutation is necessary for this read-only check.

## VirtualQuery reports regions, not object boundaries or a lasting guarantee
VirtualQuery examines the calling process; VirtualQueryEx addresses another
process. The result is a consecutive region with matching attributes and the
return is a byte count, zero on failure. Modified copy-on-write image pages can
still report MEM_IMAGE, not MEM_PRIVATE. [11]

Investigative consequence: record current Protect separately from original
allocation characteristics. Region size is not the size of a C/C++ object.
Successful inspection does not pin a mapping against concurrent free/reprotect.
MEM_IMAGE does not prove bytes still match disk. Compare content and provenance
before treating a module's static section permissions as its runtime state.

## Dynamic-code policy is an additional restriction, not another name for DEP
PROCESS_MITIGATION_DYNAMIC_CODE_POLICY.ProhibitDynamicCode restricts code
generation and modification of existing executable code. AllowThreadOptOut
permits thread policy exceptions; AllowRemoteDowngrade permits specified
external relaxation. The documentation warns against treating thread opt-out
as strong security. [12]

Investigative consequence: recover exception flags and the acting thread, not
only the prohibition bit. An import of VirtualProtect does not prove a successful
executable transition under the target's policy. A legitimate out-of-process JIT
or permitted exception must be distinguished from a demonstrated policy bypass.
These restrictions do not validate parser lengths or operation authorization.

## Sources: DEP and image options
Primary documentation reviewed 2026-10-02. No target mitigation was changed.

1. [DEP operation](https://learn.microsoft.com/en-us/windows/win32/memory/data-execution-prevention).
2. [MSVC NXCOMPAT](https://learn.microsoft.com/en-us/cpp/build/reference/nxcompat-compatible-with-data-execution-prevention?view=msvc-170).
3. [Hardware DEP applicability](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/determine-hardware-dep-available): native 64-bit versus configurable 32-bit scope.
4. [GetProcessDEPPolicy](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getprocessdeppolicy).
5. [PROCESS_MITIGATION_DEP_POLICY](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_dep_policy).
6. [DYNAMICBASE](https://learn.microsoft.com/en-us/cpp/build/reference/dynamicbase-use-address-space-layout-randomization?view=msvc-170).
7. [HIGHENTROPYVA](https://learn.microsoft.com/en-us/cpp/build/reference/highentropyva-support-64-bit-aslr?view=msvc-170).

## Sources: runtime observations
8. [Exploit Protection reference](https://learn.microsoft.com/en-us/defender-endpoint/exploit-protection-reference): application settings and mandatory ASLR; not a universal entropy measurement.
9. [ASLR policy fields](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_aslr_policy).
10. [GetProcessMitigationPolicy](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocessmitigationpolicy).
11. [VirtualQuery](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualquery).
12. [Dynamic-code policy](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_dynamic_code_policy).
