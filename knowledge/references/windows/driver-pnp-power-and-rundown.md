---
id: reference-windows-driver-pnp-power-rundown
title: Driver cleanup, PnP state, power ordering and remove-lock rundown
kind: reference
topics: [windows, drivers, pnp, power, cleanup, removal, lifetimes]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Separate handle closure, stopped hardware and deleted software state

PnP (Plug and Play) manages device discovery, configuration and removal. Rundown
means preventing new uses and waiting for existing users before releasing state;
it is not synonymous with closing one handle. The sections below describe WDM
(Windows Driver Model) requests. KMDF framework callbacks have their own
ownership contracts in reference-windows-kmdf-request-ownership.

## CLEANUP is not CLOSE and is not device removal
Reviewed 2026-10-02. IRP_MJ_CLEANUP means the last handle to that file object
closed, while outstanding I/O can still retain it. It runs in the closing
process's context. For a nonexclusive device, queued cancellation is scoped to
the associated file object, not every client's queue. [1]
IRP_MJ_CLOSE follows release with outstanding I/O finished/canceled; it runs at
PASSIVE_LEVEL but not necessarily in the closing process. Process-specific
resource cleanup belongs in CLEANUP. [2]

Investigative consequence: handle count, file-object lifetime and device-object
lifetime are different. A numeric handle value or PID is not a sufficient queue
ownership key. Do not free per-file context in CLEANUP while an active request
still accesses it; recover the driver's cancellation and reference protocol.

## Function-driver START waits for the lower stack
A WDM function driver handling IRP_MN_START_DEVICE postpones its start work
until lower drivers finish successfully. Raw and translated resource lists are
paired; translated memory resources supply physical addresses requiring
MmMapIoSpace before CPU virtual access. Mappings are released on failed start,
stop and removal paths. [3]

Investigative consequence: the presence of AddDevice or a saved BAR-like value
does not prove the hardware is ready. Trace lower completion status, translated
resource type/length, successful mapping and the transition that enables queued
I/O. A raw bus address, system physical address, CPU VA and DMA/device address
are not interchangeable. A failed or partial start must not leave callbacks
using stale mappings or publish a falsely started state.

## STOP permits reconfiguration; CANCEL_STOP resumes a prior state
On Windows 2000 and later, IRP_MN_STOP_DEVICE follows a successful query-stop
and releases hardware resources for reconfiguration/restart. It is not the
required precursor of REMOVE_DEVICE, and must not be failed after accepting
query-stop. [4] CANCEL_STOP returns a stop-pending device to started operation
and restarts held IRPs; an already-active function/filter driver can pass it
through successfully. [5]

Investigative consequence: preserve state before query-stop and the outcome of
lower-stack handling. Do not interpret every stop as final deletion, or every
cancel-stop as evidence that this layer actually entered stop-pending. Resource
rebalance can change mappings; queued requests must not retain obsolete register
addresses across restart. Windows 98/Me stop behavior differs from this scope.

## SURPRISE_REMOVAL quiesces hardware without deleting the device object
WDM surprise removal signals that the device is unavailable. Drivers prevent
new device I/O, fail outstanding requests, release hardware resources and retain
their attachment/device object until REMOVE_DEVICE. Cleanup, close and PnP/power
handling still need their appropriate paths. Function/filter drivers pass the
surprise-removal IRP down; the bus driver for the child's physical device object
(PDO) completes it. [6]

Do not unconditionally detach/delete in the surprise callback or assume an open
handle means hardware is still usable. A remaining handle can delay final
REMOVE_DEVICE, so indefinitely deferring all resource cleanup until that event
can leak resources. This WDM sequence is not a recipe for directly completing
KMDF-owned requests inside a framework surprise-removal callback.

## Remove locks count outstanding uses; they are not mutual exclusion
IoAcquireRemoveLock/IoReleaseRemoveLock account for outstanding I/O and issued
timer/DPC/callback references. In a forwarding function/filter driver's
REMOVE_DEVICE path, it acquires its own reference and passes the IRP down;
IoReleaseRemoveLockAndWait then waits for remaining users
before memory release, detach and deletion. Subsequent acquisition fails; the
same remove lock must not be reinitialized for reuse. [7]

Investigative consequence: a remove lock protects rundown, not arbitrary fields
against concurrent mutation. Check acquisition failure handling, balanced release
on error/cancel, and callbacks scheduled outside the IRP path. A count reaching
zero is meaningful only if all relevant users participated. Never release the
last protection and then touch the possibly deleted extension.

## REMOVE_DEVICE is the final resource-release boundary
IRP_MN_REMOVE_DEVICE removes the software representation. It can follow orderly
or surprise removal, disabling, or driver update; before returning success the
driver must release its device resources. This may be its last call before
unload. Function, filter and bus roles have different detailed responsibilities. [8]

Investigative consequence: inspect every entry state, including partial start
and a missing prior surprise-removal path. Completion callbacks, DPCs, timers,
mapped registers and work items must not outlive the resources/code they use.
The absence of physical hardware access after removal does not prove that
software context lifetime is safe. Pair state transition evidence with the
request ownership rules in reference-windows-wdm-irp-ownership.

## Power IRP forwarding rules have an OS-era boundary
Windows Vista and later use IoCallDriver to pass power IRPs. Windows 2000,
XP and Server 2003 instead require PoCallDriver. PoStartNextPowerIrp is no
longer required from Vista and performs no power-management operation there;
older systems require it for query/set-power sequencing. [9][10]

Do not flag a modern driver solely for omitting this legacy call, or infer
correct sequencing merely because an old import remains. In the documented
WDM power path, startup work follows the bus powering the device up, while
shutdown work precedes forwarding power-down to the bus. [9] Recover direction,
system/device state, completion point and actual hardware accesses rather than
treating all IRP_MJ_POWER cases as one transition. KMDF queue-stop semantics
have their home in reference-windows-kmdf-request-ownership.

## Sources: per-file and PnP state
Primary contracts reviewed 2026-10-02; no host device was stopped or removed.

1. [IRP_MJ_CLEANUP](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-cleanup).
2. [IRP_MJ_CLOSE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mj-close).
3. [Starting a function-driver device](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/starting-a-device-in-a-function-driver).
4. [IRP_MN_STOP_DEVICE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-stop-device).
5. [IRP_MN_CANCEL_STOP_DEVICE](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-cancel-stop-device).

## Sources: rundown and power
6. [Surprise-removal handling](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-surprise-removal-request).
7. [Using remove locks](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-remove-locks).
8. [Remove-device handling](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-remove-device-request).
9. [PoCallDriver](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-pocalldriver).
10. [PoStartNextPowerIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-postartnextpowerirp).
