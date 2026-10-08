---
id: playbook-re-driver-request-rundown
title: Trace Windows driver request ownership, memory and device rundown
kind: playbook
topics: [windows, drivers, irp, kmdf, cancellation, mdl, pnp, reverse-engineering]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Investigate a driver request across asynchronous boundaries

Track one request generation from admission to terminal completion, preserving
its owner, buffer provenance, execution context and device state. Distinguish
WDM IRPs from KMDF requests. A suspected double completion, stale mapping or
post-removal access requires a feasible path and a violated lifetime invariant.

## Establish the target and reachable entry path
Reviewed 2026-10-02. Record OS/build, architecture, driver role/framework version,
device stack, symbols and request origin. Recover device security, granted handle
rights, IOCTL access/method, RequestorMode and per-operation authorization using
reference-windows-driver-ioctl-buffer-access. Decode request/stack fields against
the matching WDK/types, not assumed universal offsets. Distinguish application
IOCTLs from internally rebuilt requests and PnP/power traffic.

For each callback record IRQL, process/thread context, held locks and whether it
can race/reenter. Use reference-windows-driver-irql-pool; do not infer passive
execution or original user address space from a dispatch-like function name.

## Build an ownership timeline before classifying a race
Identify allocation, queue publication, dequeue, forwarding, completion
registration, cancellation registration, normal completion and final disposal.
For each edge record what is transferred and what remains borrowed. Locate the
actual synchronization that selects the terminal owner, including immediate
completion before the initiating call returns. Use
reference-windows-wdm-irp-ownership or reference-windows-kmdf-request-ownership
according to the recovered framework.

Constructed WDM candidate: a normal path clears CancelRoutine and receives NULL,
then completes while a cancel callback still owns the same IRP. Preserve both
paths and the queue/lock protocol; NULL alone does not prove a bug or safe
ownership. For KMDF, distinguish failed MarkCancelableEx from a cancellation-lost
UnmarkCancelable result. Two static completion calls can be mutually exclusive.

## Give each memory resource its own lifetime
Record system buffer, original user VA, MDL descriptor, locked physical pages,
system mapping, optional user mapping, backing allocation and child-request
references separately. Identify builder/allocator, length/offset units, capture
point and matching release duty. Use reference-windows-driver-mdl-lifetimes.
Do not turn page locking into content validation or assume reference-counted
WDF context preserves a completed request buffer.

Trace arithmetic, embedded pointers and double fetches through both success and
failure paths. For exposure to user mode compare mapped page extent with
initialized allocation extent, not only returned message length. For DMA-backed
requests identify the driver-specific evidence that device access is quiescent
before release; this workflow does not infer that from a cancel flag.

## Cross the device-state boundaries and retain alternative explanations
Trace CLEANUP/CLOSE, query-stop/cancel-stop, restart, surprise removal, final
removal and power transitions that can overlap the request. Recover per-file
versus per-device context, remove-lock participants, failed-acquisition paths
and callbacks not represented by queued IRPs. Facts:
reference-windows-driver-pnp-power-rundown.

Constructed stale-register candidate: restart replaces a translated resource
mapping while a queued worker retains the old CPU VA. Demonstrate the old
mapping's release, worker scheduling and missing quiescence/version binding.
An intentional held request resumed after successful restart is not itself a
defect. Separate a deadlock/power timeout from memory corruption or privilege
gain; establish actual lower-privilege reachability for a security conclusion.

## Distinguish a vulnerable interface from malicious driver use
For a vulnerability finding, identify which caller controls the request and
which bounds, authorization or lifetime rule the feasible path violates. For
malware analysis, follow actual request codes, operands, selected objects and
effects. A powerful driver interface can be used intentionally for harmful
behavior even without a memory-safety defect. Conversely, finding a reachable
bug does not establish that the specimen uses it. Driver loading, a familiar
filename or one sensitive import alone does not establish either conclusion.

## Preserve the request evidence and limits of the conclusion
Preserve disassembly/call coordinates, request generation, status values, buffer
extents, owner transitions and the smallest invariant violation. Report contract
inference separately from observed runtime behavior. Constructed state models
can expose an inconsistent proposed timeline but cannot prove Windows scheduling,
IRQL behavior, device semantics or exploitability.

If authorized dynamic evidence is needed, driver execution requires an isolated,
recoverable target appropriate to the device and failure risk. Do not load an
untrusted driver or alter the analysis host's device/signing configuration merely
to complete a workflow. Static evidence can support a scoped contract finding;
state separately which scheduling, environment or observed-effect premise remains
unknown. No particular debugging or instrumentation product is a prerequisite.

## Source basis
Workflow synthesis reviewed 2026-10-02; no kernel experiment claimed.

- [IoCancelIrp](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iocancelirp): invocation versus final result.
- [WdfRequestUnmarkCancelable](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdfrequest/nf-wdfrequest-wdfrequestunmarkcancelable): framework handoff.
- [MmProbeAndLockPages](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmprobeandlockpages): pages versus VA.
- [Using remove locks](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-remove-locks): outstanding device uses.
