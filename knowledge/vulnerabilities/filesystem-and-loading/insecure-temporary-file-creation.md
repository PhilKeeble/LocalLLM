---
id: vulnerability-filesystem-insecure-temporary-file-creation
title: Predictable or insecure temporary-file creation and name reuse
kind: vulnerability
topics: [filesystem, temporary-files, races, symlinks, exclusive-creation, permissions]
platforms: [cross-platform]
architectures: [any]
---

# Predictable or insecure temporary-file creation and name reuse

## Definition and violated invariant

An insecure temporary-file vulnerability occurs when an attacker can predict, pre-create, replace, redirect, read, or reuse a temporary pathname or object so that a trusted operation acts on attacker-selected content or exposes trusted content. Creation must atomically select a new object with appropriate access, and later operations must remain bound to that object rather than reopen a mutable name.

Random-looking or unique names are not the invariant. Predictability matters only with namespace access or disclosure; exclusive creation can protect a predictable candidate against pre-existing entries, while later close-and-reopen can reintroduce substitution. Temporary-directory permissions, umask/ACL, cleanup, crash behavior and cross-filesystem semantics matter.

## Conditions that establish the issue

Recover temporary-directory selection and trust, name generation and entropy source, attacker directory/entry rights, creation API and flags/disposition, exclusivity, symlink/reparse behavior, requested and effective permissions, inherited descriptors/handles, retained reference, close/reopen/rename/publish sequence, cleanup, and sensitive data or operation. Prove another actor can win selection, redirect use, access content, or replace the object during its relevant lifetime.

Separate name reservation from file creation. A function that returns a candidate name does not necessarily create the object; a function that creates an empty file does not guarantee later code reuses that same handle.

## Evidence that is not sufficient

A `/tmp` path, process ID in a name, low apparent entropy, temporary API, world-readable directory, existing file, or missing cleanup is not sufficient. Atomic exclusive creation, private directories, retained unnamed files or handles, correct permissions, and race-resistant publication can change the conclusion.

Failure to delete a temporary file can be information disclosure or resource leakage without being a name-reuse race. Identify the actual violated property.

## Investigation sequence

Build a lifecycle timeline from directory selection through candidate generation, creation, writes, flush, close, reopen, rename/link, handoff and deletion. Record every returned descriptor/handle and every later name lookup. Compare requested modes with effective umask, ACL and inherited access. Identify which principal can observe or mutate the directory during each interval.

At binary level, recover creation disposition and flags, loop behavior on collisions, randomness failure handling, handle inheritance and close/reopen paths. Bind any replaced object to the final sensitive operation.

## Constructed POSIX temporary-file example

```c
snprintf(path, sizeof path, "/tmp/report-%u", (unsigned)getpid());
int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0600);
write_report(fd, secret_report);
```

In a directory another user can modify, a predictable existing pathname can be selected because this call does not request exclusive creation; ordinary `open` can follow a symbolic link under its actual flags. The finding requires attacker namespace access, a pre-created entry or race, successful open, and an unauthorized target or disclosure. Mode `0600` applies when a new file is created and does not replace permissions on an existing target.

## Constructed x86-64 flag evidence

```asm
; Illustrative System V AMD64 shape. r12 = predictable path.
mov     rdi, r12
mov     esi, O_WRONLY_OR_CREAT_OR_TRUNC ; no O_EXCL in this constructed value
mov     edx, 0x180              ; mode 0600 in octal
call    open
```

The missing exclusive bit matters only after the flag constant is decoded for the target ABI and attacker control of the directory entry is established. A decompiler's symbolic flag guess or predictable name alone does not prove substitution.

## Primitive and impact limits

The direct primitive can be pre-creation, link redirection, content substitution, unauthorized read, or replacement between lifecycle stages. Consequences include privileged overwrite, secret disclosure, corrupted processing, code/configuration substitution, persistence, or denial of service. Directory policy, effective identity, retained handles and target object permissions bound impact.

## Related knowledge and primary sources

`reference-linux-path-resolution-identity`, Windows path/reparse references, and file-authority references provide platform detail. This profile keeps atomic creation and retained-object identity distinct from name randomness.

Reviewed 2026-10-09 against POSIX [`open`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html) and [`mkstemp`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/mkstemp.html), Linux [`open(2)`](https://man7.org/linux/man-pages/man2/open.2.html), and Microsoft [Creating and Using a Temporary File](https://learn.microsoft.com/en-us/windows/win32/fileio/creating-and-using-a-temporary-file). The source and assembly are constructed; exact flags and filesystem behavior remain target-specific.
