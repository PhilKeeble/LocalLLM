---
id: reference-windows-wow64-layouts-views
title: WOW64 caller layouts, IOCTL thunking, machine detection and filesystem registry views
kind: reference
topics: [wow64, thunking, ioctl, structure-layout, registry-views, filesystem-redirection, thread-context]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# WOW64 representation and view boundaries

## Process machine and native machine are different observations

IsWow64Process2 returns BOOL success, not the WOW64 classification itself.
On success, pProcessMachine is IMAGE_FILE_MACHINE_UNKNOWN when the target is
not a WOW64 process; otherwise it identifies the emulated process machine.
pNativeMachine identifies the host's native architecture. Failure is zero with
GetLastError available. The process handle needs query or limited-query access.
The API is documented from Windows 10 version 1709. [1]

Interpretation: UNKNOWN is not an error when the call succeeded and does not
mean "x86". Record both outputs and the queried PID. A process-level result
does not classify every instruction range in a hybrid module. Do not infer
target pointer width from the analysis tool's own build or from a copied
environment variable. ARM64EC needs abi-windows-arm64ec-boundaries.

## System-service thunking is not arbitrary structure conversion

WOW64 translates supported 32-bit service arguments before native kernel entry.
The existing windows-native-service-boundaries reference owns that transition
model. For DeviceIoControl, however, WOW64 converts the outer buffer pointers
but does not translate driver-defined input/output buffer contents. Embedded
pointer-precision fields require a protocol-specific conversion by the driver
or a representation that avoids the width dependency. [2]

Investigative consequence: METHOD_BUFFERED does not make an embedded 32-bit
pointer into a 64-bit pointer or capture the memory it points at. Recover each
field's width, offset, signedness and meaning before following it. An outer
buffer length check must select the caller's actual layout, not merely the
driver compiler's sizeof. This is distinct from proving safe pointed-to memory
access, ownership or authorization.

## IoIs32bitProcess must describe the original request

IoIs32bitProcess(Irp) tests whether the original I/O request came from a 32-bit
user-mode process. The non-NULL argument must be the I/O-manager-issued IRP,
not a driver-allocated IRP. NULL is for context-dependent use, including fast
I/O; in a user-process context it tests that process. [3]

Inference for deferred work: NULL on a worker thread is not evidence of the
original caller's architecture. Preserve request provenance before forwarding
or queueing. TRUE indicates likely conversion needs, not that a supplied length,
pointer or version is valid. Microsoft's example chooses separate 32-bit/native
structures and validates the appropriate input size before field conversion. [4]
Do not interpret its abbreviated sample as a complete secure driver.

## Width, packing and range checks belong to the selected wire layout

Constructed default-packed MSVC structure: ULONG tag; void *buffer; SIZE_T length;
ULONG flags. Under x86 its field offsets are 0/4/8/12 and size 16; under x64 they
are 0/8/16/24 and size 32. These are layout calculations for the stated
ABI and packing, not measurements of an arbitrary target.
A 16-byte caller buffer cannot be read as the latter 32-byte structure merely
because a driver is 64-bit. A byte at offset 12 has different interpretations.

Fixed-width fields reduce width ambiguity but do not alone specify packing or
alignment; Microsoft documents platform-dependent alignment of fixed-precision
structures. Its historical Itanium example is not a current x64 layout table. [5]
Recover the actual ABI/packing and validate each accessed range before decoding.
For an explicit serialized format, use that format's offsets, not a host cast.

## Handle interoperability is not generic pointer truncation

Microsoft documents lower-32-bit significance and truncation/sign-extension
interoperability for shareable Windows handles. It also documents cross-bitness
named objects, RPC, COM local servers and suitably defined shared memory. [6]
This does not make arbitrary memory pointers or every typedef named HANDLE
portable. A pointer is also relative to an address space, not just a bit width.

Investigation: identify whether a field is an OS handle, pointer, offset, opaque
cookie or application ID before extending it. Cross-process handle use still
needs the relevant sharing/duplication and access contract; copying a number
does not transfer authority. Shared-memory offsets need bounds and object-lifetime
checks in the receiver. Equal numeric values do not prove equal objects.

## System32, SysWOW64 and Sysnative are not interchangeable strings

For WOW64 x86 accesses, System32 is generally redirected to SysWOW64; documented
exceptions include drivers\etc and several other subdirectories. The native
System32 directory is not simply "the 32-bit directory". Sysnative is a virtual
alias through which 32-bit applications can reach the native system directory;
64-bit applications cannot use that alias. It exists from Vista onward. [7]

Inference: record the caller architecture, thread state and resolved file, not
just the source path text. A verifier in one process and a consumer in another
can open different files from the same spelling. Windows on Arm adds distinct
architecture considerations; do not universally label every System32 file x64.
See reference-windows-arm-hybrid-images for ARM64X's loader-dependent views.

## Disabling filesystem redirection is thread-local and needs restoration

Wow64DisableWow64FsRedirection affects the calling thread's file operations.
Its opaque OldValue must remain unchanged and be supplied to a matching
Wow64RevertWow64FsRedirection after a successful disable. Work performed on a
different thread is not covered. Disabling can disrupt DLL/delay loading, and
an initial delay-load failure can remain cached after restoration. [8]

Investigation: trace success, ordinary exit and exceptional cleanup around a
short intended scope. This is not process-wide architecture selection, registry
view selection or permission bypass. A later DLL failure may reflect a leaked
redirection state rather than a missing installation. Do not change the analyst's
or another process's redirection state merely to inspect a path.

## Registry view flags select a namespace, not additional rights

WOW64 normally selects the caller's 32-bit or 64-bit registry view for redirected
keys. KEY_WOW64_64KEY=0x0100 and KEY_WOW64_32KEY=0x0200 select alternate views;
shared keys are unaffected. Child open/create/delete operations need consistent
flags. Enumerating both views requires separate passes. Wow6432Node and
WowAA32Node are reserved implementation paths, not stable API substitutes. [9]

Inference: record root, key path, view and granted rights. A missing value in
one view does not prove global absence; selecting the other view does not grant
write access. Filesystem redirection controls do not select registry views.
The documented Windows 10 ARM32/x86 view split is an additional platform case,
not permission to assume all Windows releases expose identical views.

## Registry sharing, reflection and redirection are different mechanisms

The WOW64 registry redirector splits only selected portions of the namespace;
shared keys refer to one physical copy. Historical reflection copied selected
keys between views on XP/Server 2003/Vista/Server 2008. Reflection was removed
starting with Windows 7/Server 2008 R2. [10]

Investigation: establish the target version and key's documented classification
before assuming a write propagates to another view. A compatibility fallback
that accepts a different view may read a different policy or COM registration.
Compare the actual values and their security descriptors; redirection alone
neither demonstrates a bypass nor creates an isolation boundary against callers
with access to both views.

## WOW64 thread context is a selected view, not a validity guarantee

Wow64GetThreadContext uses WOW64_CONTEXT with initialized ContextFlags and
THREAD_GET_CONTEXT access. The requested flags select which state is returned.
Microsoft warns that a running thread cannot yield a valid context this way;
calling it on the current thread can succeed while returning invalid context. [11]

Interpretation: save the stop/suspension evidence, context type and requested
flags. Do not decode WOW64_CONTEXT as native x64 CONTEXT or take success alone
as a coherent register snapshot. Inspect an authorized stopped target or suitable
dump; do not suspend unrelated user workloads. Context structure layouts and
TEB/PEB offsets require matching architecture and version, not a universal
offset copied from a different debugger session.


## Sources: machine and data boundaries

Reviewed 2026-10-02. User-mode WOW64 plus explicitly scoped driver thunking.
No undocumented transition opcode or TEB/PEB offset is assumed.

1. [IsWow64Process2](https://learn.microsoft.com/en-us/windows/win32/api/wow64apiset/nf-wow64apiset-iswow64process2).
2. [Supporting 32-bit I/O](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/supporting-32-bit-i-o-in-your-64-bit-driver): outer pointers versus payload.
3. [IoIs32bitProcess](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-iois32bitprocess): original IRP and NULL-context rules.
4. [Thunking example](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/extended-example--using-iois32bitprocess): separate size checks/conversion.
5. [Fixed-precision alignment](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/avoiding-misalignment-of-fixed-precision-data-types): principle, not its historical platform constants.
6. [Cross-bitness IPC](https://learn.microsoft.com/en-us/windows/win32/winprog64/interprocess-communication): handles, named objects and shared memory.

## Sources: views and context

7. [Filesystem redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/file-system-redirector): exceptions and Sysnative.
8. [Disable redirection](https://learn.microsoft.com/en-us/windows/win32/api/wow64apiset/nf-wow64apiset-wow64disablewow64fsredirection): thread scope, restoration and delay-load failure.
9. [Alternate registry views](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view): flags and child operations.
10. [Registry redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/registry-redirector): shared keys and historical reflection.
11. [Wow64GetThreadContext](https://learn.microsoft.com/en-us/windows/win32/api/wow64apiset/nf-wow64apiset-wow64getthreadcontext): selected state and invalid current-thread result.
