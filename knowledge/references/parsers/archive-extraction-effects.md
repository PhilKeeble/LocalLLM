---
id: reference-parser-archive-extraction-effects
title: Archive extraction paths, links, overwrite and metadata effects
kind: reference
topics: [parsers, archives, extraction, path-traversal, symlinks, hard-links, overwrite, libarchive]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Archive extraction filesystem effects

## libarchive disk-writer path controls are separate options

In libarchive's disk-writer API, ARCHIVE_EXTRACT_SECURE_NOABSOLUTEPATHS rejects
absolute paths; SECURE_NODOTDOT rejects dot-dot components; SECURE_SYMLINKS
checks symlink-altered destinations. These checks are not default-enabled.
With SECURE_SYMLINKS plus UNLINK, intermediate symlinks are removed when possible
instead of invariably causing rejection. [1] Flag names here share the
ARCHIVE_EXTRACT_ prefix. These are API rules, not every frontend's defaults.

Investigative inference: recover the complete option bitmask and wrapper's path
rewriting before judging containment. Rejecting one spelling of traversal does
not establish that filesystem resolution stays in the intended directory. For
Windows object/namespace distinctions, use
`reference-windows-filesystem-path-reparse-boundaries`.

## Tar symbolic-link and hard-link target bases differ

For relative Python TarInfo.linkname values, a symbolic-link target uses the
link's directory and a hard-link target uses the archive root. TarInfo types
distinguish regular files, directories, links, FIFOs and devices. [2]

Investigative inference: keep member name, entry type and link target separate.
A filter that validates only member names has not necessarily validated link
destinations. Determine whether the extractor creates, skips, rejects or
materializes each type; tar metadata alone does not prove the filesystem effect.
A link supported by the format is not automatically supported by the target OS.

When selected, Python tarfile's data filter rejects absolute/out-of-destination
link targets and special files such as devices and pipes. [2] Identify the actual
filter in the target; this does not describe every version's default policy.

## Extraction order changes the filesystem seen by later entries

Python tarfile calls its extraction filter just before each member and permits
inspection of current disk state. [2]

Constructed investigation model: one entry creates a directory link and a later
entry names a child beneath it. The relevant question is whether the later open
follows that link, rejects it or replaces it. Checking all names against an
initial empty-directory model does not answer that question. Also distinguish
archive-created state from concurrent changes by another principal; do not
claim a race unless the needed interleaving and authority are feasible.

## Overwrite by truncation differs from unlink-and-recreate

libarchive's disk writer normally truncates existing regular files without
breaking their hard links. ARCHIVE_EXTRACT_NO_OVERWRITE prevents overwrite;
ARCHIVE_EXTRACT_UNLINK instead removes existing objects before creation. [1]

Investigative inference: an apparently contained name can alias an existing
object. Truncating through that name affects its other hard-link aliases;
unlinking a name and creating a new object is a different operation. Recover
the destination's preexisting state and actual write disposition. A filename
collision is not sufficient proof of arbitrary overwrite: show controllable
content, the affected object, successful authority and the forbidden effect.

## Per-file safe writes are not an archive transaction

ARCHIVE_EXTRACT_SAFE_WRITES uses a temporary file and rename for file publication.
[1] Python tarfile extraction can leave partial output when aborted and does
not automatically clean it up. [2]

Investigative inference: a complete individual file does not imply a complete,
verified package. Recover whether consumers can read early outputs, when the
application declares success, and what it does with files after an error.
Cleanup by attacker-influenced names is another path-resolution operation;
do not assume a cleanup label makes that operation safe.

## Restored permissions and directory finalization are later effects

libarchive ARCHIVE_EXTRACT_PERM restores full modes rather than applying umask;
restoring SUID/SGID also requires matching ownership. Directory permissions are
finalized at archive close. Owner IDs, extended ACLs and extended attributes
are not restored by default. [1]

Investigative inference: inspect metadata options, privileges and close/error
handling separately from content writes. A recovered mode bit is not proof
that it takes effect or grants privilege on the destination system. In malware
analysis, link extraction to subsequent execution, loading or persistence use;
an executable permission or archive library import alone proves none of those.

## Sources and scope

Reviewed 2026-10-02. Current libarchive manual and Python 3.14.8 API documentation
provide concrete contracts; target flags, wrappers, platform and release matter.
Constructed models and investigative consequences are not observed specimens.

1. [libarchive archive_write_disk manual](https://raw.githubusercontent.com/libarchive/libarchive/master/libarchive/archive_write_disk.3): extraction options, defaults, hard links and deferred directory permissions.
2. [Python tarfile](https://docs.python.org/3/library/tarfile.html): TarInfo types/linkname, extraction filters and partial-output warning.
