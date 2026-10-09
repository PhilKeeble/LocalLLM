---
id: vulnerability-authorization-kernel-requestor-mode-confusion
title: Kernel access-mode, requestor-mode, or user-pointer trust confusion
kind: vulnerability
topics: [authorization, kernel, drivers, requestor-mode, user-pointers, access-checks]
platforms: [windows, linux, cross-platform]
architectures: [any]
---

# Kernel access-mode, requestor-mode, or user-pointer trust confusion

## Definition and violated invariant

A kernel requestor-mode vulnerability occurs when privileged code treats a request, pointer, handle or object name influenced by a less-trusted caller as kernel-trusted, causing validation, probing, handle-table selection or access checks to be skipped or applied under the wrong authority. Executing in kernel mode does not by itself make the originating data or request trustworthy.

Windows `PreviousMode`, IRP requestor mode and Nt/Zw behavior are one concrete family. Linux user-copy helpers express a different boundary; their contracts and return values must not be translated into Windows terminology.

## Conditions that establish the issue

Recover the original actor and request path, requestor/access-mode state, every rebuilt or forwarded request, pointer and handle provenance, selected address space and handle table, capture and validation, access checks, synchronization and lifetime, privileged operation and final object. Prove less-trusted influence is consumed under a trusted mode and bypasses a check required for that operation.

For kernel-created secondary requests, retain the original caller's authority explicitly. A default kernel requestor mode cannot authenticate user-controlled operands copied into the new request.

## Evidence that is not sufficient

A kernel pointer, Nt or Zw call, `KernelMode` constant, `copy_from_user`, probe function, IOCTL, failed access check or user-supplied address is not sufficient. Data may already be safely captured, the called API may enforce independent checks, the request may originate in trusted kernel code or the pointer may never be dereferenced.

Probing a user range does not freeze its contents or authorize the object named by those contents.

## Investigation sequence

Trace provenance from user or device input through request construction, buffer capture and forwarding. At each privileged API, record access mode, process context, handle namespace, input stability and authorization behavior. Follow return values and exception paths into the operation. Treat nested pointers and repeated user reads as separate trust boundaries.

At binary level, identify mode arguments, request flags and Nt/Zw targets, but derive semantics from the selected platform API. Track which thread and process context own raw addresses and handles.

## Hypothetical rebuilt-request example

```text
user request contains target_name
driver builds a secondary request marked KernelMode using target_name
lower component skips user-origin access validation for KernelMode requests
```

The sequence is vulnerable only if the lower component's skipped check is required for the original user, the name remains attacker-controlled, and a forbidden object operation succeeds. Rebuilding a request in kernel code is not itself a bypass when equivalent authorization is performed before forwarding.

## Primitive and impact limits

The direct primitive is a privileged memory or object operation performed under misplaced kernel trust. Impact may be kernel read/write, handle misuse or privileged object access, but each requires the specific resulting operation. Kernel execution or elevation is not implied by a mode field alone.

## Related knowledge and primary sources

Windows native-service, WDM request and IOCTL references and Linux kernel-interface references provide platform contracts. Mutable-user-memory and double-fetch profiles cover repeated reads after validation.

Reviewed 2026-10-09 against Microsoft [Using Nt and Zw Versions of Native System Services Routines](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-nt-and-zw-versions-of-the-native-system-services-routines) and [`PreviousMode`](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/previousmode) documentation for the named Windows behavior, and Linux [user-access guidance](https://docs.kernel.org/kernel-hacking/hacking.html) for its distinct copy boundary. The example is hypothetical.
