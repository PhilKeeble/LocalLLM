---
id: vulnerability-filesystem-named-object-endpoint-squatting
title: Named-object collision and IPC endpoint squatting
kind: vulnerability
topics: [filesystem, namespaces, named-pipes, ipc, collisions, impersonation]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Named-object collision and IPC endpoint squatting

## Definition and violated invariant

Endpoint or named-object squatting occurs when a lower-authority actor creates or retains control of a predictable name before the intended owner, causing a client or service to use an attacker-controlled pipe, socket, shared memory object, synchronization object, port, registry/namespace entry, or other endpoint. Name resolution, creation outcome, object type, owner and security descriptor must bind clients and servers to the intended endpoint identity.

Naming rules are mechanism-specific. Windows pipe names do not use mutex `Global\`/`Local\` rules; named kernel objects can share collision namespaces across object types; private namespace aliases require their boundary context. A creation API that returns an existing object can ignore requested initialization or security attributes. Unix-domain sockets, POSIX shared memory and platform services have different ownership and filesystem/namespace rules.

## Conditions that establish the issue

Recover complete name and scope, namespace/session/container, object type, creation/open API, first-instance or exclusive flags, immediate creation status, owner and DACL/mode, attacker creation/open rights, instance lifecycle, client resolution, peer authentication, exchanged data and security-relevant effect. Prove the attacker can win or reuse the name and that a victim connects to or trusts the attacker's object.

For Windows named pipes, distinguish server instance creation rights from client read/write rights and remote-client policy. A first-instance collision check is not a substitute for an appropriate pipe DACL or client authentication.

## Evidence that is not sufficient

A predictable name, existing object, `ERROR_ALREADY_EXISTS`, failed first-instance creation, global namespace, socket file, mutex, or pipe is not sufficient. The attacker may lack creation rights, the victim may reject an existing object, ACLs may exclude it, or a protocol handshake may authenticate the intended peer.

Successful connection does not prove peer identity, and a name match does not prove which process created the object.

## Investigation sequence

Build a namespace timeline containing creator, session/container, full name, object type, descriptor, create/open result, last-error/status, instance number, handles, client resolution and cleanup. Trace races at startup and restart, stale filesystem entries, fallback names and reconnect. Bind each message and authorization decision to the actual peer and connection generation.

At binary level, inspect creation flags, immediate error retrieval, existing-object branches, security attributes, access masks and client/server handle roles. Follow the object into the data or synchronization operation that matters.

## Constructed Windows named-pipe example

```c
HANDLE pipe = CreateNamedPipeW(L"\\\\.\\pipe\\ProductControl", PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, 1, 4096, 4096, 0, security_attributes);
if (pipe == INVALID_HANDLE_VALUE)
    connect_as_client_to_existing_name();
```

If a lower-authority process can create the same server name first, the fallback can connect the privileged component to an attacker-controlled server. The finding requires actual creation rights, the collision result, reachable fallback and a security-relevant exchange. `FILE_FLAG_FIRST_PIPE_INSTANCE` can detect an existing name for a creator but does not by itself establish safe DACLs or authenticate later peers.

## Primitive and impact limits

The direct primitive is substitution or collision of a named endpoint/object. Consequences can include credential or secret capture, command/data injection, synchronization manipulation, shared-memory substitution, denial of service, or a confused-deputy path. Privilege escalation requires a cross-authority victim and a sensitive action or data flow.

## Related knowledge and primary sources

`reference-windows-object-namespaces-collisions`, `reference-windows-named-pipe-security-identity`, pipe parsing profiles, and authority references provide mechanism detail. This profile keeps name ownership, peer identity and requested operation separate.

Reviewed 2026-10-09 against Microsoft [Object Namespaces](https://learn.microsoft.com/en-us/windows/win32/sync/object-namespaces), [`CreateNamedPipeW`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createnamedpipew), [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), and [`CreateMutexW`](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw), plus POSIX [`shm_open`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/shm_open.html) for a distinct named-object contract. The source is constructed and Windows-scoped.
