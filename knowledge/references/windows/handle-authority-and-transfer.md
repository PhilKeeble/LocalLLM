---
id: reference-windows-handle-authority-transfer
title: Windows handle authority, duplication, inheritance and release
kind: reference
topics: [windows, handles, access-rights, inheritance, duplication, resource-lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Track handle authority across process boundaries
Scope: documented Windows user-mode kernel-handle contracts. Handle grants,
object identity, process context and ownership require separate evidence;
neither an integer value nor an API name proves a successful authority transfer.

## A handle value is process-relative, not a global object identifier
Reviewed 2026-10-02. Ordinary kernel handles are process-specific; multiple
handles may identify one object while granting different rights. [1] Record
process, acquisition, object type, grant and lifetime together.

Constructed observation: processes A and B each have handle value 0x90. Numeric
equality does not establish the same object. Conversely, different values can
refer to one object. Passing the integer over IPC alone does not transfer a
kernel handle. CompareObjectHandles can compare underlying objects for valid
handles in the caller's context without demanding object-specific query rights;
it is documented from Windows 10 / Server 2016. [2] It does not make a foreign
process's raw handle value locally valid or establish equal access grants.

## An acquired I/O grant is different from a new authorization check
The I/O Manager stores granted rights with a handle and checks those rights on
later I/O; the driver can also perform required security checks. [3] Do not
substitute the worker's current token or a later DACL snapshot for the recorded
grant. This is not a claim that every operation on every Windows object ignores
current identity or additional policy.

Constructed broker trace: a file handle is acquired before client impersonation
and used afterward. Impersonation alone does not prove that this existing
handle was reopened under client authority. Establish acquisition context,
actual rights and the later operation's checks. A denied fresh open and an
operation through an already-held handle are separate evidence. Treat a claim
of revocation as unproven unless the relevant API/object contract supports it.

## DuplicateHandle transfers an existing object reference
DuplicateHandle requires PROCESS_DUP_HANDLE on the supplied source/target
process handles. The source handle belongs to the source process; the returned
value belongs to the target process, even though written into caller memory.
The duplicate references the same object. [4]

Constructed broker result: a handle duplicated into client B cannot be used or
closed locally by broker A merely because A received its numeric value. Record
which process owns the output and the IPC recipient. An output value alone
does not prove that the intended authenticated client received the authority.

## Duplication flags can defeat intended attenuation or failure cleanup
DUPLICATE_SAME_ACCESS ignores dwDesiredAccess. DUPLICATE_CLOSE_SOURCE closes
the source regardless of returned error status. Other duplication-rights limits
depend on object type: do not assume either universal amplification or universal
attenuation; a read-only file handle cannot become read/write this way. [4]

Constructed request: source grant READ|WRITE, desired READ, SAME_ACCESS set.
The desired mask does not remove WRITE. A failure path with CLOSE_SOURCE must
not assume the source is still usable or blindly close it again. Preserve both
flags, API status and ownership transition. Socket transfer requires its own
Winsock contract, not generic DuplicateHandle assumptions. [4]

## Handle inheritance preserves object and grant, not a fresh open
For ordinary CreateProcess inheritance, the handle must be inheritable and
bInheritHandles must be TRUE. An inherited handle has the same value, object
and access rights in the child. Module/GDI/USER handles and pseudo handles do
not follow this kernel-handle inheritance contract. [5]

Constructed parent owns inheritable handles {pipe, secret-file}; it intends to
pass only pipe but launches with unrestricted inheritance. The intended list
does not prove secret-file was excluded. Conversely, an inheritable flag alone
does not prove any child received a handle. Capture flags at process creation,
the actual inherited set and any explicit handle-list restriction. A parent's
later close does not itself close the child's separate reference.

## SetHandleInformation changes only the masked properties
HANDLE_FLAG_INHERIT=1 controls inheritability; HANDLE_FLAG_PROTECT_FROM_CLOSE=2
prevents CloseHandle from closing that handle. SetHandleInformation changes
only bits selected by dwMask, and its Boolean return must be checked. [6]

Constructed flags=3, mask=1, requested flags=0 produces flags=2: inheritance is
cleared while close protection remains. Passing mask=0 does not clear either
bit. Clearing inheritance is not revocation of handles already passed to a
child; close protection is not an object DACL or a confidentiality guarantee.
Keep property flags separate from access masks even when numeric bits coincide.

## Pseudo handles and owned handles have different release duties
GetCurrentProcess yields a context-relative pseudo handle, currently (HANDLE)-1;
it is not inherited and needs no close. A real handle obtained by duplicating
it does need closing. The API documents PROCESS_ALL_ACCESS for current systems
and different XP/Server 2003 behavior. [7] Do not use a raw -1 test without
knowing the producing API: another API can use that value as a failure sentinel.

CloseHandle is not a universal Windows destructor: sockets need closesocket,
search handles need FindClose. Closing a process/thread handle does not terminate
the process/thread, and closing a mapping handle need not unmap its views.
Under a debugger an invalid/pseudo handle close can raise an exception. [8]
Track handle ownership, execution lifetime and mapped-view lifetime separately.

## Handle sources
Reviewed 2026-10-02; Microsoft documented contracts, not native execution tests.
Examples are constructed. Kernel-driver handle validation has additional rules
and is not inferred from these user-mode cases.

1. [Kernel objects](https://learn.microsoft.com/en-us/windows/win32/sysinfo/kernel-objects): process-relative handles and differing grants.
2. [CompareObjectHandles](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-compareobjecthandles): identity comparison and minimum versions.
3. [Windows security model](https://learn.microsoft.com/en-us/windows-hardware/drivers/driversecurity/windows-security-model): I/O Manager grant storage and additional driver checks.
4. [DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle): process context, flags, object-specific limits and sockets.

## Inheritance and release sources
5. [Process inheritance](https://learn.microsoft.com/en-us/windows/win32/procthread/inheritance): same value/rights/object and excluded resource kinds.
6. [SetHandleInformation](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-sethandleinformation): flag mask and close protection.
7. [GetCurrentProcess](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getcurrentprocess): pseudo versus real handles and historical grants.
8. [CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle): resource-specific close and execution/view lifetimes.

General ownership: reference-native-resource-lifetimes-results. Token-object
duplication: reference-windows-tokens-sids-groups-impersonation. Child launch:
reference-windows-process-creation-context.
