---
id: vulnerability-filesystem-canonicalization-prefix-check-mismatch
title: Filesystem canonicalization and prefix-check mismatch
kind: vulnerability
topics: [filesystem, canonicalization, prefixes, paths, containment, check-use]
platforms: [cross-platform]
architectures: [any]
---

# Filesystem canonicalization and prefix-check mismatch

## Definition and violated invariant

A filesystem canonicalization mismatch occurs when a path is authorized under one textual or resolved representation but a later operation uses a different representation, base, comparison rule, or filesystem generation. A containment check must compare complete path components under the target namespace and remain bound to the same object selected for the sensitive operation.

String prefixes are not path ancestry. `/srv/safe-other` has the text prefix `/srv/safe` without being its child; case rules, separators, drive/UNC forms, Unicode, short/long names and trailing syntax depend on the platform and API. Even a correct canonical path checked before a later name-based open does not freeze links, mount points, renames or current-directory state.

## Conditions that establish the issue

Recover raw and decoded paths, base/root, canonicalization or full-path API and result handling, comparison length and boundary, case/Unicode policy, separator rules, existence requirements, link/reparse behavior, current directory, time between check and use, final API arguments, returned handle and object identity. Prove the accepted check and final lookup select different authorization domains or objects.

Distinguish lexical normalization from filesystem-backed resolution and handle-derived final names. Neither is automatically a containment primitive; the required relation depends on policy and the actual lookup.

## Evidence that is not sufficient

A canonicalization call, prefix comparison, case-insensitive comparison, normalized path, separator, handle-derived name, or time gap is not sufficient. The comparison may enforce a component boundary, the final operation may use the verified handle, or the namespace may be immutable to the attacker.

A failed canonicalization followed by rejection is not a bypass. Trace error fallbacks and the path actually consumed.

## Investigation sequence

Lay out every path representation and operation in order, including input, decoded value, combined path, canonical result, compared prefix, comparison length/mode, opened name, returned handle and final identity. Mark changes to current directory or namespace and attacker mutation rights. Test the logical component relation rather than only byte prefixes.

At binary level, recover comparison return semantics, exact lengths, case flags, delimiter checks, error branches and whether the open consumes the checked buffer or reconstructs another path. Follow any close-and-reopen by name.

## Constructed prefix-check example

```c
string full = lexical_absolute(submitted_path);
if (!starts_with_bytes(full, "/srv/safe"))
    reject();
int fd = open(full.c_str(), O_RDONLY);
```

The byte prefix accepts `/srv/safe-other/secret`, which is not a descendant component of `/srv/safe`. The finding requires this exact comparison and an unauthorized successful open. Adding a separator boundary fixes this lexical counterexample but does not by itself address link traversal, namespace races or platform-specific aliases.

## Constructed comparison shape

```asm
; Illustrative System V AMD64 shape. r12 = candidate, prefix length is fixed at 9.
mov     rdi, r12
lea     rsi, [safe_prefix]
mov     edx, 9
call    strncmp
test    eax, eax
jne     .reject
mov     rdi, r12
call    open_candidate
```

This shows a fixed byte-prefix check without a component-boundary test only after helper semantics and prefix length are confirmed. It does not prove the candidate's contents, filesystem interpretation, or successful outside-root selection.

## Primitive and impact limits

The direct primitive is authorization of a path representation that does not bind the object used by the filesystem operation. Consequences can include outside-root read/write/delete, wrong-object authorization, configuration replacement, or loader selection. The operation, object permissions, process authority and later consumer determine impact.

## Related knowledge and primary sources

`reference-linux-path-resolution-identity`, `reference-windows-filesystem-path-reparse-boundaries`, Unicode comparison references, and link-race profiles provide platform details. This profile repeats component-boundary and same-object requirements locally.

Reviewed 2026-10-09 against POSIX [pathname resolution](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html#tag_04_16), Linux [`realpath`](https://man7.org/linux/man-pages/man3/realpath.3.html), Microsoft [`GetFullPathNameW`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfullpathnamew), and [`GetFinalPathNameByHandleW`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew). The source and assembly are constructed.
