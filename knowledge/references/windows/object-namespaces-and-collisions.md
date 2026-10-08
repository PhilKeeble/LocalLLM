---
id: reference-windows-object-namespaces-collisions
title: Windows session and private namespaces, named-object collisions and creation outcomes
kind: reference
topics: [windows, namespaces, named-objects, sessions, collisions, mutexes, events]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Resolve a name before assigning trust
Scope: documented Win32 named kernel objects, with explicit distinctions for
pipe names. An object name is a lookup input, not authentication of its creator
or evidence that the latest caller initialized the returned object.

## Global and Local select scope, not an access-control policy
Reviewed 2026-10-02. For the documented event, mutex, semaphore, timer, mapping,
job and symbolic-link namespaces, client-session processes use their session
namespace by default; services use the global namespace. Global\ selects global
scope, Local\ explicitly selects session scope; these prefixes are case-sensitive.
Session\ is reserved. Since Vista, session zero hosts services. [1]

Constructed pair: Local\Channel in two different sessions need not identify one
object. Global\Channel allows a shared lookup scope, not unrestricted access
or proof that a service created it. Preserve actual process session, prefix,
object type, descriptor and open result. Do not identify a principal merely
from its session number or apply these prefixes to every Windows naming API.
These desktop/session contracts do not remove packaged/AppContainer namespace
restrictions, which require separate analysis.

## SeCreateGlobalPrivilege is scoped to creation of specific object types
Creating global file-mapping or symbolic-link objects outside session zero
requires enabled SeCreateGlobalPrivilege. That check does not apply to opening
existing objects; opening still requires the relevant access rights. [1]

Investigation consequence: a client lacking this privilege can still obtain an
authorized handle to a service-created global mapping. Conversely, privilege
possession alone does not establish that an open was allowed. Do not extend
this creation requirement to every global event or mutex. Capture create/open,
session, object kind and the actual failing call before attributing an error
to missing privilege.

## Object type and naming API affect collision interpretation
CreateMutexW compares names case-sensitively. A collision with an event,
semaphore, timer, job or file-mapping object fails with ERROR_INVALID_HANDLE
because these named objects share a namespace. [2] That error need not mean
the caller supplied a stale numeric handle: this call receives a name.

Pipe names use \\ServerName\pipe\PipeName, with a period for the local host,
and are case-insensitive. CreateNamedPipe uses the local-host form. [3] These
are different naming rules from mutex Global\ and Local\ prefixes.
Constructed evidence: strings differing only in letter case may select the
same pipe, while differently cased mutex names can be distinct. Recover API,
host/session context and complete name before merging identifiers in a report.

## CreateMutex success does not prove new ownership or installed security
When CreateMutexW opens an existing named mutex, it requests MUTEX_ALL_ACCESS,
ignores bInitialOwner and ignores the supplied descriptor; inheritability is
still taken from supplied attributes. Successful existing-object return is
accompanied by ERROR_ALREADY_EXISTS. [2]

Constructed caller supplies a restrictive DACL and bInitialOwner=TRUE, then
enters a critical section on any non-NULL return. Neither newly installed DACL
nor mutex ownership follows on the existing-object path. Preserve the immediate
last-error result and later wait/ownership path. A predictable name is only a
collision candidate: show that another actor can create/open the relevant
object and that the victim mishandles that outcome before claiming a defect.

## CreateEvent does not reset the properties of an existing event
For an existing named event, CreateEventW requests EVENT_ALL_ACCESS; supplied
manual-reset, initial-state and security-descriptor settings do not replace
the existing object's settings. A successful open reports ERROR_ALREADY_EXISTS;
an access failure returns NULL. [4]

Constructed call requests a nonsignaled manual-reset event but opens an existing
auto-reset event. The arguments are not evidence that all waiters will later
be released. A manual-reset event stays signaled until reset and can release
multiple waiters; an auto-reset event releases one waiter before resetting. [4]
Identify the actual object and state transitions. A signaled notification alone
does not authenticate a publisher or prove that shared payload fields are valid.

## A private namespace is identified by boundary as well as alias
CreatePrivateNamespace requires its creator to satisfy the supplied boundary.
Multiple namespaces can share an alias when their boundaries differ. Objects
are addressed as alias\object; namespace security attributes and the objects'
own security remain relevant. [5][6] These APIs are documented from Vista /
Server 2008, not all historical Windows releases.

Constructed observations both contain alias Team\Ready but use different
boundary descriptors. Alias equality alone does not establish one event or
one synchronization domain. Capture boundary construction, SID inputs,
namespace descriptor and successful create/open results. Do not equate the
word private with an unforgeable application identity or omit ACL review;
the overview separately warns about access when namespace security is not
restricted. [6]

## Namespace destruction and existing object operations are different
ClosePrivateNamespace accepts PRIVATE_NAMESPACE_FLAG_DESTROY to request
namespace destruction and returns a success/failure result. [7] The namespace
overview distinguishes subsequent namespace opens from operations on objects
already obtained. [6]

Constructed shutdown report says closing the namespace revoked all client
event handles. That conclusion needs separate handle/object-lifetime evidence;
a name becoming unavailable is not proof that every existing reference stopped
working. Record close flags, result, creator/opener role and remaining references,
not just an imported close function. Handle authority and ownership rules:
reference-windows-handle-authority-transfer.

## Namespace and collision sources
Reviewed 2026-10-02; documented Windows contracts, not observed target behavior.
Examples are constructed. Global/session rules are not universal file-path,
registry, pipe, AppContainer or kernel-driver namespace rules.

1. [Kernel object namespaces](https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces): default scope, prefixes, session zero and creation privilege.
2. [CreateMutexW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw): case, cross-type collision, existing-object flags and rights.
3. [Pipe names](https://learn.microsoft.com/en-us/windows/win32/ipc/pipe-names): host-qualified syntax and case-insensitivity.
4. [CreateEventW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventw): existing-object semantics and reset behavior.

## Private namespace sources and routing
5. [CreatePrivateNamespaceW](https://learn.microsoft.com/en-us/windows/win32/api/namespaceapi/nf-namespaceapi-createprivatenamespacew): creator boundary, alias and minimum versions.
6. [Object namespaces](https://learn.microsoft.com/en-us/windows/win32/sync/object-namespaces): identity, open-security caveat and existing objects.
7. [ClosePrivateNamespace](https://learn.microsoft.com/en-us/windows/win32/api/namespaceapi/nf-namespaceapi-closeprivatenamespace): destroy flag and return status.

Mapping size and view evidence: reference-windows-shared-mapping-evidence.
Pipe authorization/framing: reference-windows-named-pipe-security-identity.
Access decisions: reference-windows-access-check-rights-integrity.
