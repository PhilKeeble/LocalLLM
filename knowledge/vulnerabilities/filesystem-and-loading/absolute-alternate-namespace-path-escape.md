---
id: vulnerability-filesystem-absolute-alternate-namespace-path-escape
title: Absolute, drive, UNC, device, or alternate-namespace path escape
kind: vulnerability
topics: [filesystem, paths, windows, unc, devices, namespaces, containment]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Absolute, drive, UNC, device, or alternate-namespace path escape

## Definition and violated invariant

An absolute or alternate-namespace escape occurs when a path intended to name an object beneath an application-controlled base instead selects a filesystem root, drive, network share, device, object namespace, or other independent naming domain. The application must constrain the path form and namespace consumed by the final API, not merely reject parent components.

Windows distinguishes drive-qualified, drive-relative, UNC, device and extended-length forms, with API-specific normalization and reserved names. POSIX absolute paths begin at the process root and ignore an `openat` directory argument. Archive, URI, runtime and language path helpers can apply their own absolute-path and join rules before the operating-system call.

## Conditions that establish the issue

Recover the selected platform/API grammar, all prefixes and separators, drive/current-directory state, UNC host/share, device or object namespace, path-combination behavior, normalization flags, process root or mount namespace, final call, and selected object. Prove attacker data selects a namespace or root outside the intended base and reaches an unauthorized operation.

For network paths, establish outbound resolution and credentials as separate facts. For device paths, establish the named device and control operation rather than treating the prefix alone as impact.

## Evidence that is not sufficient

Absence of `..`, a colon, leading slash, backslash pair, reserved-looking name, `\\?\` prefix, or path-combine API is not sufficient. The consumer may reject the form, treat it as literal data, anchor it under a root, or lack access to the named object.

Likewise, an absolute path can be authorized input under the product policy. The defect requires disagreement with the intended namespace boundary.

## Investigation sequence

Classify the input at every layer as relative, rooted, drive-relative, drive-absolute, UNC, device, extended, URI, archive member, or runtime-specific form. Record which base is ignored or replaced, which normalization is bypassed or changed, and which credentials and namespace view the final call uses. Bind the returned handle to its object identity and operation.

At binary level, inspect prefix tests, path helper flags, wide/narrow conversions, current-directory reads and the final native call. Do not infer Win32 parsing from a generic decompiler type if the code calls a native object-manager API.

## Constructed Windows absolute-path example

```c
if (contains_parent_component(submitted_path))
    reject();
HANDLE file = CreateFileW(submitted_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
```

Rejecting parent components does not constrain `submitted_path` to an application directory because the final call consumes the submitted path directly. A drive-absolute or UNC name can select another root or host if accepted by this call and accessible to the process. The finding requires the actual string form, successful object selection and policy violation; a prefix alone is not enough.

## Primitive and impact limits

The direct primitive is selection of an object in an unintended root or namespace. Consequences can include local or network file access, credential-bearing outbound connections, device operations, configuration overwrite, or execution through a selected object. Access checks, namespace isolation, share permissions, device ACLs and the final operation bound impact.

## Related knowledge and primary sources

`reference-windows-filesystem-path-reparse-boundaries`, Windows namespace references, and Linux path-resolution references provide platform-specific details. This profile keeps namespace selection distinct from `..` traversal and link replacement.

Reviewed 2026-10-09 against Microsoft [Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file), [`CreateFileW`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew), POSIX [pathname resolution](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html#tag_04_16), and Linux [`openat`](https://man7.org/linux/man-pages/man2/open.2.html). The source is constructed and does not treat any prefix as universally accepted.
