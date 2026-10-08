---
id: reference-windows-heap-identity-diagnostics
title: Windows NT heap, LFH, segment heap, CRT wrappers and diagnostic evidence limits
kind: reference
topics: [heap, lfh, segment-heap, crt, pageheap, windbg, heapvalidate, allocator-identification]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# Identify the allocator before interpreting its metadata

## Allocator identity includes implementation, instance and wrapper

For a Windows user-mode allocation, record OS build/servicing identity, process
architecture, loaded ntdll/CRT identity, heap handle, allocating wrapper and
diagnostic settings. The same exported HeapAlloc call can reach different heap
implementations; the call name does not identify the internal metadata format.
Allocator-aware diagnostic evidence can help distinguish NT and segment heaps,
but its decoder must support the captured implementation. WinDbg's !heap is one
documented example supporting both families. [1]

Interpretation rule: an NT heap segment is not automatically a segment-heap
implementation. An allocation wrapper can return an interior user region of
a larger backing block. Keep application object, wrapper allocation, heap block
and virtual-memory reservation as distinct extents. Unknown custom arenas or
managed allocations must not be forced through an NT-heap header decoder.
Use reference-windows-heap-allocation-contracts for documented API behavior.

## Low-fragmentation heap policy is not a universal block layout

Microsoft's low-fragmentation heap (LFH) overview scopes its older details to XP/Server 2003;
Vista and later use LFH as needed. That overview describes a size-bucket policy
within a heap, not a separate heap, and an approximately 16-KB implementation
limit. [2] Do not promote that historical threshold to every modern allocator.

For HeapQueryInformation with HeapCompatibilityInformation, the documented
ULONG values are 0 for standard, 1 for look-aside support, 2 for LFH enabled.
The query can fail; inspect its result before consuming the output. [3]
This is not a documented complete enumeration of every current heap backend.
An LFH-enabled heap does not establish that this particular block took an LFH
path. Record the block's observed allocation path and relevant size class.

## SegmentHeap manifest declaration is not a private structure definition

The heapType element in the 2020 WindowsSettings namespace accepts SegmentHeap
to override the default Win32 heap implementation. Support begins at Windows 10
2004/build 19041; other values are ignored. [4] This dates the manifest option,
not the first existence of segment heap.

Investigation: preserve the effective manifest, target OS and observed heap
type. A declaration does not supply structure offsets, guarantee every wrapper
uses that heap, or describe private heaps created with different requirements.
Microsoft's VS 2026 18.6 announcement describes Segment Heap configuration for
new C++ projects. [5] Do not infer an existing binary's allocator solely from
the installed IDE version or assume every rebuilt older project opted in.

## Historical segment-heap components: explicit build boundary

Mark Yason's 2016 primary analysis concerns x64 ntdll 10.0.14295.1000, Windows 10
preview build 14295. It identifies backend allocation, variable-size (VS), LFH,
and large-block components. VS/LFH subsegments obtain backing from the backend;
an inactive LFH bucket can route a small request to VS. [6, pp.5-10]

For that build, LFH bitmap-managed blocks and separately tracked large blocks
do not share the VS per-block header representation. [6, pp.24-35] Consequently,
subtracting one guessed header size from every returned pointer is invalid.
These are historical implementation observations, not current Windows ABI
promises. Match target symbols and instructions before applying any private
offset, encoding, bucket boundary or adjacent-block rule. Absence of a familiar
header is not by itself proof of corruption.

## Version-specific hardening does not establish application memory safety

Yason's build-14295 analysis describes encoded VS metadata, LFH allocation
randomization, and consistency checks that fail fast on damaged list/tree
links. [6, pp.36-41] These observations must not be generalized into a current
decoder, predictable reuse order or a guarantee that all corruptions terminate.

On Windows Vista and later, HeapSetInformation's HeapEnableTerminationOnCorruption
requests process termination when the heap manager detects an error; once enabled it cannot be
disabled in that process. [7] Detection is the condition, not every out-of-bounds
write. An in-object overwrite or dangling read may violate application rules
without breaking allocator metadata. Report the demonstrated invalid access
separately from unproved downstream exploitability or mitigation bypass.

## CRT debug heap user pointer differs from its backing block

MSVC debug CRT allocation adds bookkeeping and guard regions around the user
data, returning the user-region pointer. Its documentation describes 0xFD guard
bytes, 0xCD newly allocated data and 0xDD retained freed data when delayed-free
checking is enabled. The published structure is conceptual, not a portable
constant-offset decoder. [8]

Investigation: verify the loaded debug CRT and flags before interpreting these
patterns. A matching byte pattern alone does not prove allocation state; an
application can store the same bytes. Direct HeapFree of a debug CRT user pointer
is not justified by discovering a backing Win32 heap. Allocation/release family
and heap instance must match; the common DLL ownership rule lives in
reference-native-ownership-release-dangling. Shared UCRT code does not make
distinct heaps interchangeable. [9]

## HeapValidate reports allocator consistency, not an owning reference

HeapValidate with NULL lpMem checks heap control structures; a non-NULL lpMem
restricts validation to that allocated block. It returns nonzero for validity,
zero for invalidity, and does not set last error. Validation may be costly and
block other heap users. [10]

Interpretation: a successful check does not prove correct application fields,
initialized payload, subtype, subobject bounds or the lifetime of a prior object
at a reused address. It does not retain the block after return. A concurrent
release can occur before the subsequent access. Do not add HeapValidate as a
substitute for ownership or as an arbitrary-pointer authorization gate.
For WinDbg LFH checking, the extension documents !heap -triage rather than its
ordinary NT !heap -v validation option. [1] Tool options are not API synonyms.

## Heap enumeration does not pin handles or freeze a changing heap

GetProcessHeaps returns the active heap count; if larger than supplied capacity,
only that capacity of handles is stored and the caller must retry. Zero is
failure. Another component can destroy a returned private heap after the call;
enumeration does not extend its lifetime. [11]

HeapWalk starts with lpData=NULL and continues with unchanged enumeration state.
FALSE with ERROR_NO_MORE_ITEMS means the normal end, not detected corruption.
Unlocked enumeration can fail when concurrent operations change the heap; heap
locking can block other threads. [12] Capture errors before unrelated calls
overwrite last error. A failed or incomplete walk is not evidence that missing
allocations never existed. Prefer an appropriate captured diagnostic snapshot
over injecting uncoordinated API walks into a busy target.

## Tail-pattern checks and guard pages detect different access violations

Tail-pattern checking can expose an overwrite when the pattern is later inspected;
an inaccessible guard page can instead fault when an access reaches that page.
These mechanisms do not detect identical ranges or report at the same time.
In Windows PageHeap, standard mode checks tail fill patterns on free; full mode
uses an inaccessible boundary page and consumes substantially more memory. [13]

## Diagnostic configuration changes layout and survives beyond one run

Windows PageHeap image settings persist in the registry until explicitly changed, and
must be active before process launch; enabling/disabling them does not switch
an already running instance. The GFlags checkbox alone does not distinguish
standard from full mode. [13]

Investigative limit: boundary-page detection is not byte-level validation of
every subobject or semantic field. Instrumentation can change layout, reuse
and timing. Record the exact mode and compare the original fault with the
instrumented one. Use only an authorized disposable test instance; do not
silently change global GFlags, restart shared services or assume reboot removes
settings. A clean instrumented run covers its exercised paths, not all inputs.

## Containing-block evidence does not prove application ownership

An allocator-aware address lookup can identify a containing allocation, whereas
allocation/free history depends on what instrumentation recorded and retained.
A containing block is not automatically the application object's base or proof
of live ownership. Preserve allocator instance, generation, address range and
history coverage independently; missing history is not proof of no prior free.

WinDbg's !heap documents containing-block and PageHeap-history facilities, but
support differs by heap family and extension version. [1] These observations
must not be inferred from an arbitrary readable-memory region or an unsupported
decoder's failure. Keep the actual diagnostic output and its interpretation limits.

## Allocator stop categories distinguish detection from root cause

Application Verifier's Heaps stops distinguish switched heap handle (0x6),
double free (0x7) and generic corrupted block (0x8). Its delayed-free evidence
is finite; reuse can prevent a double-free diagnosis. [14] Preserve stop code,
parameters and allocation/free histories. A crash in allocator code can be the
detection point of an earlier overwrite, not the original bad instruction.
Do not assign a specific cause from generic corruption alone.

## Sources: identity and implementation scope

Reviewed 2026-10-02. User-mode Windows only. No private offsets are supplied as
universal constants; no segment-heap internals were locally reproduced.

1. [WinDbg !heap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap): shared/NT options, LFH validation, page-heap evidence and version caveats.
2. [Low-fragmentation heap](https://learn.microsoft.com/en-us/windows/win32/memory/low-fragmentation-heap): historical scope and policy.
3. [HeapQueryInformation](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapqueryinformation): documented compatibility values/results.
4. [Application manifests](https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests#heaptype): heapType support and namespace.
5. [Microsoft C++ team: Segment Heap project support](https://devblogs.microsoft.com/cppblog/segment-heap-support-for-c-projects-in-visual-studio/): VS 2026 18.6 new-project configuration, not binary attestation.

## Sources: historical internals and CRT

6. [Mark Yason, Windows 10 Segment Heap Internals, 2016](https://blackhat.com/docs/us-16/materials/us-16-Yason-Windows-10-Segment-Heap-Internals-wp.pdf): original researcher paper, numbered pp.5-10,24-41; x64 ntdll 10.0.14295.1000. Only scoped structural/hardening facts summarized here, not its exploit case study.
7. [HeapSetInformation](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapsetinformation): termination-on-detected-corruption.
8. [CRT debug heap details](https://learn.microsoft.com/en-us/cpp/c-runtime-library/crt-debug-heap-details?view=msvc-170): user region, conceptual header, guard and fill patterns.
9. [CRT objects across DLL boundaries](https://learn.microsoft.com/en-us/cpp/c-runtime-library/potential-errors-passing-crt-objects-across-dll-boundaries?view=msvc-170): distinct CRT/heap state.

## Sources: diagnostic contracts

10. [HeapValidate](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapvalidate): scope, results and cost.
11. [GetProcessHeaps](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-getprocessheaps): capacity/retry and stale handles.
12. [HeapWalk](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heapwalk): state, end/error and synchronization.
13. [GFlags and PageHeap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-and-pageheap): modes, launch boundary and persistence.
14. [Application Verifier basic stops](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/application-verifier-stop-codes-basics): Heaps codes 0x6-0x9 and delayed-free limits.
