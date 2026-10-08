---
id: reference-apple-xpc-peer-request-authority
title: XPC peer identity, request authorization and connection lifecycle
kind: reference
topics: [xpc, ipc, audit-tokens, entitlements, authorization, connection-lifetime]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# XPC caller and request evidence

## Peer evidence must belong to the connection that supplied the request

Apple's supported XPC peer-requirement API can check a signed entitlement on
messages; this mechanism needs platform/API support and explicit configuration.
SecTaskCreateWithAuditToken describes creating a task object for the sender
represented by a Mach message audit token. [1][2]

Bind authenticated peer evidence to the request rather than looking up a
caller-supplied PID or path later. An entitlement's existence is not the same
predicate as its expected value. A signed peer identity also does not establish
that this peer may perform every operation offered by the service.

## Interface class restrictions do not authorize a requested effect

NSXPC interfaces restrict transferable object classes and use secure-coding
contracts for custom objects. [3] This bounds representation choices; it does
not prove valid paths, handles, amounts or application permissions.

Recover message method, allowed classes, decoded values and per-operation policy.
Keep deserialization validation separate from caller and object authorization.
A well-typed request can still select an unauthorized object; the supported
consumer relation is necessary before reporting a defect or malicious use.

## Interruption and invalidation have different connection meanings

Apple's NSXPC guide distinguishes interruption after peer closure/crash from
invalidation after connection teardown. An interrupted connection can remain
usable; an invalidated connection must be recreated. [3]

Track connection generation, pending replies and retained helper state across
retry. A lost reply does not prove the remote operation had no effect, and a
new helper need not inherit old authorization/session state. These are NSXPC
concepts, not a guarantee about every lower-level XPC callback sequence.

## Sources and scope

Reviewed 2026-10-08. [XPC peer entitlement requirement](https://developer.apple.com/documentation/XPC/xpc_connection_set_peer_entitlement_exists_requirement(_:_:))
[1], Discussion; [Security SecTask.h](https://raw.githubusercontent.com/apple-oss-distributions/Security/main/sectask/SecTask.h)
[2], audit-token creation contract; [Creating XPC Services](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingXPCServices.html)
[3], Handling Errors and Working with Custom Classes. No private identity API,
universal peer-check default or release-specific availability assumed.
Workflow: playbook-apple-service-authority.
