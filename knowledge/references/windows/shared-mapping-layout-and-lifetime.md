---
id: reference-windows-shared-mapping-evidence
title: Windows shared mappings, offsets, view rights, publication and lifetime
kind: reference
topics: [windows, shared-memory, file-mapping, bounds, synchronization, mapping-lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Reconstruct mapping objects and process-local views
Scope: Win32 file mappings and mapped views. A backing file, mapping object,
handle, local view and application record are different entities; evidence
about one does not establish every other's size, ownership or protection.

## CreateFileMapping can return an old object with its old size
Reviewed 2026-10-02. CreateFileMappingW may open an existing named mapping;
success then reports ERROR_ALREADY_EXISTS and retains the current size, not
the requested size. Creating the mapping object does not itself map a view. [1]

Constructed request asks for 0x10000 bytes but opens an existing 0x1000-byte
mapping. The successful handle is not evidence of a 0x10000-byte view. Follow
MapViewOfFile arguments, return and actual extent before validating accesses.
Do not treat a supplied creation descriptor as proof of the security or origin
of an object that already existed; inspect the returned object's descriptor
and provenance. Name scope/collision facts:
reference-windows-object-namespaces-collisions.

## Fresh paging-file storage is not fresh protocol state on every open
INVALID_HANDLE_VALUE as CreateFileMapping's backing handle selects paging-file
storage and requires a positive size. Unnamed mappings can be shared through
inherited/duplicated handles; named ones can be opened by name. Participants
still need local views and synchronization. [2] Initial paging-file-backed
pages are zero, but extending a disk-backed file does not universally promise
zero-filled added bytes. [1]

Constructed second participant opens an existing mapping and assumes its
zero-valued ready field implies this caller owns initialization. Neither a
CreateFileMapping call nor a zero header proves a fresh protocol generation.
Recover creator election, initialization completion, schema version and reuse
rules. Anonymous does not mean unshared when a handle was transferred.

## Mapping-handle rights and view protections use distinct contracts
OpenFileMapping checks requested rights against the mapping descriptor. [3]
File mappings do not support SYNCHRONIZE. FILE_MAP_ALL_ACCESS excludes
FILE_MAP_EXECUTE and, at MapViewOfFile, means a read/write view. FILE_MAP_COPY
is a view flag, not an access right to put in a DACL; copy-on-write mapping
requires read access. [4]

Constructed dump shows FILE_MAP_ALL_ACCESS. Do not label the view executable
from that name alone. Record mapping protection, handle grant and requested/
observed view protection separately. A data view must have compatible creation
protection. SEC_IMAGE is a different case: image contents determine protections
and MapViewOfFile's desired-access argument does not select them. [1][5]

## File coordinates and view coordinates differ
MapViewOfFile's start offset must follow system allocation granularity, not
merely page size. A zero byte-count maps from that offset to the mapping's end.
[5] For wanted file offset O and byte count N, align down to B, use delta=O-B,
and request enough view bytes for delta+N, with checked arithmetic. [6]

Constructed granularity=0x10000, O=0x23456, N=0x300: B=0x20000,
delta=0x3456, required view bytes=0x3756; minimum mapping end=0x23756.
This granularity is an example, not a hard-coded platform promise. The data
address is returned_view_base+delta, not returned_view_base+O. Check the entire
range against actual view/mapping extents and target SIZE_T width before use.

## Shared layouts need relative offsets with a defined origin
Views may occupy different addresses in different processes. MapViewOfFileEx
can request a base but can fail if unavailable; matching address availability
across participants is not guaranteed. Microsoft recommends offsets rather
than stored pointers. [7]

Constructed whole-mapping views at 0x10000000 and 0x70000000 contain a record at
relative offset 0x120. Its local addresses are 0x10000120 and 0x70000120; a raw
pointer written by the first process is not a portable reference for the second.
Specify whether offsets are mapping-, view- or record-relative. For unsigned
offset o, length n and retained extent L, require o<=L then n<=L-o before forming
the local range; still check alignment, record type/version and arithmetic width.
Cross-bitness layouts need explicit field widths, not native pointers/size_t.

## A read-only view does not freeze another participant's writes
Sharing a mapping requires coordination of accesses. [2] Read-only protection
limits this view's writes; it is not evidence that all other views are read-only
or that a multi-field record is a stable snapshot.

Constructed consumer checks shared length=16, then later reloads length=4096
after another participant writes it. Establish actual reloads and a feasible
mutation interval before claiming a double fetch. Validate and consume retained
values under an evidenced protocol; copying a pointer is not copying its data.
Even a private multi-field copy can capture mixed versions during publication.
Detailed proof obligations and limits:
reference-concurrency-mutable-validation-double-fetch.

## Copy-on-write is private modification, not shared publication
With FILE_MAP_COPY, a write makes that page private to the writing process;
those changes do not write back to the original file. [5] Thus a constructed
publisher that modifies a copy-on-write view cannot infer that its new record
was published to a peer's shared view. Copy-on-write is also not evidence of an
atomic snapshot of a whole multi-page protocol at mapping time.

VirtualQuery can still report modified copy-on-write pages as MEM_MAPPED or
MEM_IMAGE, not MEM_PRIVATE. [8] A debugger region label alone therefore does
not prove that modifications remain shared. Preserve mapping mode, page-level
evidence and the observed reader result; distinguish a classification label
from a proof of cross-process visibility.

## VirtualQuery reports a page region, not an application record boundary
VirtualQuery describes consecutive pages with matching attributes and allocation
origin, stopping when attributes change. Its returned region may start inside
an allocation and is not automatically the entire view. [8]

Constructed protocol record declares 48 valid bytes inside a 4096-byte mapped
page. A readable page does not authorize reading a 64-byte record or disclosing
the remaining bytes. Recover mapping bounds, committed/readable regions and
validated protocol extent independently. Adjacent readable memory is not proof
that an offset belongs to the same record, mapping generation or owner.

## Abandoned mutex acquisition does not validate shared state
WaitForSingleObject returns WAIT_ABANDONED=0x80 when a previous mutex owner
terminated without releasing it; ownership is granted to the caller, but
protected persistent state needs consistency checking. WAIT_OBJECT_0=0,
WAIT_TIMEOUT=0x102 and WAIT_FAILED=0xFFFFFFFF have different meanings. Closing
the waited handle while a wait is pending has undefined behavior. [9]

Constructed writer dies between storing offset and length. The next mutex owner
must not treat ownership as proof of a committed record. Recover rollback,
generation or validation logic. Conversely, treating every nonzero result as
ordinary timeout loses track of acquired ownership on the abandoned path and
can omit a required release. A notification event and a mutex have different
state/ownership rules.

## Coherence is not a transaction or a durability guarantee
Windows documents coherence for relevant local shared file views, with exceptions
for writable remote mappings across machines and no guaranteed coherence with
ReadFile/WriteFile access. [7] These rules do not supply an application-level
atomic multi-field update or replace synchronization.

FlushViewOfFile initiates dirty-page writes but does not flush file metadata or
wait for hardware-cache persistence. Microsoft specifies FlushViewOfFile then
FlushFileBuffers for data-plus-metadata flushing; network-server caching adds
another boundary. [10] A successful flush is not itself a transactional commit
or peer acknowledgement. State which failure model and API sequence support a
claim of persistence; do not infer durability from mere visibility to a reader.

## A live mapping can fault after successful creation
Accessing a disk/remote-file view can raise EXCEPTION_IN_PAGE_ERROR because
later paging I/O fails, for example after a server connection is lost. Microsoft's
handling guidance requires associating the failing access with the relevant
mapping rather than swallowing unrelated exceptions. [11]

For this exception, the inaccessible virtual address is ExceptionInformation[1],
not ExceptionAddress, which identifies the instruction where the exception occurred.
Check ExceptionCode and NumberParameters before interpreting the array; the
underlying paging status is ExceptionInformation[2]. [14] A faulting instruction
in one module can be accessing an unrelated mapped-data region.

Constructed parser's map call succeeds but a later header load faults. Map
success did not guarantee every future read. Recover the exception edge,
partially initialized outputs and cleanup before treating the operation as
completed. Error recovery is not evidence that already-consumed partial data
was valid, and blanket exception suppression is not a bounds check.

## View lifetime is not the mapping-handle lifetime
Closing backing-file or mapping handles can succeed while views remain mapped.
UnmapViewOfFile removes a view from the calling process and requires the original
returned base, not an interior data pointer. [12][13]

Constructed code saves view_base+0x3456, closes its mapping handle, then continues
using the view: the close alone does not prove a use-after-unmap. Conversely,
successful unmap invalidates aliases in that view even if another mapping handle
is still open. Track each process's views, original bases, borrowers and
cleanup results. Remaining peer views are not proof that this process's address
is still valid, and unmapping is not a synchronous disk-flush guarantee.

## Creation and protection sources
Reviewed 2026-10-02; documented Win32 contracts. All examples are constructed;
no native mapping or exception experiment is claimed.

1. [CreateFileMappingW](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-createfilemappingw): existing size, creation versus view, zeroing and SEC_IMAGE.
2. [Sharing files and memory](https://learn.microsoft.com/en-us/windows/win32/memory/sharing-files-and-memory): backing, transfer and coordination.
3. [OpenFileMappingW](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-openfilemappingw): descriptor-based requested access.
4. [Mapping access rights](https://learn.microsoft.com/en-us/windows/win32/memory/file-mapping-security-and-access-rights): COPY, ALL_ACCESS, EXECUTE and SYNCHRONIZE distinctions.

## View and observation sources
5. [MapViewOfFile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffile): offset/count, image exception and copy-on-write.
6. [View within a file](https://learn.microsoft.com/en-us/windows/win32/memory/creating-a-view-within-a-file): aligned base and intra-view delta.
7. [MapViewOfFileEx](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-mapviewoffileex): address availability, relative offsets and coherence limits.
8. [VirtualQuery](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualquery): page-region scope and copy-on-write classification.
9. [WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject): result codes, abandoned ownership and pending-wait lifetime.

## Failure and lifetime sources
10. [FlushViewOfFile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-flushviewoffile): metadata, hardware and remote limits.
11. [Reading/writing file views](https://learn.microsoft.com/en-us/windows/win32/memory/reading-and-writing-from-a-file-view): deferred I/O faults and scoped handling.
12. [Closing file mappings](https://learn.microsoft.com/en-us/windows/win32/memory/closing-a-file-mapping-object): handles versus views.
13. [UnmapViewOfFile](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-unmapviewoffile): original base, local invalidation and delayed writeback.
14. [EXCEPTION_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-exception_record): instruction address versus inaccessible address and in-page-error status.
