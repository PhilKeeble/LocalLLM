---
id: reference-windows-driver-mdl-lifetimes
title: Windows MDL construction, page locking, mappings and release duties
kind: reference
topics: [windows, drivers, mdl, user-pointers, memory-mapping, lifetimes]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Separate descriptor, pages, mapping and contents

## An allocated MDL is not a locked or mapped buffer
Reviewed 2026-10-02. An MDL (memory descriptor list) describes physical pages
backing a virtually contiguous range; those pages need not be physically contiguous. IoAllocateMdl
and MmInitializeMdl do not initialize the following page-description array.
Lock/build operations establish that description. MmGetMdlVirtualAddress returns
the described original address, not a newly valid system mapping. [1]

For reverse engineering, identify the exact MDL builder, byte count, offset,
original address space, page-lock owner and mapping owner. Do not infer residency
from the existence of MdlAddress or dereference an original user VA in an
arbitrary worker context. VA means virtual address, interpreted in its address
space; it is not a physical page address. MDL layout is semi-opaque: native offsets
observed in one WDK/build are not a cross-version serialized format.

## Probe-and-lock checks access but can raise
MmProbeAndLockPages takes AccessMode and an operation: IoReadAccess allows
examining the buffer; IoWriteAccess/IoModifyAccess allow reading and writing.
It must be inside exception handling. Pageable addresses require IRQL <=
APC_LEVEL; nonpageable addresses allow <= DISPATCH_LEVEL. Successful calls must
be matched by MmUnlockPages; the same MDL cannot be locked again before unlock. [2]

Investigative consequence: decode direction from the operation actually passed,
not an IOCTL method's name or the presence of a probe. A call without a Boolean
return can fail by exception. Cleanup must distinguish a successful lock from
an allocation followed by a failed probe; do not unlock as if both acquired
the same resource.

## Locked physical pages do not preserve the original virtual address
MmProbeAndLockPages guarantees locked physical pages after success, not continued
validity of the original VA, which can be unmapped or reused. [2] A system mapping
can provide access independent of the original process context. [1]

Investigative inference: locking is not copying or making contents immutable.
If the user retains a writable alias, fields can change between validation and
use. A length checked through one mapping and refetched through another can
still be a double-fetch candidate. Preserve a bounded captured representation
or prove another synchronization/immutability mechanism. Do not claim an MDL
alone prevents TOCTOU, validates embedded pointers or defines message lengths.

## Safe system mapping still has failure and synchronization requirements
MmGetSystemAddressForMdlSafe requires an MDL describing locked-down pages. It
returns an existing system mapping or attempts one; the latter can return NULL.
Concurrent calls for the same MDL require explicit synchronization. The returned
base already includes the described buffer's offset. From Windows 8, priority
can include MdlMappingNoWrite/MdlMappingNoExecute. [3]

Do not add the MDL byte offset a second time, treat Safe as infallible, or infer
read-only contents through every other alias from one protected mapping. Check
whether the mapping already existed before reasoning about requested protection.
The mapping does not enlarge the valid buffer beyond its byte count.

## Release duties depend on how the MDL was built
For a system mapping obtained with MmGetSystemAddressForMdlSafe:

- Probe-and-locked MDL: MmUnlockPages also releases its system mapping.
- Nonpaged-pool-built MDL: the original mapping is reused; no unlock/unmap of
  that mapping is required.
- Partial MDL: MmPrepareMdlForReuse or IoFreeMdl releases an allocated mapping.
- MmAllocatePagesForMdlEx: mapping cleanup differs; Windows 7/Server 2008 R2+
  MmFreePagesFromMdl also releases the system mapping. [3]

This is a mapping-lifetime distinction, not permission to free the MDL, backing
pool or pages while another request/device still uses them. Record each resource
and its owner separately. Do not run one generic unlock/free sequence on every
MDL regardless of construction.

## Nonpaged-pool MDLs must not be probe-locked or unlocked
MmBuildMdlForNonPagedPool describes already-resident system memory. Its MDL
must not be passed to MmProbeAndLockPages or MmUnlockPages, or remapped/unmapped
as a second system mapping. MmGetSystemAddressForMdlSafe can return the existing
address. User-space mapping is a separate supported operation with security
requirements. [4]

Kernel-stack buffers are explicitly excluded from this builder: stack physical
pages can be traded even when the stack cannot be paged out. They require the
probe-and-lock route. [4] Thus resident code or a current stack address does
not justify treating every kernel buffer as nonpaged-pool storage. Trace the
allocation provenance, not merely whether its address is above user space.

## Partial MDL zero length means the remaining source range
IoBuildPartialMdl describes a subrange of an already locked source; the target
MDL must have sufficient capacity. Length=0 means the remainder starting at
VirtualAddress, not an empty range. Existing source system mapping can be shared;
a separately created partial mapping must be released before reuse via
MmPrepareMdlForReuse, or when freeing with IoFreeMdl. [5]

Constructed byte-range model: source [0x1000,0x2800), start 0x1800, Length=0
describes 0x1000 bytes. An explicit length 0x1001 exceeds the source. Arithmetic
is not an execution of IoBuildPartialMdl. Do not unlock a partial MDL as though
it independently acquired the source's page lock; preserve source lifetime
until all dependent uses finish.

## Mapping to user space is process-specific and can disclose whole pages
MmMapLockedPagesSpecifyCache with UserMode returns a VA in the current process
and raises on mapping failure, so requires try/except and IRQL <= APC_LEVEL.
KernelMode with BugCheckOnFailure=FALSE instead returns NULL on failure and
allows <= DISPATCH_LEVEL. Drivers must use FALSE for that parameter. [6]

When exposing kernel pool to user space, initialize it and use page-multiple
allocation sizes so neighboring allocations do not share exposed pages. Do not
free the pool while the user mapping remains. User mappings are non-executable;
that does not prevent data disclosure or unauthorized writes. [6] Recover which
process was current, mapping extent, protection and unmapping context. A safe
logical message length is not sufficient evidence of safe page-level exposure.

## Sources and limits
Primary contracts reviewed 2026-10-02; no MDL was mapped or driver executed.
IOCTL transfer methods remain in reference-windows-driver-ioctl-buffer-access.

1. [Using MDLs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-mdls): descriptor creation and original VA; not a blanket teardown recipe.
2. [MmProbeAndLockPages](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmprobeandlockpages).
3. [MmGetSystemAddressForMdlSafe](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmgetsystemaddressformdlsafe).
4. [MmBuildMdlForNonPagedPool](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmbuildmdlfornonpagedpool).
5. [IoBuildPartialMdl](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iobuildpartialmdl).
6. [MmMapLockedPagesSpecifyCache](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmaplockedpagesspecifycache).
