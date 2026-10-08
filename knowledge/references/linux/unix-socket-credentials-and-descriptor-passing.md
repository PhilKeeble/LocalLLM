---
id: reference-linux-unix-socket-credentials-rights
title: Linux Unix-domain endpoints, peer credentials and passed descriptor authority
kind: reference
topics: [linux, unix-sockets, ipc, peer-credentials, ancillary-data, descriptor-passing, authority]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Unix-domain communication and delegated references

## Pathname and abstract sockets have different access boundaries

Linux pathname sockets use filesystem permissions: stream connection and datagram
sending require socket write permission. Linux abstract sockets have no such
filesystem permission boundary. Their names are length-delimited bytes, not
ordinary pathname strings. These rules are not universal Unix socket contracts. [1]

Investigate actual address type/extent, namespace, endpoint owner, listener and
access policy. A path-like display can conceal an abstract address. Reachability
does not establish authorization for every method. Conversely, absence of a
filesystem socket file does not prove absence of an abstract or unnamed endpoint.
Do not assign privilege or maliciousness from the endpoint's name.

## SO_PEERCRED supplies a connection credential observation, not every request's intent

Linux SO_PEERCRED supplies peer credentials from the documented connect/listen/
socketpair event, for its supported connected socket types. [1]

For investigation, bind the actual query result to the same socket and connection
generation. It is not proof that a later payload's claimed UID is authentic or
that every requested object belongs to the peer. Credential transitions and
delegation require their own evidence. A PID also needs process lifetime and
namespace context; do not correlate an old peer record with a reused PID solely
by number. This contract must not be applied to unsupported socket types.

## SCM_CREDENTIALS has kernel checks distinct from application identity fields

Linux SCM_CREDENTIALS ancillary messages carry process/user/group credentials
checked by the kernel; suitably privileged senders can supply permitted alternate
values under the API's rules. [1]

Investigate the actual ancillary type, receive support, returned credentials and
privilege/namespace context. An application payload containing a UID is a different
object. Kernel validation authenticates the supported credential relation, not
authorization for every requested operation. Keep connection-based identity and
message-associated identity separate; neither can silently supply the other's
time or scope. Missing ancillary evidence leaves that authentication edge unknown.

## SCM_RIGHTS transfers an open-file-description reference, not the sender's integer

Linux SCM_RIGHTS transfers references to open file descriptions. The receiver
normally obtains its own descriptor numbers for those references. [1]

For investigation, bind each transmitted reference to its receiver-side descriptor
generation, object, open mode and lifetime. Do not compare numeric descriptors
between processes as object identity. A received descriptor can delegate access
without selecting the resource through its pathname again; establish the specific
operation and remaining checks. Same-user communication alone does not authorize
arbitrary delegated resources. Shared offset/status behavior is in
reference-linux-descriptors-open-file-descriptions.

## Ancillary truncation can change which resources a message actually delivered

Linux Unix-socket documentation states that excess SCM_RIGHTS descriptors are
closed in the receiver when ancillary capacity is insufficient or descriptor
limits are exceeded. [1]

For investigation, preserve returned data/ancillary extents, truncation indication,
descriptor count and the resources the consumer actually retained. A successful
receive of payload bytes does not establish receipt of every expected resource.
Partial acceptance, cleanup and rejected messages require separate ownership
tracking. Never treat an absent descriptor as a valid default number; inspect
the consumer's actual missing-resource path before reporting an effect.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19, Unix socket address classes, permissions,
SO_PEERCRED and ancillary-message contracts. No portable BSD permission model,
fixed address capacity, descriptor limit or credential-structure offset is adopted.

1. [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html): named mechanisms and their limits.

Workflow: playbook-linux-ipc-authority. Kernel-provided identity, application
authorization and effect are separate evidence relations.
