---
id: playbook-specialist-kernel-boundary
title: Recover kernel request authority, synchronization and object lifetime
kind: playbook
topics: [kernel-interfaces, authority, user-copy, refcounts, rcu, locks, teardown]
platforms: [linux, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Kernel boundary investigation

## Identify the OS, caller ABI, object and request contract

Bind the request to the actual device/service, command, caller representation
and selected handler. Recover copied input/output extents and conversion results
before assigning native structures. Shared instruction sets do not imply identical
syscall selectors, request encoding, error conventions or ownership.

Facts: reference-linux-kernel-interface-representations and
reference-freebsd-authority-interface-evidence. A command's encoded size is not
complete validation of nested data or proof that the operation is authorized.

## Recover authority at the decision and retained work context

Identify caller identity, namespace/jail context, object rights, policy checks
and any delegation to a worker or service. Preserve the authority actually bound
to queued work instead of inferring it from that worker's ambient identity.

Linux capability and FreeBSD Capsicum contracts differ. Route to
playbook-linux-authority-boundary and reference-freebsd-authority-interface-evidence.
A root UID, open descriptor or sandbox API string does not prove the claimed
permission or successful policy transition.

## Follow lifetime and synchronization through lookup and handoff

Identify what keeps the object valid during lookup, ownership acquisition, queued
use and completion. Separate locks protecting mutable state, references retaining
objects and RCU grace periods delaying reclamation. Record actual configuration
and context before applying lock or sleeping rules.

Facts: reference-linux-kernel-object-lifetime and
reference-concurrency-refcounts-reuse. A reference increment on an invalid pointer
does not establish safe retention, and a lock name is not proof all users serialize.

## Review errors, cancellation and teardown as separate paths

Recover partial input/output, failure result, retained work and final cleanup.
Track admission stop, lookup removal, callback/work completion and device users
before concluding backing storage is reclaimable. A cancellation request or
caller close does not establish the final asynchronous use ended.

Report the precise invalid use, missing authority binding or incomplete evidence
for the actual object/request. A powerful API or crash alone does not prove
exploitation or malicious intent. No target execution is required by this workflow.

## Review basis

Reviewed 2026-10-08 against the OS-specific references named above and
reference-concurrency-cancellation-completion-shutdown. Primary contracts remain
in their factual homes; this workflow supplies evidence order rather than a
cross-platform kernel implementation or testing recipe.
