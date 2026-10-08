---
id: reference-windows-kmdf-request-ownership
title: KMDF request send, cancellation, completion and power-stop ownership
kind: reference
topics: [windows, drivers, kmdf, requests, cancellation, completion, power]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Do not substitute WDM IRP rules for framework request rules

KMDF (Kernel-Mode Driver Framework) represents I/O with framework request objects
identified by WDFREQUEST handles. WDM (Windows Driver Model) represents it with
IRPs, or I/O request packets. A framework object and its underlying IRP are not
one interchangeable lifetime: retaining the former does not retain all access
rights to the latter. [4]

## Send success is not operation success
Reviewed 2026-10-02. WdfRequestSend returns TRUE when the request was sent;
FALSE means it was not sent, with failure available via WdfRequestGetStatus. [1]
Investigative consequence: recover send options, target and completion callback
before interpreting the Boolean. For an asynchronous send, TRUE does not prove
the device operation succeeded or that buffers can be freed. A failed-send
branch must retain a clearly identified completion/cleanup owner; a successful
send must not be followed by unsynchronized reuse of the outstanding request.

These sections target KMDF semantics. Some linked APIs also support UMDF, but
kernel IRQL and WDM IRP access conclusions are not portable user-mode rules.

## MarkCancelableEx failure and UnmarkCancelable cancellation differ
WdfRequestMarkCancelableEx (KMDF 1.9+) returns STATUS_CANCELLED if cancellation
already occurred. The Ex call does not invoke EvtRequestCancel itself; the
driver handles the failed-mark cleanup path. Invalid ownership or an already
cancelable request can instead produce STATUS_INVALID_DEVICE_REQUEST. [2]

Do not wait for a callback that failed registration never promised. Equally,
do not interpret every failure as an already-canceled, valid owned request.
Trace successful ownership, mark result and synchronized worker state before
completing. The older WdfRequestMarkCancelable has different callback/deadlock
considerations; matching a similar name is insufficient evidence of Ex behavior.

## UnmarkCancelable losing the race leaves completion to cancellation
For a marked KMDF request, normal completion first disables cancellation with
WdfRequestUnmarkCancelable. If it returns STATUS_CANCELLED, that normal path
must not complete before EvtRequestCancel is called; doing so can hand the
callback an invalid request. After the callback completes the request, that
request must not be used. An extra WdfObjectReference does not permit calling
UnmarkCancelable after completion. [3]

This differs from STATUS_CANCELLED returned by MarkCancelableEx. Recover exact
callee, status branch and synchronization scope. A normal callback and cancel
callback each unconditionally calling WdfRequestComplete is a candidate double
completion only if both are feasible for the same request generation.

## Forwarding into another queue changes the cancel owner
A request must not remain marked cancelable when passed to WdfRequestForwardToIoQueue.
While queued, the framework owns cancellation; EvtIoCanceledOnQueue is the
notification hook for driver-owned auxiliary resources. After redelivery, the
driver may mark it cancelable again. [2]

Investigative consequence: distinguish queue ownership from driver-owned active
processing and from a request sent to an I/O target. A cached WDFREQUEST value
does not establish current ownership. Resource context must survive the handoff
without two independent paths freeing it or an unobserved queued cancellation
leaking it. Do not substitute WDM IoSetCancelRoutine on a framework-owned request.

## An object reference does not retain the completed IRP or its buffers
After WdfRequestComplete, the request handle is invalid unless an extra object
reference retains the framework object. Even with that reference, the driver
must not access the associated WDM IRP, including through
WdfRequestRetrieveInputBuffer or WdfRequestRetrieveOutputBuffer. [4]

Investigative consequence: WDF object lifetime, IRP validity and backing buffer
lifetime are separate. A reference count that keeps a context object alive does
not authorize post-completion access to request memory. Trace final use before
completion; cross-link raw buffer/MDL provenance to
reference-windows-driver-mdl-lifetimes.

## EvtIoStop is an ownership and power transition, not automatic completion
For a registered power-managed queue, EvtIoStop handles outstanding requests
when the device leaves D0, including sent requests. SEND_AND_FORGET from a request
handler is a documented exception; forwarding from another thread can differ. ActionFlags distinguish
suspend/purge/cancelable circumstances. The driver needs exclusive request
access before completing, requeuing or acknowledging a stop. With
WdfRequestStopRequestCancelable it must unmark before completion/requeue and
respect the cancellation-race result. [5]

WdfRequestStopAcknowledge(FALSE) postpones processing without requeue; TRUE
returns the request for requeue. Taking no action waits for completion and can
block power transitions. EvtIoStop can run up to DISPATCH_LEVEL unless configured
for passive execution. [5] Do not infer that a stop callback itself drains
hardware, cancels every child request, or permits freeing in-flight buffers.

## Sources and limits
Primary contracts reviewed 2026-10-02. No KMDF driver loaded or verifier enabled.

1. [WdfRequestSend](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestsend): return value; options must be recovered per target.
2. [WdfRequestMarkCancelableEx](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestmarkcancelableex): registration failure and queue handoff.
3. [WdfRequestUnmarkCancelable](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestunmarkcancelable): losing cancellation and object-reference limits.
4. [WdfRequestComplete](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestcomplete): request versus IRP lifetime.
5. [EvtIoStop](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfio/nc-wdfio-evt_wdf_io_queue_io_stop): ownership, action flags and execution level.
