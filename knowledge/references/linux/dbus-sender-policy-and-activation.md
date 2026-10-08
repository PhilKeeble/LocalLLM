---
id: reference-linux-dbus-sender-policy-activation
title: D-Bus sender identity, method authorization, policy and service activation
kind: reference
topics: [linux, dbus, ipc, sender-identity, authorization, activation, helpers]
platforms: [linux, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# D-Bus identity and operation boundaries

## Message-bus sender identity differs from a sender-controlled field

On a D-Bus message bus, the bus controls the SENDER header. In direct peer
communication, its meaning can be sender-controlled unless another authenticated
channel supplies identity. Unique names identify connections; well-known names
can change owners. [1]

For investigation, bind bus instance, connection generation, message sender and
authenticated credentials to the request. A well-known name or payload username
is not independent proof of the caller. A later name-owner query cannot silently
authenticate an earlier message after owner changes. Identity supplied by a bus
is only as trustworthy as that bus and its deployment; do not transfer this
guarantee to a direct connection or untrusted intermediary.

## Bus delivery policy is separate from method/object authorization

The documented dbus-daemon policy controls sending, receiving and name ownership.
Matching rules and their order matter; send_destination/receive_sender rules
refer to the connection owning a name. [2]

Investigate the effective policy and actual destination owner, then the service's
method dispatch, arguments and object authorization. Permission to deliver a
message is not authorization for every privileged action or caller-selected file.
Conversely, a policy denial must be tied to the same request before concluding
that its handler is unreachable. Another bus implementation needs its own policy
contract; a configuration excerpt is not necessarily the loaded policy.

## Activation starts a service before delivery, not a completed operation

D-Bus supports activation when an eligible requested name has no owner and the
bus knows how to start its service. The service must acquire the name before the
queued message is delivered. Activation can fail. [1]

For investigation, connect effective activation definition, selected program,
execution identity, name ownership and delivered request. A .service file or a
successful start request does not establish that the later method ran or committed
its effect. Launch managers and helper policies require their own contracts.
Keep installed definition, active owner and observed behavior distinct; a familiar
service name neither authenticates its historical executable nor settles intent.

## Deferred helpers must retain the authenticated request context

For a D-Bus service delegating work, identify the verified request identity, selected
operation/object and authority used by the helper. Follow asynchronous queues,
callbacks and replies under that same request generation.

Do not replace a request's identity with the worker's UID or a newly queried owner
of a recycled name. A method return can indicate acceptance rather than a committed
effect; establish the implementation's result semantics. This is evidence guidance,
not a D-Bus-wide rule for helper authorization. Shared object/caller binding is in
reference-logic-authorization-object-binding.

## Sources and scope

Reviewed 2026-10-08. Rolling D-Bus specification: Header Fields, Bus Names,
Message Routing and Service Activation. dbus-daemon manual: Policy and rule
matching. No default bus policy or service installation path is assumed.

1. [D-Bus specification](https://dbus.freedesktop.org/doc/dbus-specification.html): bus-mediated identity and activation contracts.
2. [dbus-daemon manual](https://dbus.freedesktop.org/doc/dbus-daemon.1.html): implementation-specific policy semantics.

Workflow: playbook-linux-ipc-authority. Linux transport credentials:
reference-linux-unix-socket-credentials-rights.
