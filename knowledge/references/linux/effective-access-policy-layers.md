---
id: reference-linux-effective-access-policy-layers
title: Linux discretionary permissions, POSIX ACLs, capabilities, LSM and seccomp layers
kind: reference
topics: [linux, permissions, posix-acl, capabilities, lsm, seccomp, authorization]
platforms: [linux]
architectures: [any]
---

# Linux effective access policy layers

## Path resolution and discretionary access are distinct steps

Linux pathname resolution selects objects through a starting directory, mount namespace and link/mount traversal. Directory search permission is checked along the path, and the final operation applies its object and requested access rules. A writable final file mode does not prove the caller can traverse the path; a validated path string does not prove which inode is selected after resolution.

Recover caller filesystem credentials and supplementary groups, namespace/id mappings, each relevant directory, final inode, operation, mount flags and object identity. Use `reference-linux-path-resolution-identity` for resolution details.

## POSIX ACLs refine the discretionary decision

Linux POSIX access ACLs can supply named user/group entries and a mask that limits named-user, group-owner and named-group permissions. The ACL decision is not computed by simply ORing every matching entry, and the mode group bits correspond to the ACL mask when an extended ACL exists. Default ACLs affect inheritance on newly created objects rather than access to the directory itself.

Inspect the effective access ACL on the selected inode, caller IDs/groups and requested operation. An `ls -l` mode display alone can omit the named entries needed to explain access.

## Capabilities are scoped privilege inputs

Effective Linux capabilities can bypass selected discretionary checks, but each capability has defined operations and is evaluated in relation to the user namespace governing the resource. A capability string, permitted-set bit or UID 0 in a child namespace does not establish effective authority for a host object.

Recover the effective set and governing namespace at the operation, plus bounding/ambient/inheritable transitions when execution is involved. Use `reference-linux-capability-exec-evidence` for set transitions.

## LSM and seccomp add different restrictions

Linux Security Module policy can deny operations beyond discretionary access and capability checks. Seccomp filters act on syscall metadata and return an action; they do not generally authorize pointed-to objects and do not replace filesystem or LSM policy. Filter coverage can differ by thread unless synchronization rules are used.

Treat DAC/ACL, capability, LSM and seccomp evidence as separate layers and preserve the final operation result. Passing one layer is not proof of complete authorization, while a denial at any effective mandatory layer can stop the path.

## Primary sources and scope

Reviewed 2026-10-09 against Linux man-pages [`path_resolution(7)`](https://man7.org/linux/man-pages/man7/path_resolution.7.html), [`acl(5)` access algorithm](https://man7.org/linux/man-pages/man5/acl.5.html), [`capabilities(7)`](https://man7.org/linux/man-pages/man7/capabilities.7.html), kernel [LSM documentation](https://docs.kernel.org/security/lsm.html), and kernel [seccomp filter documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html). Filesystem, LSM and kernel configuration affect the realized policy.
