---
id: playbook-linux-ipc-authority
title: Recover Linux IPC caller identity, method authority and delegated descriptors
kind: playbook
topics: [linux, ipc, unix-sockets, dbus, caller-identity, authorization, delegation]
platforms: [linux, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover IPC identity and delegated authority

## Identify endpoint, transport and selecting namespace

Bind the observed listener/connection to its address type, byte extent, process
generation and namespace or bus instance. Distinguish Unix pathname, abstract
and unnamed endpoints from D-Bus routing names.

Use reference-linux-unix-socket-credentials-rights and
reference-linux-dbus-sender-policy-activation. A familiar name is not endpoint
ownership proof. Filesystem permissions cannot be copied onto Linux abstract
sockets, and a D-Bus well-known name can change owners. Reachability is one
relation, separate from authentication and method/object authorization.

## Bind the authenticated identity to this request

Recover the actual peer query, kernel ancillary credentials or trusted bus sender
and its result. Keep payload identity fields separate. Record connection/request
generation and credential observation time.

Apply the named mechanism's supported socket/bus scope. SO_PEERCRED is not every
later request's credential snapshot; direct D-Bus peers do not inherit the bus's
SENDER guarantee. PID and unique-name correlations need lifetime and namespace
context. Missing authenticated identity cannot be filled from a service log label
or the worker's current UID.

## Follow message framing, accepted method and object authorization

Trace actual message extent, parser result, selected method/handler, operands,
policy checks and sensitive operation. Preserve partial messages, duplicates,
ancillary truncation and rejected paths.

Delivery permission does not authorize arbitrary caller-selected objects.
Likewise, successful decoding does not establish an effect. Determine what the
service checks about the authenticated caller and selected object, under
reference-logic-authorization-object-binding. Activation configuration and name
acquisition are separate from delivery and completed operation.

## Track transferred references and asynchronous request context

For each passed descriptor, bind sender-side object to receiver-side descriptor
generation, mode, lifetime and actual use. Retain received versus expected resource
counts, cleanup and final ownership.

SCM_RIGHTS transfers references, not matching integers. A resource accepted from
one caller must not silently supply authority for another request. Follow queued
work under the original authenticated context rather than a later name-owner
lookup. Shared offset/flags and inheritance are in
reference-linux-descriptors-open-file-descriptions; transport success alone does
not establish the intended delegated operation occurred.

## Report caller, delegated object and committed effect separately

Deliver endpoint/bus identity, authenticated caller, accepted request, checks,
delegated references, execution authority and supported effect. Label whether a
reply acknowledges receipt, acceptance or a completed operation.

Unsupported credential, dispatch or completion relations remain unknown. Do not
turn IPC API presence into an authorization defect or a malware verdict. A known
service can perform harmful supplied operations, while an unexplained endpoint
is only a lead until its behavior and authority are established.

## Basis and scope

Reviewed 2026-10-08. Linux Unix-socket and D-Bus reference contracts, applied only
where the transport/implementation is identified. Metadata includes D-Bus platforms;
Linux-specific credential and abstract-socket rules are not BSD universals.
