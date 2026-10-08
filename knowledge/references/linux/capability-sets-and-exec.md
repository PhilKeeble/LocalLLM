---
id: reference-linux-capability-exec-evidence
title: Linux capability sets, executable file capabilities and authority after exec
kind: reference
topics: [linux, capabilities, file-capabilities, exec, authority, user-namespaces]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Capability and executable authority evidence

## Effective capability possession is separate from other capability sets

Linux divides privileged operations into capabilities. The effective set is used
for capability permission checks; the permitted set limits capabilities the thread
may make effective. Inheritable, bounding and, where supported, ambient sets
participate in execution transitions. [1]

Investigate the required capability for the actual operation, the executing
thread's effective set and the namespace governing that resource. A capability
name in a manifest or permitted set is not evidence that it was effective at
the decisive check. UID alone is not a complete capability model. Availability
of individual capabilities and ambient support must be established on the target;
this section does not assume every Linux system exposes the same set.

## Bounding limits do not mean all currently held authority was removed

Linux's capability bounding set constrains file-permitted capability acquisition
during exec. It is not the effective set and does not itself describe every
currently usable capability. [1]

For investigation, compare the relevant pre/post-transition sets and actual
permission check. A reduced bounding mask cannot alone prove that current
privileged operations are impossible. Similarly, an inheritable bit does not
alone establish effective authority after executing an arbitrary file. Keep
set type, namespace, supported mechanism and observation time with the mask;
do not read a numeric capability mask without its target's bit definitions.

## File capabilities participate in a transition rather than acting as a grant label

Linux stores executable file capabilities in security.capability extended
attributes. File-permitted and file-inheritable masks combine with thread state;
the file effective flag is a single flag, not an independent capability mask. [1]

Investigate the exact executed file, its supported attribute encoding, namespace
association, thread sets and execution conditions. An attribute recovered from
a copied file does not prove the deployed execution acquired those privileges.
Exec suppression conditions, securebits and UID treatment can alter the result;
do not apply a simplified set equation without those premises. A captured
post-exec effective set is stronger evidence of resulting authority than a
filesystem label, but still does not prove the privileged operation occurred.

## Ambient capabilities need their own supported lifecycle

In Linux implementations supporting ambient capabilities, they must also be
permitted and inheritable. Executing a privileged file clears the ambient set;
an ordinary nonprivileged exec can carry it into new permitted/effective state.
The capability manual defines these conditions. [1]

Record support, actual set membership and the selected executable's privilege
properties. Do not infer that an ordinary-looking child executable necessarily
lost all authority, or that a privileged file retained ambient authority. Existing
descriptors and application delegation are separate channels. This is a named
Linux mechanism, not a default claim about every kernel or container runtime.

## A capability is checked in relation to the resource's user namespace

Linux user namespaces scope capabilities to governed resources; a capability in
a child user namespace does not confer the same authority in its ancestors. [2]

Bind the operation, resource-owning namespace, caller membership/mapping and
effective capability together. A container's root label or CAP_SYS_ADMIN string
cannot establish host-wide permission. Likewise, namespaces alone do not remove
access already delegated through a descriptor or broker. Identify the actual
boundary being checked rather than assigning a universal sandbox verdict.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19: set meanings, File capabilities,
Transformation of capabilities during execve, ambient conditions and namespace
scope. No raw attribute layout, kernel offsets or exploit sequence is assumed.

1. [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html): named sets and execution lifecycle; target support and special UID/securebits rules remain necessary.
2. [user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html): capabilities within governing namespaces.

Execution suppression: reference-linux-privilege-drop-exec. Workflow:
playbook-linux-authority-boundary.
