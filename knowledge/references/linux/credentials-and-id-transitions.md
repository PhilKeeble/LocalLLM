---
id: reference-linux-credentials-id-transitions
title: Linux real, effective, saved and filesystem credentials
kind: reference
topics: [linux, credentials, uid, gid, supplementary-groups, privilege-transitions]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Credentials and identity transitions

## Real, effective and saved IDs answer different authority questions

Linux distinguishes real, effective and saved user/group IDs. Effective IDs are
used for many resource permission checks; saved IDs can permit a later effective
ID transition under the relevant API rules. Filesystem checks have additional
credentials described separately below. [1]

For investigation, bind the exact operation to the executing thread's credentials
at that time. A real UID or process-owner display is not a complete authority
snapshot. A later credential capture cannot establish the identity of an earlier
request. Keep the API, requested transition, result and subsequent operation
together; an attempted identity change is not a completed privilege reduction.
These Linux contracts do not supply application-specific object authorization.

## Filesystem IDs and supplementary groups participate in file access

Linux filesystem UID/GID normally track effective UID/GID but can differ through
the filesystem-ID APIs. Supplementary groups also participate in permissions.
They are a distinct group list, not the process's effective GID. [1]

Investigate the filesystem operation under the actual filesystem user/group IDs
(fsuid/fsgid), supplementary groups, namespace mapping and access-control policy. Do not conclude
that changing a UID removed all group-based access. Conversely, a group name in
a configuration file does not establish current membership or access to every
object. Descriptor-based operations may retain an already opened object; use
reference-linux-descriptors-open-file-descriptions for that separate boundary.

## Kernel thread credentials and libc process-wide changes are distinct

Linux kernel user/group credentials are per-thread. POSIX requires process
threads to share credentials; the documented NPTL libc wrappers coordinate
credential changes across threads. [1] A direct system call is not automatically
the same operation as the corresponding coordinated library call.

Investigate the actual caller and wrapper path, affected threads, return status
and any interval of transition. One thread's credential snapshot does not clear
another thread's operation when synchronization or collection coverage is unknown.
Do not assume every libc has the same coordination implementation. Match the
observed library and kernel interface rather than a decompiler's function name.

## Credential numbers need their namespace and selecting event

Linux user namespaces map user/group identities between namespace contexts. [2]
The same displayed number can therefore describe different authority contexts.

Record thread/process generation, user namespace, mappings and credential event
before joining a request to an identity. A UID of zero inside a child namespace
is not by itself host-wide privilege. For capability checks, identify the user
namespace governing the resource; use reference-linux-capability-exec-evidence
and reference-linux-namespace-resource-scope. Missing mappings leave identity
correlation unresolved rather than proving an anonymous or privileged caller.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19, stable credential concepts and named
interfaces; no credential-structure offsets or universal Unix transition rules.

1. [credentials(7)](https://man7.org/linux/man-pages/man7/credentials.7.html): user/group identifiers, modifying IDs and per-thread versus NPTL behavior.
2. [user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html): identity mappings and capability scope.

Workflow: playbook-linux-authority-boundary. Credential possession is neither
evidence of malicious use nor complete authorization for an application's object.
