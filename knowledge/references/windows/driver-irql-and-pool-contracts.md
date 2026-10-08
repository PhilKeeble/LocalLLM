---
id: reference-windows-driver-irql-pool
title: Driver IRQL, execution context, waits and pool allocation contracts
kind: reference
topics: [windows, drivers, irql, pool, spinlocks, waits, allocation]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Recover execution constraints, not just instruction flow

## IRQL controls legal kernel operations, not caller authority
IRQL (interrupt request level) is the executing processor's interrupt-priority
level. PASSIVE_LEVEL, APC_LEVEL and DISPATCH_LEVEL have different interruption,
paging and waiting constraints. APC means asynchronous procedure call; a DPC is
a deferred procedure call, ordinarily executed at DISPATCH_LEVEL. Higher IRQL
does not make user-controlled parameters trusted or establish a process identity.
Recover IRQL separately from address space, ownership and authorization. [8]

## Dispatch name does not establish passive caller context
Reviewed 2026-10-02. Windows driver support routines have individual IRQL
requirements, sometimes an exact level rather than only a maximum. Most
dispatch routines use PASSIVE_LEVEL, but paging-path read/write/device-control
processing can run at APC_LEVEL in arbitrary thread context. DispatchPower and
several I/O dispatch paths can reach DISPATCH_LEVEL. [1]

Do not infer original-user address space, ability to wait or pageable-code safety
from a function named DispatchDeviceControl. Recover its actual callers, driver
role, paging/hibernation path and current IRQL. A PASSIVE_LEVEL observation on one
test path does not establish all invocations. An ordinary completion callback's
separate constraints are in reference-windows-wdm-irp-ownership.

## Spin-lock protection also changes IRQL obligations
KeAcquireSpinLock raises to DISPATCH_LEVEL, acquires the lock and returns the
previous level through OldIrql; KeReleaseSpinLock must receive that saved level.
Protected code and data must not be pageable or raise exceptions. Recursive
acquisition deadlocks; sharing one OldIrql storage location across different
locks can race. [2]

Investigative consequence: an allocation/helper safe at the function's entry
level can become invalid inside its locked region. Trace every exit, callback
and error path across acquisition/release, including which saved level is used.
Raising IRQL alone is not a substitute for the actual lock protecting shared
state on other processors. Identify all participants in the protocol.

## Zero-timeout polling is not an indefinite wait
KeWaitForSingleObject Timeout=NULL means indefinite wait; a non-NULL pointer
to zero means test without waiting. NULL or nonzero timeout requires IRQL <=
APC_LEVEL and nonarbitrary thread context; zero-timeout polling permits <=
DISPATCH_LEVEL. The dispatcher object must be resident; a stack event requires
KernelMode wait because a UserMode wait can allow stack swapping. [3]

Investigative consequence: distinguish pointer value from pointed-to timeout.
A decompiler displaying a zero argument may mean NULL, not zero-duration poll.
Do not replace one with the other when evaluating a DPC or spin-locked path.
Wait legality does not prove the waited-on callback can run without another
lock or resource held by the waiter.

## NT_SUCCESS on a wait does not prove the object was signaled
KeWaitForSingleObject can return STATUS_SUCCESS, STATUS_TIMEOUT,
STATUS_ALERTED or STATUS_USER_APC; all pass NT_SUCCESS. Only STATUS_SUCCESS
identifies the documented satisfied-object result in that list. [3]

Constructed bug candidate: timeout returns a nonnegative status, a caller tests
only NT_SUCCESS, and then frees an event/status block while pending I/O still
references it. Show the outstanding reference and actual branch before claiming
use-after-free. Timeout units are 100 ns; negative values are relative, positive
values absolute. [3] Kernel wait return conventions must not be replaced with
Win32 WAIT_OBJECT_0/WAIT_TIMEOUT assumptions without checking the actual API.

## ExAllocatePool2 defaults differ from legacy pool allocation
ExAllocatePool2 is available from Windows 10 version 2004. It takes ULONG64
POOL_FLAGS, a nonzero byte count and nonzero tag. Memory is zeroed unless
POOL_FLAG_UNINITIALIZED is set. Failure normally returns NULL; the
POOL_FLAG_RAISE_ON_FAILURE option raises instead. [4]
ExAllocatePoolWithTag instead uses POOL_TYPE and returns uninitialized memory;
it was deprecated in Windows 10 version 2004, not removed by that declaration. [5]

Reversing consequence: identify wrappers and actual flag width before decoding
constants. A reused lookaside/cached object is not automatically a fresh zeroed
allocation. Zero allocation defaults also do not initialize semantic state or
justify returning more bytes than the logical output. Follow writes and lengths.

## Pool residency is constrained by later use as well as allocation
ExAllocatePool2 permits IRQL <= DISPATCH_LEVEL, but DISPATCH_LEVEL allocation
requires nonpaged pool. Allocation at <= APC_LEVEL may use paged pool only if
later users permit it; memory accessed at DISPATCH_LEVEL must still be nonpaged.
Allocations below PAGE_SIZE have 8-byte alignment on 32-bit systems and 16-byte
alignment on 64-bit systems; only the requested byte range is usable. [4]

ExFreePoolWithTag takes the allocation's beginning and original tag; paged-pool
free requires <= APC_LEVEL, while nonpaged free permits <= DISPATCH_LEVEL. [6]
Do not infer ownership, object size or initialization from a pool tag alone.
Allocator rounding and page-aligned placement do not enlarge the caller's object.

## Decode POOL_FLAGS as 64 bits and retain optional-flag limits
POOL_FLAG_NON_PAGED=0x40 requests NX nonpaged pool;
POOL_FLAG_NON_PAGED_EXECUTE=0x80 requests executable nonpaged pool;
POOL_FLAG_PAGED=0x100 requests paged pool. POOL_FLAG_UNINITIALIZED=0x2 disables
default zeroing. POOL_FLAG_SPECIAL_POOL=0x100000000 is optional: allocation may
fall back to normal pool. CACHE_ALIGNED is documented as best effort, unsuitable
as a correctness guarantee. [7]

These constants are not legacy POOL_TYPE values. Truncating a recovered flags
argument to 32 bits loses SPECIAL_POOL. An allocation request containing that
bit does not prove a guard page was actually supplied. NX pool prevents execution
from that mapping, not out-of-bounds writes, UAF or data-only corruption.

## Sources and limits
Primary contracts reviewed 2026-10-02; no kernel allocator/IRQL experiment run.

1. [Dispatch routines and IRQLs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/dispatch-routines-and-irqls).
2. [KeAcquireSpinLock](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-keacquirespinlock).
3. [KeWaitForSingleObject](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-kewaitforsingleobject).
4. [ExAllocatePool2](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exallocatepool2).
5. [ExAllocatePoolWithTag](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exallocatepoolwithtag).
6. [ExFreePoolWithTag](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exfreepoolwithtag).
7. [POOL_FLAGS](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/pool_flags).
8. [Managing hardware priorities](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/managing-hardware-priorities): execution levels and routine constraints; each API's own contract supplies its precise allowed level.
