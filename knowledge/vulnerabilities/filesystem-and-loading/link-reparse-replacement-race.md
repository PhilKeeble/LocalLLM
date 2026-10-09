---
id: vulnerability-filesystem-link-reparse-replacement-race
title: Symlink, hard-link, junction, or reparse-point traversal and replacement
kind: vulnerability
topics: [filesystem, symlinks, hard-links, junctions, reparse-points, race-conditions]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Symlink, hard-link, junction, or reparse-point traversal and replacement

## Definition and violated invariant

A link or replacement vulnerability occurs when an attacker can make a privileged or trusted filesystem operation select a different object through symbolic links, hard links, junctions, reparse points, mount changes, rename/replacement, or name reuse between check and use. Authorization and validation must remain bound to the same opened object and resolution generation used by the sensitive operation.

Mechanisms differ. A hard link is another name for the same file; symbolic links and Windows reparse mechanisms can redirect traversal; junctions apply to directories; mount changes alter namespace traversal. A flag that affects the final component may not constrain ancestors, and opening a link object differs from opening its referent.

## Conditions that establish the issue

Recover directory and entry mutability, attacker's link/rename/mount rights, path components, check and open APIs, flags, root/directory handles, reparse or link policy, race interval, retries/fallbacks, returned handles, object identity before and after the check, and sensitive operation. Prove an attacker-controlled namespace change makes the operation target an unauthorized object.

For hard links, establish creation rights, filesystem/volume constraints, existing object permissions and whether policy protects names or underlying objects. For reparse points, decode the actual tag and consumer behavior rather than treating the attribute as one universal symlink.

## Evidence that is not sufficient

A symlink, hard-link count, reparse attribute, junction, `lstat`, `O_NOFOLLOW`, root handle, canonical path, rename, or race window is not sufficient. The attacker may lack mutation rights, the sensitive operation may use a retained verified handle, resolution controls may cover all components, or the selected object may remain authorized.

A reparse point can be legitimate, and absence of symbolic links does not exclude hard-link aliases or replacement races.

## Investigation sequence

Construct an object-selection timeline containing each name lookup, directory object, component, flags, returned handle, identity query, close/reopen, rename/reparse change and operation. Mark which checks describe strings, link objects, referents or open handles. Compare object identity at authorization with the object used for read, write, execute, delete, permission change or ownership change.

At binary level, locate separate metadata-check and open calls, final versus ancestor no-follow semantics, handle-relative operations, fallback paths, and name-based reopen. Preserve volume/file identity with lifetime scope where supported.

## Constructed check-then-open example

```c
struct stat metadata;
if (lstat(candidate_path, &metadata) != 0 || S_ISLNK(metadata.st_mode))
    reject();
int fd = open(candidate_path, O_WRONLY | O_TRUNC);
```

An attacker who can replace `candidate_path` between `lstat` and `open` can make the check describe one entry while the write opens another, including a symlink target. The finding requires that mutation right and a successful interleaving. Even without a race, this final-component check says nothing about symbolic links in ancestor components.

## Constructed x86-64 control-flow shape

```asm
; Illustrative System V AMD64 shape. r12 = candidate pathname.
mov     rdi, r12
lea     rsi, [stat_buffer]
call    lstat
; metadata checks omitted
mov     rdi, r12                ; a second name lookup, not use of an already-open handle
mov     esi, O_WRONLY_OR_TRUNC
call    open
```

The two lookups identify a possible substitution interval; they do not prove another actor can mutate the namespace or that the second lookup selects a different object. Recover flags, directory permissions, identities, and the sensitive write.

## Primitive and impact limits

The direct primitive is substitution or aliasing of the filesystem object used by a sensitive operation. Consequences can include privileged overwrite, disclosure, deletion, permission or ownership change, executable/library replacement, or sandbox escape. Impact depends on mutation rights, process authority, filesystem semantics, selected object and operation.

## Related knowledge and primary sources

`reference-linux-path-resolution-identity` and `reference-windows-filesystem-path-reparse-boundaries` define link and handle distinctions. This profile keeps attacker mutation rights and same-object binding as required proof.

Reviewed 2026-10-09 against POSIX [`lstat`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/lstat.html), Linux [`open`](https://man7.org/linux/man-pages/man2/open.2.html) and [`openat2`](https://man7.org/linux/man-pages/man2/openat2.2.html), and Microsoft [Hard Links and Junctions](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions), [Reparse Point Operations](https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-point-operations), and [`CreateFileW`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew). The source and assembly are constructed.
