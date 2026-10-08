---
id: reference-windows-filesystem-path-reparse-boundaries
title: Windows filesystem path and reparse-point boundaries
kind: reference
topics: [windows, filesystem, paths, reparse-points, symlinks, hard-links, privileged-services]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows filesystem path and reparse-point boundaries

## Path prefixes and canonical names do not prove containment

Windows paths can vary by namespace, normalization, case behavior, relative
base, drive/current-directory state, and reparse processing. A textual prefix
check does not prove that the opened object remains beneath an intended
directory. Canonicalization performed before opening does not freeze the
filesystem against replacement or reparse changes.
Constructed lexical counterexample: C:\safe-other starts with C:\safe but is
not its child. Adding a separator fixes that string mistake, not filesystem
containment. Archive name rewriting needs the same name-versus-object distinction;
see `reference-parser-archive-extraction-effects`.
Unicode normalization, case mapping and visual similarity are different from
filesystem object identity; use `reference-parser-unicode-normalization-comparison`
for those text contracts, without treating them as a portable containment recipe.

## GetFullPathNameW uses shared current-directory state

GetFullPathNameW combines a name with current drive/directory state; success
does not verify that the resulting object exists. The current directory is
process-wide, so another thread can change the base between relative-name uses.
A fully qualified string removes that particular dependency, not reparse or
replacement races. [1]

## Hard links, junctions and reparse points

Hard links are multiple names for one file on the same volume; they are not
directory links. Junctions link directories and can cross local volumes. [2]
Reparse points are a broader mechanism used by symbolic links, mount points
and filesystem/filter-defined behaviors. An attribute or reparse tag is
evidence of a mechanism, not by itself evidence of attacker control. [3]

Inference: rejecting reparse points does not exclude hard-link aliases. Whether
an alias violates policy depends on who can create/control it, the object
access check, and whether the policy protects a name, object, or directory tree.

## CreateFileW symbolic-link and directory-open flags

For CreateFileW's symbolic-link case, FILE_FLAG_OPEN_REPARSE_POINT opens the
link itself; without it the target is opened. The flag cannot be used with
CREATE_ALWAYS. Opening a directory uses FILE_FLAG_BACKUP_SEMANTICS; that flag
alone does not grant backup/restore privileges or exempt ordinary callers from
access checks. [4] Inference: opening a final link itself does not prove all
ancestor components were trustworthy.

## Native OBJECT_ATTRIBUTES: OBJ_DONT_REPARSE and RootDirectory

For native object opens using OBJECT_ATTRIBUTES, OBJ_DONT_REPARSE fails with
STATUS_REPARSE_POINT_ENCOUNTERED if parsing encounters a reparse. RootDirectory
can name a filesystem directory or object-manager directory and supplies the
base for a relative ObjectName. [5] These are not identical to Win32 flags.
Inference: a root handle alone is not a confinement policy.

## GetFinalPathNameByHandleW result is handle evidence

GetFinalPathNameByHandleW takes an open file/directory handle. FILE_NAME_OPENED
requests the opened spelling; FILE_NAME_NORMALIZED requests normalization.
Volume flags select DOS, GUID, NT or no-volume form. DOS results use the
extended-path prefix. For SMB normalization, lack of access to a path component
can make the query fail even though the file handle exists. [6]

## GetFinalPathNameByHandleW lengths and failure are not checked paths

GetFinalPathNameByHandleW buffer capacity is in WCHAR units, not bytes. Success returns length without
the NUL; insufficient capacity returns required size including the NUL; other
failure returns zero. Zero is not a valid checked empty path. [6] Inference:
neither a failed query nor later normalization justifies falling back to an
unchecked privileged reopen by name. The final path cannot undo an earlier
side effect or prevent a subsequent name from resolving differently.

## File identity includes volume, format and lifetime

For supported filesystems, compare volume serial number and file index from
open handles, not file index alone. ReFS has 128-bit identifiers: use
GetFileInformationByHandleEx with FileIdInfo; the legacy 64-bit index is not
guaranteed unique there. File ID support is filesystem-specific and IDs can be
reused over time. They are not timeless, globally unique authorization tokens. [7]

Inference: comparing two live handles can test an object-identity hypothesis;
storing an old ID and later reopening a name requires fresh identity and
authorization evidence. Same-object identity does not imply unchanged contents.
Investigation order and race evidence are in playbook-vr-windows-cross-boundary.

## Sources

Reviewed 2026-10-02 against Microsoft path/open and file-information contracts.
Containment conclusions above are explicitly investigative inferences, not a
portable recipe or a claim that every filesystem implements identical behavior.

- [1. GetFullPathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfullpathnamew): lexical resolution and shared current-directory state.
- [2. Hard Links and Junctions](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions): file/directory and volume distinctions.
- [3. Reparse Point Operations](https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-point-operations): attributes, tags and reparse operations.
- [4. CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew): link handling, disposition and directory-open flags.
- [5. OBJECT_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes): RootDirectory and OBJ_DONT_REPARSE.
- [6. GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew): result formats, counts, errors and SMB qualification.
- [7. BY_HANDLE_FILE_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/ns-fileapi-by_handle_file_information): volume/ID comparison, ReFS and reuse.
