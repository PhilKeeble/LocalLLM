---
id: reference-windows-named-pipe-security-identity
title: Windows named-pipe security and client identity
kind: reference
topics: [windows, named-pipes, dacl, sddl, impersonation, client-identity]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows named-pipe security and client identity

## Default pipe permissions are not client authentication

Named-pipe access is controlled by the pipe object's security descriptor. The
server supplies it when creating the pipe; if `lpSecurityAttributes` is NULL,
Windows assigns a default descriptor. Microsoft
documents that the default grants full control to LocalSystem, administrators,
and the creator owner, with read access for Everyone and anonymous accounts.
Therefore “only our client uses this pipe” is not an access-control property.

An access-control list (ACL) uses security identifiers (SIDs) to identify principals,
not an executable path, file hash, signer or product name. Security Descriptor
Definition Language (SDDL) represents security-descriptor fields as text; decode
owner, group, discretionary/system ACLs (DACL/SACL), entry (ACE) type, SID, rights and
inheritance rather than judging the string by a familiar substring.

The same pipe name can have multiple server instances. Capture the effective
descriptor from the actual object/build, full host/pipe name and remote-client
settings. Do not apply mutex Global/Local naming rules to pipe names; the
reviewed naming distinction is in reference-windows-object-namespaces-collisions.

## Write rights can include server-instance creation

Named-pipe FILE_GENERIC_WRITE includes FILE_APPEND_DATA, whose bit is also
FILE_CREATE_PIPE_INSTANCE. A grant intended as generic write access can thus
allow creating another server instance. Opening an existing pipe's server end
checks requested rights and FILE_CREATE_PIPE_INSTANCE against the DACL.
Individual data rights avoid unintentionally bundling that instance right. [1]
This is an access-right distinction, not proof that a particular client can
impersonate a service: actual DACL, requested flags and connection path matter.

## First-instance flag and remote-client mode

CreateNamedPipe with FILE_FLAG_FIRST_PIPE_INSTANCE fails with
ERROR_ACCESS_DENIED when the named pipe already exists. Inference: that is a
creation-time collision check, not a substitute for an appropriate pipe DACL
or lifetime-long exclusive ownership. PIPE_REJECT_REMOTE_CLIENTS rejects remote
clients; PIPE_ACCEPT_REMOTE_CLIENTS leaves them subject to security checks.
These are separate from the pipe's byte/message type and read mode. [7]

## Client identity

On success, `ImpersonateNamedPipeClient` makes the calling server thread
impersonate the security context of the last message read from the pipe.
Check its return before executing client work: failed impersonation does not
establish client authority, and continuing can use privileged server authority.
Confirm the effective token, thread and impersonation level at the operation.

End this Win32 impersonation with `RevertToSelf` and check that result too.
Failed reversion leaves client context active; it does not establish restored
server identity. Entry failure and reversion failure are different conditions.
The detailed restoration contract is in
reference-windows-tokens-sids-groups-impersonation. These API distinctions were
reviewed 2026-10-02 against the ImpersonateNamedPipeClient and RevertToSelf
references below; they are not observations of a target server.

`GetNamedPipeClientProcessId` returns a client process identifier. A PID is
diagnostic identity, not authorization: PIDs are reused, processes can exit or
change between checks, and opening a process/image introduces a separate race
and access check. If process properties are security-relevant, bind them to an
authenticated client token or protocol and define race-resistant validation.

## I/O and framing

Pipe type, per-handle read mode and wait mode are distinct. A CreateFile client
handle starts in byte-read mode even for a message-type pipe. Message-read mode
can return FALSE/ERROR_MORE_DATA after supplying part of a message; remaining
bytes belong to that message. Byte-read mode does not preserve message framing.
PIPE_NOWAIT is a legacy nonblocking mode, not overlapped asynchronous I/O. [8]

Consequently, actual transferred bytes, claimed frame length and destination
capacity are separate values. A short/partial result must not turn unwritten
buffer capacity into parser input. Reassembly must bind fragments to the same
connection and protocol frame; reconnect is not continuation of old authority.

## ConnectNamedPipe return value and connection generation

ConnectNamedPipe can return zero with ERROR_PIPE_CONNECTED when a client
connected between pipe creation and the connect call; that is a valid
connection. Zero/ERROR_IO_PENDING instead means an asynchronous connect is
outstanding, not complete. A FILE_FLAG_OVERLAPPED handle requires a valid
OVERLAPPED pointer; NULL can incorrectly report completion. [9]

With PIPE_NOWAIT, an initial nonzero result can merely announce availability
after disconnection, not prove that a new client is connected. Reusing an
instance requires DisconnectNamedPipe before connecting another client. [9]
Inference: connection state, pending I/O and cached client identity must be
tracked per generation. See reference-windows-overlapped-io-lifetime-cancellation
for lifetime facts and playbook-vr-windows-cross-boundary for investigation.

## Sources

Pipe permission, mode and connection contracts reviewed 2026-10-02. These are
documented API rules, not observations of a deployed service's security.

- [1. Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights)
- [Named Pipe Client Impersonation](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-client-impersonation)
- [ImpersonateNamedPipeClient](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient): success context and failed-entry handling.
- [RevertToSelf](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-reverttoself): reversion result and remaining client context.
- [GetNamedPipeClientProcessId](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-getnamedpipeclientprocessid)
- [Security descriptor string format](https://learn.microsoft.com/en-us/windows/win32/secauthz/security-descriptor-string-format)
- [7. CreateNamedPipeW](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew): first-instance and remote-client flags.
- [8. Named Pipe Type, Read, and Wait Modes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-type-read-and-wait-modes): client defaults, partial messages and NOWAIT.
- [9. ConnectNamedPipe](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe): result/state combinations and instance reuse.
