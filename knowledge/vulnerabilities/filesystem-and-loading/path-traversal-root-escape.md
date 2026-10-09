---
id: vulnerability-filesystem-path-traversal-root-escape
title: Path traversal above an intended root
kind: vulnerability
topics: [filesystem, path-traversal, containment, separators, decoding]
platforms: [cross-platform]
architectures: [any]
---

# Path traversal above an intended root

## Definition and violated invariant

Path traversal occurs when attacker-controlled path components cause resolution outside the directory tree authorized by the application. The final filesystem object must be selected under an enforced root and component-resolution policy after all relevant decoding, separator handling, normalization, and link traversal.

Textual `..` is one mechanism, not the definition. Mixed separators, encoded separators or dots, empty components, platform aliases, archive-name rewriting, and later decoding matter only as the actual consumer interprets them. POSIX and Windows path grammars, roots, current-directory state, case behavior, and link mechanisms differ.

## Conditions that establish the issue

Recover raw input, encoding and decode stages, path grammar, accepted separators, base/root object, current directory, component normalization, absolute-path handling, links and mounts, final open API and flags, race window, selected object, and operation. Prove attacker input makes the actual lookup select an object outside the intended root or changes which protected object is accessed.

Containment must be tied to the opened object and lookup generation. A normalized string checked before a later name-based open can become stale or can disagree with link-aware resolution.

## Evidence that is not sufficient

A `..` substring, encoded dot, path join, normalization call, relative path, failed open, or file outside the root is not sufficient. The component may be literal in that grammar, decoding may stop before it gains meaning, a kernel-enforced resolution policy may reject escape, or the outside file may be opened by an unrelated path.

Removing literal `../` does not establish safety across platforms or decode layers. Conversely, accepting `..` can be intentional when the effective root and operation permit it.

## Investigation sequence

Build a path-stage ledger containing raw bytes, decoded string, separator rules, component list, base directory object, normalization, link/mount traversal, final API arguments, returned handle or descriptor, and object identity. Follow fallback paths when constrained lookup fails. Compare the authorization root with the actual process root, mount namespace, drive/current-directory state, or sandbox view.

At binary level, recover string builders, decoder calls, normalization helpers and the exact open call. Confirm whether the path is relative or absolute at the consumer and bind the returned handle to the sensitive read, write, execute, or delete.

## Constructed relative traversal example

```c
string path = root_text + "/" + submitted_name;
int fd = open(path.c_str(), O_RDONLY);
```

If `submitted_name` is `../../secrets/key` and ordinary POSIX path resolution is used, component traversal can move above `root_text` before selecting the file. The finding requires the process's actual root and working/mount context, successful resolution, and an unauthorized object. String concatenation alone does not prove the object exists or is accessible.

## Constructed x86-64 call shape

```asm
; Illustrative System V AMD64 shape after path construction. r12 = combined path.
mov     rdi, r12
xor     esi, esi                ; O_RDONLY in this constructed target
call    open
```

This identifies the final name-based lookup only after the imported prototype and flag domain are confirmed. It does not show the path contents, root policy, successful result, or selected object; recover those separately.

## Primitive and impact limits

The direct primitive is selection of a filesystem object outside the authorized tree. Consequences can include file disclosure, overwrite, deletion, configuration change, credential access, or loading/execution. Impact depends on operation, filesystem permissions, process authority, link/mount context, object contents, and later consumption.

## Related knowledge and primary sources

`reference-linux-path-resolution-identity`, `reference-windows-filesystem-path-reparse-boundaries`, archive path references, and layered-decoding profiles provide platform and transformation details. This profile keeps final object selection as the required proof.

Reviewed 2026-10-09 against Linux [`path_resolution(7)`](https://man7.org/linux/man-pages/man7/path_resolution.7.html), POSIX [pathname resolution](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html#tag_04_16), Microsoft [Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file), and Linux [`openat2`](https://man7.org/linux/man-pages/man2/openat2.2.html) for an example of kernel resolution constraints. The code and assembly are constructed.
