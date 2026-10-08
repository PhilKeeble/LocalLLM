---
id: reference-linux-path-resolution-identity
title: Linux directory-relative lookup, links, mounts and selected file identity
kind: reference
topics: [linux, paths, openat, openat2, symlinks, mounts, temporary-files, file-identity]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Path resolution and object selection

## A Linux path needs a starting directory and mount context

Linux absolute paths start at the process root; ordinary relative paths start
at its working directory. Lookup walks components with directory search checks
and can traverse links and mount points. [1]

For investigation, preserve path bytes, root, working directory, mount namespace
and the actual consumer's lookup rules. An analyst's resolution of the same text
can select another object. A normalized display is not proof of the target's
historical selection. Directory permissions, links and concurrent changes remain
relevant even when the final basename looks safe. Object authorization and
malicious-use interpretation need evidence beyond a path's appearance.

## openat anchors relative selection but is not automatic containment

Linux openat resolves a relative path against dirfd, or the working directory
for AT_FDCWD. An absolute path ignores dirfd. [2]

Investigation: identify the actual directory object and path consumed by the same
call. A directory descriptor stabilizes that starting object, not every child
entry or the complete traversal policy. It does not alone prevent '..', links
or mount traversal. If a boundary claims confinement, establish enforced resolution
constraints and error handling rather than a function-name match. Keep absolute
and relative cases separate so an isolated passage does not clear all openat uses.

## O_NOFOLLOW addresses the final component, with an O_PATH exception

For ordinary Linux open, O_NOFOLLOW rejects a symbolic link in the final component;
earlier symbolic links can still be followed. With O_PATH and O_NOFOLLOW, a final
link can instead be opened as a link object. [2]

Investigate the complete flags and selected operation. Presence of O_NOFOLLOW
cannot prove that the whole path is link-free or confined. Conversely, a returned
link descriptor does not mean its target was opened for data access. Separate
selection of the link itself from selection of its referent and preserve the
actual later operation. Do not transfer this named Linux flag contract to another
platform's similarly named API.

## openat2 resolution flags express different constraints

Where supported, Linux openat2 RESOLVE_BENEATH rejects resolution outside the
dirfd descendants, including absolute paths. RESOLVE_IN_ROOT instead interprets
resolution relative to that root, including absolute paths. RESOLVE_NO_SYMLINKS
prohibits symlink resolution; RESOLVE_NO_XDEV prohibits mount traversal, including
bind mounts. Magic links have their own explicit restriction. [3]

For investigation, bind supported flags and successful result to the actual
lookup. These restrictions are distinct, not interchangeable 'safe path' labels.
An unavailable feature or rejected lookup followed by unrestricted fallback can
change the boundary. Do not assume that a containment flag currently disabling
magic links is its enduring contract; inspect the explicit magic-link policy.

## Temporary creation and later reopening are separate selections

Linux O_CREAT with O_EXCL rejects an already existing path under the documented
filesystem contract. It does not certify every future operation at that name. [2]

For investigation, distinguish the object created/opened from a later pathname
lookup, and preserve directory mutability, file permissions, retained reference
and any rename/replacement interval. A unique-looking name is not proof of
exclusive creation. An exclusive creation result is not proof of later content
integrity. Filesystem-specific support and network filesystem behavior require
their own contract; do not generalize a local creation guarantee to every mount.

## Proc magic links differ from ordinary textual link traversal

Linux openat2 documents magic links such as proc executable/descriptor links;
their resolution can select objects beyond an apparent container path context.
RESOLVE_NO_MAGICLINKS addresses that mechanism. [3]

Investigate the selected object and supported resolution policy. A proc path is
not a complete authorization decision, and text-based prefix validation cannot
certify what a kernel reference ultimately selects. Preserve descriptor generation
and namespace identity under reference-linux-descriptors-open-file-descriptions.
This section describes selection limits, not evidence of an actual escape or
malicious operation in the examined program.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19, stable named lookup contracts. Feature
availability is a prerequisite, not an assumed kernel version or deployment default.

1. [path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html): root/working-directory lookup, components, links and mounts.
2. [open/openat](https://man7.org/linux/man-pages/man2/open.2.html): directory context, O_NOFOLLOW/O_PATH and exclusive creation.
3. [openat2](https://man7.org/linux/man-pages/man2/openat2.2.html): resolution constraints and magic-link distinctions.

Workflow: playbook-linux-file-object-boundary. A suspicious path is a lead; the
selected object and sensitive operation establish the relevant consequence.
