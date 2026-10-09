---
id: vulnerability-authorization-namespace-authority-confusion
title: Namespace, container, jail, or user-namespace identity and authority confusion
kind: vulnerability
topics: [authorization, namespaces, containers, jails, user-namespaces, identity-mapping]
platforms: [linux, freebsd, cross-platform]
architectures: [any]
---

# Namespace, container, jail, or user-namespace identity and authority confusion

## Definition and violated invariant

A namespace-authority vulnerability occurs when software interprets an identity, name, capability or resource reference under one container, jail or namespace context but authorizes or consumes it in another, granting authority outside the initiating isolation scope. Namespace membership is multidimensional: identity, mounts, processes, networking and IPC can be isolated or shared independently.

Numeric root or administrator-like identity inside a child namespace is not automatically host authority. Conversely, a process in a namespace can retain host capabilities through descriptors, mounts, devices or brokers that cross the boundary.

## Conditions that establish the issue

Recover the initiating actor, process generation, every namespace or jail relevant to identity and selected resource, UID/GID or principal mappings, governing namespace for capabilities, root and working directory, mount and network views, retained descriptors or handles, broker paths, authorization decision, final object and exact authority gained outside the intended scope. Prove a context mismatch permits a forbidden effect.

State whether the result is cross-user access, container/jail escape or host authority. A namespace-local capability matters only for resources governed by its scope or descendants under the platform contract.

## Evidence that is not sufficient

UID 0, container root, a namespace API, shared namespace, visible host path, bind mount, capability bit, jail ID or container label is not sufficient. Identity mappings and resource governance may limit authority, the object may be intentionally delegated, or another policy layer may deny the operation.

Likewise, a hidden pathname does not prove the absence of a preopened descriptor or brokered reference to the same host object.

## Investigation sequence

Build a namespace matrix for the initiating task, deputy and protected resource. Resolve identity mappings and the user namespace or jail governing each capability check. Trace path selection through root, working directory and mount view, then retain the opened object's identity through use. Add shared devices, sockets, descriptors and management APIs separately.

At binary level, follow namespace setup, ID-map writes, credential queries and object opens. A displayed UID or pathname must be interpreted in the context that produced it.

## Hypothetical identity-context example

```text
broker receives { uid: 0, object_id: X } from a container client
if request.uid == 0:
    broker.modify_host_object(X)
```

The caller-supplied number does not authenticate host root and may represent namespace-local identity. The path is vulnerable only if the broker trusts it, a less-authorized container actor can send the request, and the broker modifies a host object outside the permitted delegation.

## Primitive and impact limits

The direct primitive is access or action interpreted in the wrong identity or resource namespace. Impact is the exact authority outside the initiating boundary, which may be horizontal access or an isolation escape. Host code execution requires a separate host execution path or privileged object activation.

## Related knowledge and primary sources

Linux namespace, credentials, path and capability references and FreeBSD jail/Capsicum references define platform scopes. Container profiles cover management sockets and delegated host resources.

Reviewed 2026-10-09 against Linux [`namespaces(7)`](https://man7.org/linux/man-pages/man7/namespaces.7.html) and [`user_namespaces(7)`](https://man7.org/linux/man-pages/man7/user_namespaces.7.html) for distinct resource domains, ID mappings and capability scope. The example is hypothetical; FreeBSD jails and other container systems require their own contracts.
