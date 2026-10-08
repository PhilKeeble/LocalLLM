---
id: reference-windows-process-creation-context
title: Windows child-process identity, executable selection and inherited context
kind: reference
topics: [windows, process-creation, tokens, command-line, inheritance, startupinfo]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Distinguish the child launch decisions
Windows user-mode launch analysis must separate child token, selected image,
parsed arguments, transferred handles and observed child outcome. This reference
describes documented APIs; it does not establish any target's effective launch.

## Ordinary CreateProcess does not adopt a thread's impersonation token
Reviewed 2026-10-02. In ordinary CreateProcessW use without alternate-parent
attributes, the child uses the calling process's token, not the thread's
impersonation token. [1] Process identity, current worker identity and intended
client identity must be recorded separately.

Constructed service path: impersonate client, then call ordinary CreateProcessW.
That sequence does not establish a client-identity child. Inspect explicit-token
APIs and extended startup attributes before concluding which security context
was selected. Neither a nearby impersonation call nor the executable's signer
proves the child's identity or application-level authorization.

## CreateProcessAsUser has token, privilege and environment prerequisites
CreateProcessAsUser requires a primary-token handle with TOKEN_QUERY,
TOKEN_DUPLICATE and TOKEN_ASSIGN_PRIMARY. Typically SeIncreaseQuotaPrivilege
is needed; SeAssignPrimaryTokenPrivilege can also be required, with an exception
for a restricted version of the caller's primary token. Required available
privileges can be enabled for the call. The token's session selects the session.
The API does not automatically load the user's profile; NULL environment inherits
the caller's environment, not user-specific variables derived from hToken. [2]

Constructed child uses client token but inherits a server-controlled USERNAME
string. The variable is not proof of the child's principal. Keep token identity,
session, profile, environment and desktop access as separate launch properties;
failure to initialize the intended environment is not evidence of token failure.

## Child identity does not identify every launch-time access-check context
CreateProcessAsUser by default accesses the directory and image under the
caller's security context. Its documentation describes caller impersonation
to use the target user's context for that access; the hToken contract also
requires the target user to have read/execute access to the image. [2] Do not
confuse launch-time resource access with the child's selected primary token.

Constructed trace: the service can read an image but the intended client cannot.
Whether launch succeeds and which principal the child uses are different
questions; recover the caller's actual context, explicit token, image access
requirements and API result. A logged access-denied result is not enough to
identify which prerequisite failed. Do not generalize this API's access-context
rule to every process-creation function.

## CreateProcessWithToken and network-only logon are not interchangeable
CreateProcessWithTokenW normally uses the supplied primary token and requires
SeImpersonatePrivilege; the token handle needs TOKEN_QUERY, TOKEN_DUPLICATE and
TOKEN_ASSIGN_PRIMARY. Its documentation directs callers requiring the token's
session to CreateProcessAsUser instead. LOGON_WITH_PROFILE requests profile
loading. LOGON_NETCREDENTIALS_ONLY is a distinct mode, not ordinary token launch.
[3]

For both CreateProcessWithTokenW and CreateProcessWithLogonW,
LOGON_NETCREDENTIALS_ONLY retains the caller's local token while supplying
separate default network credentials in a new logon session; those credentials
are not validated at launch. [3][4] A successful
network-only launch therefore proves neither local identity change nor successful
authentication to a remote service. Record the exact API and logon flags, not
just the presence of username/password or token arguments.

## An alternate parent attribute changes more than a reported parent PID
PROC_THREAD_ATTRIBUTE_PARENT_PROCESS supplies a parent process handle requiring
PROCESS_CREATE_PROCESS. Documented inherited properties include the process
token, handles and job association; some properties, such as the debug port,
still come from the creating process. [5]

Constructed evidence: caller A supplies parent B in STARTUPINFOEX. A process-tree
parent observation alone does not identify the creating caller or establish that
every child property came from B. Recover the attribute list, successful update,
EXTENDED_STARTUPINFO_PRESENT and final creation result. Explicit-token APIs and
other attribute combinations require their own contracts; do not invent a
universal precedence rule from the ordinary CreateProcess case.

## Explicit handle lists narrow inheritance only when correctly installed
PROC_THREAD_ATTRIBUTE_HANDLE_LIST supplies handles for a particular child;
listed handles must be inheritable, cannot be pseudo handles, and require
bInheritHandles=TRUE. [5] STARTUPINFOEX and EXTENDED_STARTUPINFO_PRESENT are
needed for extended attributes. [8] A prepared but unused list grants no such
assurance.

Constructed inheritable set {pipe, secret-file}, installed list {pipe}: review
the final launch arguments and result before concluding the secret-file was
excluded. Check other concurrent launch paths that still request broad
inheritance. Standard-stream assignment is separate: for ordinary CreateProcess
with STARTF_USESTDHANDLES, inspect all three standard handle fields and their
inheritability. [6] Generic inheritance is not cross-session, and CreateProcess
documents PPL-to-non-PPL restrictions. [1] Retain target-version scope.

## Returned process-handle inheritance is not incoming handle inheritance
SECURITY_ATTRIBUTES describes the created object's security descriptor and
whether its returned handle is inheritable. [9] In CreateProcessW,
lpProcessAttributes/lpThreadAttributes govern the new objects and returned
handles; bInheritHandles separately governs existing handles passed into the
child. [1]

Constructed call uses NULL process attributes but bInheritHandles=TRUE. A
noninheritable returned process handle does not prove that the new child received
no existing handles. Trace each argument's direction and object. Similarly,
NULL lpSecurityDescriptor requests a default descriptor, not a null DACL. [9]
Do not confuse security on the process object with the new process's token or
with access rights carried by other inherited objects.

## Executable selection is not the child's argument parsing
For CreateProcessW, a non-NULL lpApplicationName identifies the image; a partial
name there uses the current drive/directory, not PATH search. With NULL, executable
selection comes from the command-line prefix; unquoted spaces can make it
ambiguous. CreateProcessW may modify its command-line buffer. [1]

Microsoft C startup then parses arguments under its own rules: argv[0] is
special; later arguments use quote/backslash rules, and caret is not an escape.
For backslashes immediately before a quote, pairs yield literal backslashes;
an odd leftover escapes the quote. [7] These are not universal shell or custom
parser rules. A correctly selected executable can still receive unintended
arguments. Recover the full string and actual consumer grammar before claiming
that quoting an image path prevents all argument injection.

## Launch success, primary-thread start and application readiness differ
CreateProcessW can return before initialization finishes; loader/DLL failure
can terminate the child afterward. [1] CREATE_SUSPENDED (0x4) holds the primary
thread until resumed; it is not an application-ready indication. A Unicode
environment block requires CREATE_UNICODE_ENVIRONMENT (0x400), even for a W
entry point. [8]

Constructed coordinator marks a job complete on successful process creation,
before observing any child result. That proves creation, not completion of the
requested operation. Preserve process/thread handles, resume paths, child exit
or protocol result and cleanup ownership. A later handle close is not evidence
that the child stopped. Do not equate UI visibility, process existence or a
successful startup API with a verified business operation.

## Identity and API sources
Reviewed 2026-10-02; current Microsoft documentation with explicit historical
qualifications where used. Examples are constructed, not target executions.

1. [CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw): ordinary identity, image/buffer contract, inheritance restrictions and initialization.
2. [CreateProcessAsUserW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessasuserw): primary token, privileges, session, profile and environment.
3. [CreateProcessWithTokenW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithtokenw): token, privileges and logon/session options.
4. [CreateProcessWithLogonW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createprocesswithlogonw): network-only local identity and unvalidated remote credentials.

## Startup and parsing sources
5. [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute): handle list and alternate parent.
6. [STARTUPINFOW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-startupinfow): standard handles and flags.
7. [Microsoft C argument parsing](https://learn.microsoft.com/en-us/cpp/c-language/parsing-c-command-line-arguments?view=msvc-170): runtime-specific quote/backslash rules.
8. [Process creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags): suspended, environment and extended-startup flags.
9. [SECURITY_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ns-wtypesbase-security_attributes): returned-handle inheritance and default descriptor versus null DACL.

Authority transfer: reference-windows-handle-authority-transfer. Token conversion:
reference-windows-tokens-sids-groups-impersonation. DLL search after selecting an
image: reference-windows-dll-plugin-resolution-activation.
