---
id: playbook-linux-kernel-request
title: Recover Linux user-to-kernel request layout, authority and output evidence
kind: playbook
topics: [linux, kernel-interfaces, ioctl, netlink, user-copy, compat, validation, investigation]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover a Linux user/kernel request

## Bind the entry to its caller ABI and selected kernel object

Identify actual device, socket family, proc/sysfs entry or other interface,
caller credentials, namespace and selected handler. Preserve command/method,
input bytes, lengths and entry result.

Use reference-linux-kernel-interface-representations. A descriptor or writable
virtual file establishes a possible entry, not authorization for every operation.
Native and compat paths can consume different layouts. Select the actual path
before assigning widths or offsets; a decompiler's type or command name is only
a hypothesis until supported by copies and field use.

## Recover the bounded representation actually consumed

Trace copied extents, copy result, conversion, selector and nested lengths to
the operation. Preserve units, signedness, pointer/scalar interpretation and
same-value versions; split unrelated fields into separate evidence relations.

Bulk Linux user-copy results count uncopied bytes, unlike single-value helper
errors. A partially supplied object must not be treated as complete because one
header parsed. Repeated user/shared reads can observe different values. Bind
validation to the bytes consumed, retaining mutation and conversion limits under
the shared parser and data-flow contracts.

## Establish authorization, lifetime and output extent at the same operation

Identify caller-to-object permission, retained object/device state, acquired
reference, queued work and release. For returned content, retain initialized
extent and the amount actually copied/reported.

Proc/sysfs names are not ordinary passive-file guarantees, and a retained software
object need not mean its physical device is present. A success/error label also
does not establish all requested output was returned. Follow selected callbacks
and cleanup. Report the concrete violated invariant or supported effect; powerful
kernel interfaces alone establish neither a defect nor malicious use.

## Interpret netlink stream state and report evidence gaps

For netlink, bind family, port/socket context, sequence, aligned message extents,
multipart termination and result semantics. Separate transport acknowledgment
from the family's actual state change.

A missing notification cannot prove no operation occurred when receive loss or
coverage is unresolved. Port IDs cannot automatically authenticate a process.
Deliver the supported request-to-handler-to-effect chain and earliest missing
edge. Family payload and permission rules require their own source, rather than
generalizing generic netlink framing to every subsystem.

## Basis and scope

Reviewed 2026-10-08. Uses reference-linux-kernel-interface-representations and
shared parser, authority and lifetime references. Conceptual boundary review;
no command construction, vulnerability reproduction or kernel layout assumptions.
