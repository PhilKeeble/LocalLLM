---
id: vulnerability-filesystem-unsafe-overwrite-permission-ownership-transition
title: Unsafe file overwrite, permission preservation, or ownership transition
kind: vulnerability
topics: [filesystem, overwrite, permissions, ownership, replacement, updates]
platforms: [cross-platform]
architectures: [any]
---

# Unsafe file overwrite, permission preservation, or ownership transition

## Definition and violated invariant

An unsafe overwrite or metadata-transition vulnerability occurs when a trusted process creates, truncates, replaces, renames, copies, or publishes a file without preserving the required object identity, contents, owner, group, ACL, mode, labels, alternate streams, integrity metadata, or durability semantics. The final published object and its metadata must satisfy the policy for that destination and must be selected under the intended authority.

In-place truncation, write-to-temporary then rename/replace, copy, and delete/recreate have different object and metadata effects. POSIX rename changes which object a name references and does not merge the replaced object's mode or owner into the replacement. Windows replacement and copy APIs have their own metadata and stream behavior. No generic "atomic write" label proves correct authorization or metadata.

## Conditions that establish the issue

Recover destination control, open/create disposition, link handling, existing versus new object, requested/effective permissions, umask, owner/group, ACL and labels, temporary object directory, copy/rename/replace API and flags, cross-filesystem fallback, metadata application order, error handling, durability requirements, and final identity. Prove the resulting object is writable/readable/executable by an unintended principal, loses required protections, retains forbidden authority, or overwrites an unauthorized object.

For privileged ownership or permission changes, establish which credentials apply to creation and metadata operations and whether failures are ignored. For updates, bind verified content to the final installed object after replacement.

## Evidence that is not sufficient

A write, truncate, rename, temporary file, chmod/chown, ACL call, changed inode/file ID, or permission difference is not sufficient. Replacement can be intended, metadata can be explicitly re-established, and the final object may still meet policy.

Atomic namespace replacement does not prove durable storage, preserved metadata, verified content or correct destination authority. Keep these claims separate.

## Investigation sequence

Build an object/metadata ledger for the original destination, temporary object and final published object. Record identity, owner, group, mode/ACL, labels, streams/attributes, content hash, open handles and each operation/result. Trace failures and fallbacks, especially copy-after-rename-failure and permission changes performed before versus after publication.

At binary level, recover create modes, dispositions, share flags, rename/replace calls, metadata APIs and return checks. Follow the final handle or reopened name into consumption and compare it with the object whose content was verified.

## Constructed POSIX replacement example

```c
int fd = open(temp_path, O_WRONLY | O_CREAT | O_EXCL, 0600);
write_complete(fd, new_content);
close(fd);
rename(temp_path, published_path);
```

If replacement succeeds on one filesystem, `published_path` now names the temporary file object with its metadata; it does not inherit the replaced file's mode and owner by textual name. This becomes a vulnerability only when policy required different metadata or ownership and the application fails to establish it. The example also does not prove durable content because flush and directory-durability steps are absent.

## Primitive and impact limits

The direct primitive can be unauthorized overwrite, publication with excessive or insufficient access, loss or retention of metadata, verified-to-installed object substitution, or incomplete update state. Consequences include disclosure, tampering, persistence, service failure, or later code/configuration loading. Filesystem permissions, process authority, consumer behavior and recovery policy bound impact.

## Related knowledge and primary sources

Filesystem identity, link-race, update-binding, and platform ACL references provide detailed contracts. This profile keeps content, object identity, metadata and durability as separate review dimensions.

Reviewed 2026-10-09 against POSIX [`open`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html), [`rename`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html), [`fchmod`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fchmod.html), and Microsoft [`ReplaceFileW`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew) and [`CopyFileExW`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-copyfileexw). The example is constructed and POSIX-scoped.
