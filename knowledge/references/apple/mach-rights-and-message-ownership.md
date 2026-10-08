---
id: reference-apple-mach-rights-message-ownership
title: Mach port rights, message descriptors and ownership evidence
kind: reference
topics: [mach, ipc, port-rights, descriptors, ownership, audit-tokens]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Mach capability and message evidence

## A Mach port name is local to a task's right namespace

Mach ports are communication endpoints accessed through send, receive or send-once
rights. A task uses an integer name in its own namespace; equal integers in two
tasks need not identify the same port. A message-queue port has one receive-right
owner and may have multiple senders. [1]

Recover the right and object relation before joining client/server evidence.
Holding a send right enables communication with that endpoint; the server still
determines the requested operation's policy. A numeric name alone neither grants
a right nor establishes the sender's application identity.

## Message dispositions and descriptors carry ownership information

XNU message definitions distinguish moving, copying and creating rights, and
port, out-of-line memory and out-of-line port-array descriptors. A port name
carried as uninterpreted data does not transfer a right. [2]

Recover the descriptor type, disposition, extent and actual send/receive result.
Track sender and receiver cleanup separately, including failures. Out-of-line
memory is described separately from inline message bytes; do not treat every
address-sized field as a receiver-local pointer. Exact descriptor layout and
failure ownership require the target's matching contract, not a universal offset.

## A Mach audit trailer is different from a caller-supplied identity field

XNU defines an audit trailer with an opaque audit token identifying the Mach
subject; its comments require appropriate audit-library interpretation because
representation may change. [2]

Determine whether identity came from the actual received message's supported
trailer or from payload data. Retain requested trailer type, returned extent and
validity. Do not decode fixed token words from memory or trust a claimed PID in
the payload as authenticated caller identity. Sender identity and authority for
the selected object/action are separate decisions.

## Sources and scope

Reviewed 2026-10-08. [Apple Mach overview](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/KernelProgramming/Mach/Mach.html)
[1], Ports/Namespaces and Message Queues; archived guide's obsolete IPC-family
advice is not adopted. [XNU message.h](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/mach/message.h)
[2], public disposition/descriptor/trailer definitions and audit-token comments.
Rolling source supplies concept/field roles, not target private layout.
Workflow: playbook-apple-service-authority.
