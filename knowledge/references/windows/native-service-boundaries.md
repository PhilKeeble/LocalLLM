---
id: windows-native-service-boundaries
title: Windows native service boundaries, Nt versus Zw, PreviousMode and WOW64
kind: reference
topics: [syscalls, native-api, previousmode, wow64, ntstatus]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# Windows native service and trust-boundary evidence

## Nt and Zw names do not grant user-mode kernel trust
Reviewed 2026-10-02. Microsoft's native-service contract distinguishes a user
system call from a driver calling a service. User-mode Nt and Zw counterparts
have the same parameter-trust treatment. A kernel-mode Zw call identifies its
parameters as coming from a trusted kernel source; a kernel Nt call uses the
thread's PreviousMode context. [1]

Investigation inference: a user-mode import named ZwCreateFile does not bypass
user-parameter checks simply because its spelling starts with Zw. Conversely,
a driver forwarding a caller-controlled pointer to Zw needs evidence of prior
safe capture/validation and the correct request context. The prefix alone proves
neither a vulnerability nor that the driver has checked authorization. Separate
buffer provenance, handle provenance, caller authority and the called API contract.

## PreviousMode is not identical to the currently executing privilege level
A Windows driver can execute with a thread whose PreviousMode remains UserMode.
The documented kernel Zw wrapper temporarily selects KernelMode for the service
and restores the prior value afterward. Nt leaves that context unaltered. [2]

Microsoft's example: NtClose with UserMode context does not find a kernel handle
in the user handle table and returns STATUS_INVALID_HANDLE; ignoring that result
can leave the kernel handle open. [2] This is a documented example, not a local
reproduction. While reversing a cleanup path, do not infer the handle table from
the fact that execution is inside a driver. Trace the handle's creation flags,
the request/thread context and the actual return status before declaring a leak.
Do not recommend manually editing thread internals as a fix.

## WOW64 adds a user-mode translation boundary
Microsoft documents WOW64 interception between 32-bit Ntdll and the native
kernel. Its thunks recover 32-bit stack arguments and translate them for native
entry; the described custom call sequence is intercepted in user mode. [3]

Investigation inference: a 32-bit wrapper lacking the expected native trap
instruction is not thereby a no-op, a hook or a broken service. Follow its WOW64
transition and argument conversion. Do not decode a 32-bit caller's pointed-to
structure using the native kernel's pointer size. Identify process machine,
loaded Ntdll image, native machine and translation modules independently.
The cited document includes historical platforms; it is not a byte signature
or exhaustive list of every current emulation path.

Caller layouts, driver payload conversion and namespace views are covered by
`reference-windows-wow64-layouts-views`; ARM64EC is separately covered by
`abi-windows-arm64ec-boundaries`, not by this historical 32-bit service model.

## NTSTATUS tests must match the service's outcome contract
NT_SUCCESS accepts success and informational NTSTATUS classes, not only zero.
Warning and error classes both fail NT_SUCCESS, but are not interchangeable;
warnings can accompany partial information under an API's contract. [4]

Constructed investigation: replacing a signed status test with status==0 can
discard a nonzero informational result. Treating every nonzero NTSTATUS as a
positive POSIX errno is also wrong. Identify whether the observed return is raw
NTSTATUS or a higher-level wrapper's translated result; determine which outputs
are valid for that specific status before following a length or handle. A general
success-class test alone does not prove asynchronous work has completed.

## Native API names are not a portable numeric syscall catalogue
Microsoft explicitly warns that NtQueryInformationProcess can change or become
unavailable, and recommends its documented alternatives for applications. [5]
That warning is API-specific; it does not prove every native service changes in
every release or that a particular number changed.

For binary identification, retain the target OS build, process architecture,
actual stub bytes, symbol/export identity and loaded image provenance. Treat a
numeric selector copied from another build as an unverified hypothesis. Recover
the actual stub's register/stack transformation rather than applying the ordinary
Windows function ABI directly to the trap. This reference intentionally supplies
no universal stub signature or service-number table without target evidence.

## Sources and limits
Reviewed 2026-10-02; Microsoft documentation, not execution of Windows stubs.

1. [Nt and Zw service versions](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-nt-and-zw-versions-of-the-native-system-services-routines): user versus driver parameter treatment, updated 2025-04-30.
2. [PreviousMode](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/previousmode): wrapper behavior and kernel-handle example, updated 2021-12-15.
3. [WOW64 implementation details](https://learn.microsoft.com/en-us/windows/win32/winprog64/wow64-implementation-details): interception and thunking, updated 2020-08-19; historical scope retained.
4. [Using NTSTATUS values](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-ntstatus-values): status classes and partial-information warning, updated 2025-11-05.
5. [NtQueryInformationProcess](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntqueryinformationprocess): availability warning and documented alternatives.
