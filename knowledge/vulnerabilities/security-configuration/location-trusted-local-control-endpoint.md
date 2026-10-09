---
id: vulnerability-config-location-trusted-local-control-endpoint
title: Local control endpoint trusted solely because of its location
kind: vulnerability
topics: [configuration, local-socket, named-pipe, loopback, management-api, authorization]
platforms: [cross-platform, windows, linux, macos]
architectures: [any]
---

# Local control endpoint trusted solely because of its location

## Definition and violated invariant

This vulnerability occurs when a local socket, named pipe, loopback listener, shared-memory command channel, or management API treats endpoint location as sufficient proof of caller identity and authority. The invariant is that the actual peer and each requested operation/object must be authorized whenever multiple principals or constrained processes can reach the local transport.

Locality can reduce exposure but does not identify a user, process, sandbox, container, session, or application. An endpoint can be safe without application credentials when the transport supplies and the service correctly evaluates adequate peer credentials and permissions.

## Conditions that establish the issue

Identify namespace and bind/listen object, creation permissions, competing endpoint risk, network/container/session reachability, peer-credential mechanism, proxies, caller identity selected, authentication, per-operation authorization and privileged effect. Prove an unintended local actor can connect or send and obtain an operation beyond its rights.

For loopback, check namespace sharing, port forwarding, browser/web-origin reachability, DNS rebinding assumptions, and whether another local process can relay requests. Source address `127.0.0.1` or `::1` proves an IP path, not application identity.

## Evidence that is not sufficient

A loopback bind, Unix socket, pipe name, local RPC transport, missing password, or management method is not sufficient. Filesystem/socket ACLs, peer credentials, private namespaces, unguessable capability endpoints, or operation-level policy can enforce the intended boundary.

## Investigation sequence

Recover endpoint creation before client handling: namespace, permissions, owner, inheritance, listen address and proxies. Determine which kernel-supplied peer identity is available and whether code uses it instead of caller-supplied fields. Trace one request through parsing, identity propagation and object/action authorization to the effect.

At binary level, distinguish a string naming the endpoint from successful creation. Check failure fallback because inability to create a protected socket can lead to a broader temporary path or TCP listener.

## Primary sources and scope

Reviewed 2026-10-09 against Linux [`unix(7)` peer credentials and pathname permissions](https://man7.org/linux/man-pages/man7/unix.7.html), Microsoft [named-pipe security and access rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), and RFC 8252 [loopback redirect considerations for native applications](https://www.rfc-editor.org/rfc/rfc8252). Transport guarantees and caller identity differ by platform and namespace.
