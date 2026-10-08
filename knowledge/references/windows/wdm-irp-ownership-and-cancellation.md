---
id: reference-windows-wdm-irp-ownership
title: WDM IRP forwarding, pending, completion and cancellation ownership
kind: reference
topics: [windows, drivers, wdm, irp, cancellation, completion, lifetimes]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Recover who may access or finish a WDM request

WDM is the Windows Driver Model. An IRP (I/O request packet) carries an operation
through a device stack, the participating layers of drivers. Its I/O stack
locations hold per-layer parameters and completion metadata; these are not
machine call-stack frames. A saved IRP address identifies storage, not permission
to access that storage after forwarding or completion. [1,2,3]

## Forwarding transfers access; a saved pointer is not ownership
Reviewed 2026-10-02. IoCallDriver wraps IofCallDriver, which returns NTSTATUS
and sends the IRP to the driver for the supplied device object. The caller must
prepare the target stack location. The forwarded IRP is inaccessible to the
upper driver except through its registered completion routine; lower stack
locations are zeroed by the time that routine receives it. [1]

Investigative consequence: the macro page's empty return-value description
does not make IofCallDriver a void function. Decode the imported function and
ABI correctly. Do not read Irp->IoStatus after an unretained pass-through call
just because the pointer remains in a register. Dispatch return, eventual I/O
status and regained ownership are different evidence.

## Skip shares a stack slot; copy prepares another
IoSkipCurrentIrpStackLocation makes the lower driver receive the same
IO_STACK_LOCATION. It is for forwarding without a completion routine. Setting
one after skipping can overwrite an upper driver's completion routine. A
driver that has pended the IRP must not skip before forwarding: the lower driver
can overwrite the shared pending flag. Use a separate prepared stack location
instead. [2] IoCopyCurrentIrpStackLocationToNext copies request parameters to
the next slot, normally followed by completion registration. [3]

Reversing consequence: these helpers do not mean copying the entire request
or transferring buffer ownership. Recover Parameters, Control and completion
registration order. Changes to a shared slot can affect another layer, not just
the current function's local state.

## Mark pending before publishing a queued IRP
IoMarkIrpPending must precede queue publication; another routine can dequeue,
complete and release the IRP before the publisher resumes. Once marked, the
dispatch routine returns STATUS_PENDING even if completion already occurred
before dispatch returns. [4]

Constructed interleaving: enqueue R; worker completes R; dispatch marks R.
The last action accesses a potentially released request. Moving the mark before
publication addresses this ordering obligation, but does not prove cancellation,
queue locking or final completion are correct. STATUS_PENDING is not a final
successful result, nor evidence that the request is still alive when observed.

## Pending propagation is conditional on the completion pattern
For an ordinary forwarded IRP whose completion continues upward, inspect
PendingReturned and propagate pending with IoMarkIrpPending when set. Completion
routines do not return STATUS_PENDING. A driver-created IRP sent to another
stack must not be marked pending by its creator's completion routine when that
creator has no stack location. The documented forward-and-wait pattern instead
signals an event and returns STATUS_MORE_PROCESSING_REQUIRED. [4]

Do not turn a missing IoMarkIrpPending into a finding without classifying the
IRP's origin and the completion pattern. An upper-layer forwarding callback,
a request creator and a synchronous retention callback have different duties.

## Completion return controls unwinding, not the request's result
An IoCompletion routine returns STATUS_MORE_PROCESSING_REQUIRED to stop
completion processing; otherwise it normally returns STATUS_SUCCESS. The I/O
manager distinguishes that stop value, not arbitrary callback error statuses.
The request result lives in IoStatus.Status. A retained request still needs its
owner's later completion or allocator-appropriate disposal. [5]

The callback can run in an arbitrary thread or DPC context at IRQL <=
DISPATCH_LEVEL. It is not guaranteed to run exactly at DISPATCH_LEVEL or in the
original process. Its context must be nonpaged. [5] Do not return
an application error from the callback and assume it changes the I/O result;
do not dereference an original user VA there without a valid mapping/context.

## Completion registration and disposal depend on IRP origin
IoSetCompletionRoutine's InvokeOnSuccess/Error/Cancel flags determine callback
coverage. Its caller must ensure its code cannot unload too early; otherwise
IoSetCompletionRoutineEx supplies unload protection. For IRPs allocated with
IoAllocateIrp or IoBuildAsynchronousFsdRequest, Microsoft requires all three
flags and creator cleanup. A callback freeing that IRP returns
STATUS_MORE_PROCESSING_REQUIRED to prevent further I/O-manager processing. [6]

This is not a rule that every driver-created IRP is freed with IoFreeIrp.
Identify the actual allocation helper before judging ownership. Missing error
or cancel callback coverage can strand resources if no other path owns cleanup;
prove that path, not merely the presence of one FALSE argument.

## Synchronous IOCTL construction is a different ownership contract
IoBuildDeviceIoControlRequest creates a synchronous IRP which the I/O manager
frees after completion: its caller must not IoFreeIrp it. It associates the IRP
with the current thread; thread exit triggers cancellation. The event and
IO_STATUS_BLOCK supply completion evidence. The returned RequestorMode starts
as KernelMode, and supplied input/output buffers must be system memory. [7]

Copying untrusted user operands into such a request does not make them trusted.
Microsoft requires validating those values or using UserMode when they must
remain untrusted. [7] Investigate a deputy that rebuilds a request and silently
changes the lower driver's validation assumptions. A timeout does not establish
that the event, status block or buffers are no longer referenced.

## Completing under a spin lock can deadlock
IoCompleteRequest wraps IofCompleteRequest and starts completion processing up
the driver stack. It must not be called while holding a spin lock; callbacks can
cause deadlock. Its maximum IRQL is DISPATCH_LEVEL. [8]

Investigation consequence: detach a request from protected shared state under
the appropriate protocol, then establish who owns completion outside that lock.
Do not apply a simplistic textual rule that any lock/unlock pair proves safety:
another path may complete or free the same request after the lock is released.
Likewise, returning from IoCompleteRequest is not permission to keep accessing
an IRP already returned to the I/O manager.

## IoCancelIrp reports callback invocation, not final cancellation
IoCancelIrp sets the IRP cancel bit. TRUE means a cancel routine existed and was
called; FALSE means none was called, not that the bit remained clear. The request
can still complete successfully despite the cancel bit. The API warns against
canceling an IRP the caller does not own. [9]

Do not treat either Boolean as a join with completion, permission to release
buffers, or proof of STATUS_CANCELLED. Recover the completion owner and actual
terminal status. A cancel path and normal completion path need a synchronized
ownership handoff; the flag alone does not serialize them.

## Clearing the cancel routine can lose to cancellation
IoSetCancelRoutine returns the previous callback pointer. NULL can mean no
previous routine or cancellation already in progress. For I/O-manager device
queues the cancel spin lock is required; drivers with their own queues can use
other synchronization around the atomic callback exchange. A cancel routine
runs at DISPATCH_LEVEL with the cancel spin lock held and must release it before
returning. [10]

Consequently, NULL from IoSetCancelRoutine(Irp,NULL) is not universal proof
that the normal path owns completion. Recover the queue/cancel state protocol,
which path removed the IRP, and which path may still access it. An atomic
pointer exchange alone does not protect every queue link or lifetime.

## Cancel-safe queues cover queued requests, not all device activity
The IoCsq framework coordinates insertion/removal and queued cancellation via
driver-provided queue, lock and canceled-completion callbacks. Drivers using
it do not supply a separate Cancel routine for those queued IRPs. [11]

Investigative inference: after successful dequeue, follow the active operation's
own cancellation and hardware-quiescence protocol. An IoCsq import does not
prove that all requests use the queue or that an active DMA/callback has stopped.
Constructed invariant: exactly one path removes a queued request and assumes
its completion duty; every later asynchronous reference must finish before
that owner's buffers/context are released.

## Sources: forwarding and completion
Primary contracts reviewed 2026-10-02; no kernel execution claimed.

1. [IofCallDriver](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iofcalldriver).
2. [IoSkipCurrentIrpStackLocation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-ioskipcurrentirpstacklocation).
3. [IoCopyCurrentIrpStackLocationToNext](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocopycurrentirpstacklocationtonext).
4. [IoMarkIrpPending](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iomarkirppending).
5. [IO_COMPLETION_ROUTINE](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-io_completion_routine).
6. [IoSetCompletionRoutine](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iosetcompletionroutine).

## Sources: construction and cancellation
7. [IoBuildDeviceIoControlRequest](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iobuilddeviceiocontrolrequest).
8. [IoCompleteRequest](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocompleterequest).
9. [IoCancelIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocancelirp).
10. [IoSetCancelRoutine](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iosetcancelroutine).
11. [Cancel-safe IRP queues](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/cancel-safe-irp-queues).
