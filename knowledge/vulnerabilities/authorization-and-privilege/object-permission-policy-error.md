---
id: vulnerability-authorization-object-permission-policy-error
title: Incorrect file, object, ACL, mode, integrity-level, or security-label permission
kind: vulnerability
topics: [authorization, permissions, acl, file-modes, integrity-level, security-labels]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect file, object, ACL, mode, integrity-level, or security-label permission

## Definition and violated invariant

An object-permission vulnerability occurs when the effective access-control metadata on a file, registry key, IPC endpoint, named object, device, shared memory region or other resource grants an unintended subject a security-relevant right, or denies a boundary the system relies upon. The finding concerns the effective decision across applicable policy layers, not a suspicious permission string in isolation.

Read, content write, metadata change, ownership change, execute, create-child and policy-change rights are distinct. Platform discretionary ACLs, mandatory integrity or label policy, namespaces and capabilities can combine rather than replace one another.

## Conditions that establish the issue

Recover the initiating subject's effective token or credentials, object identity and namespace, owner and group, inherited and explicit permissions, ACL order and object-specific rights, mandatory label or integrity policy, capabilities or privileges, requested operation, existing handles, configuration and actual access result. Prove the unintended actor can acquire or exercise the right and connect it to a protected object or effect.

For creation defaults, include parent inheritance, umask or platform template and post-creation changes. For existing handles, determine whether policy changes are meant to revoke acquired authority.

## Evidence that is not sufficient

A world-writable-looking mode, permissive ACE, null-looking descriptor, low integrity, missing label, broad group, inherited flag or current ACL snapshot is not sufficient. Another policy layer may deny access, the object may be non-sensitive, the subject may not reach its namespace, or an existing handle may retain different authority.

Decode raw rights by object type. Identical numeric bits can name different operations, and Windows null and empty DACLs have opposite discretionary effects.

## Investigation sequence

Resolve the exact object and security descriptor or permission state at acquisition time. Model the access check using the effective subject, mapped operation-specific rights, ordered rules and mandatory policy, then follow the acquired handle or descriptor into use. Compare creator defaults and later mutations, retaining object generation and namespace.

At binary level, trace security-attribute construction, mode calculations, inheritance flags and result handling. A constant or ACL-building API does not prove the object was successfully created with that policy.

## Hypothetical writable-configuration example

```text
privileged service loads executable_path from configuration object C
unprivileged user has effective write permission to C
```

The permission becomes security-relevant only if the user can modify the live object generation, the service consumes the changed field under greater authority, and downstream validation does not reject it. A writable copy or unused template is not enough.

## Primitive and impact limits

The direct primitive is an unintended object-specific right such as read, write, create, execute or policy modification. Impact depends on object semantics and consumer. A writable configuration supports elevation or code execution only when the privileged consumer and activation path are established.

## Related knowledge and primary sources

Windows access-check, POSIX/Linux credential, Apple entitlement and filesystem-object references define platform layers. This profile keeps effective subject, exact right and live object together.

Reviewed 2026-10-09 against Microsoft [Access Control Model](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-model) and POSIX [`chmod`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/chmod.html) contracts as examples of distinct permission models. The example is hypothetical; platform-specific policy must be recovered in full.
