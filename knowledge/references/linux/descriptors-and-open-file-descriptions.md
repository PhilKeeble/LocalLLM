---
id: reference-linux-descriptors-open-file-descriptions
title: Linux descriptor identity, shared open file descriptions and inheritance
kind: reference
topics: [linux, file-descriptors, open-file-descriptions, duplication, inheritance, close-on-exec, resource-lifetime]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Descriptor identity and retained authority

## A file descriptor is a table entry, not a pathname or permanent identity

Linux open returns a descriptor referencing an open file description, which holds
the file offset and file status flags. Changing or removing the pathname does
not retarget that existing reference. [1]

For investigation, record process/table context, descriptor allocation generation,
underlying object and open mode. After close and reuse, the same integer can name
an unrelated object. A path shown through proc is useful context, not a historical
proof that the number always selected that file. Follow the actual reference
through the operation; a later open at the same name cannot authenticate earlier
bytes. An open reference does not remove checks imposed by a particular operation.

## dup shares offset/status while close-on-exec belongs to the descriptor

Linux dup creates another descriptor referring to the same open file description;
offset and file status flags are shared. Descriptor flags are separate, and a
plain dup result has close-on-exec disabled. dup3 can request O_CLOEXEC. [2]

Investigate shared-offset effects and each descriptor's own lifetime/flags.
Closing one reference does not by itself show all references were released.
Likewise, setting close-on-exec on one descriptor does not establish it on its
duplicates. Keep the duplication variant and successful result with the claim;
do not copy plain dup's flag behavior onto every descriptor-transfer interface.

## Fork inherits references while exec close-on-exec is a different boundary

Linux fork gives the child descriptor copies referring to the same open file
descriptions. Successful exec closes descriptors marked FD_CLOEXEC. [3][4]
O_CLOEXEC at creation avoids the interval introduced by a separate flag-setting
call in concurrent fork/exec code. [1]

For investigation, preserve the child identity, inherited descriptor set and
actual successful exec. A close-on-exec flag does not mean 'not inherited at
fork' or 'closed when exec failed'. Determine whether a helper received an
unintended resource, then trace its actual use. A descriptor number in one
process cannot be compared directly with a number in another to prove identity.

## Descriptor replacement and stale references require the exact transition

Linux dup2 atomically closes/replaces its chosen destination descriptor when
needed; this differs from independent close followed by dup. [2]

For analysis, associate the old and new object with the transition and retain
which thread holds the table/reference. A stored integer used after replacement
may select a different object. Establish the actual reuse and consuming operation
before reporting a lifetime or authorization defect; integer equality alone is
not an object relation. Shared descriptor tables and application-owned wrappers
require their own ownership evidence, not assumptions from process names.

## Proc descriptor views describe the observed process and time

For investigation, a proc descriptor view is an observation of a particular
process generation and namespace context. Correlate it with open/dup/transfer,
close and use evidence; do not substitute it for a complete history.

Missing proc access or a missing table entry leaves coverage and timing questions.
It does not prove a descriptor never existed or that a blocked operation lacked
authority. Opening a proc-derived path is a new selection action whose contract
must be reviewed; it is not automatically equivalent to inspecting the original
reference. Namespace and magic-link distinctions are in
reference-linux-path-resolution-identity. This is analytical evidence guidance.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19, named open/dup/fork/exec contracts.
No fixed descriptor values or private table layout is assumed.

1. [open(2)](https://man7.org/linux/man-pages/man2/open.2.html): open file descriptions, pathname independence and atomic close-on-exec creation.
2. [dup(2)](https://man7.org/linux/man-pages/man2/dup.2.html): sharing, separate flags and replacement.
3. [fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html): inherited references.
4. [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html): descriptor preservation and close-on-exec.

Workflow: playbook-linux-file-object-boundary. Cross-process delegation:
reference-linux-unix-socket-credentials-rights.
