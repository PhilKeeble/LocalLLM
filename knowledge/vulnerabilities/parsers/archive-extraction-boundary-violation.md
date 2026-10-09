---
id: vulnerability-parser-archive-extraction-boundary-violation
title: Archive path, link, overwrite, or extraction-boundary violation
kind: vulnerability
topics: [parsers, archives, extraction, path-traversal, links, overwrite]
platforms: [cross-platform]
architectures: [any]
---

# Archive path, link, overwrite, or extraction-boundary violation

## Definition and violated invariant

An archive-extraction vulnerability occurs when member names, link targets, entry types, extraction order or preexisting filesystem objects cause a write or metadata effect outside the intended destination or onto an unauthorized object. Every filesystem effect must remain bound to the extraction root and policy after actual path resolution at the time of the operation.

Lexical removal of `..` is not a complete containment proof. Absolute paths, platform namespaces, separators, symlinks, hard links, junctions, case folding, collisions, special files and later archive entries can change the selected object.

## Conditions that establish the issue

Recover raw and decoded member names, entry types, link targets and their format-defined bases, normalization and platform path rules, extractor flags, destination root identity, existing and earlier-created objects, extraction order, open/create disposition, metadata restoration, privileges and resulting object. Prove attacker-controlled archive state reaches a filesystem effect outside policy.

For races, identify the actor able to change a path component between validation and use. For hard links or overwrite, show the affected object identity rather than relying on a suspicious spelling.

## Evidence that is not sufficient

An archive member containing `..`, an absolute-looking string, a symlink entry, duplicate name, executable bit or extraction API import is not sufficient. The active filter may reject or rewrite it, the platform may not support the entry type, or the member may never be extracted.

Successful extraction does not prove subsequent execution, loading or persistence. Those effects require their own reachable consumer.

## Investigation sequence

Replay entries in extraction order while tracking the actual filesystem tree, root handle, links, collisions and write disposition. Resolve member paths and link targets using the target platform's rules and the format-specific link base. Record the final opened object and authority for every relevant effect.

Inspect error and cleanup paths because partial extraction can leave attacker-selected files even when the archive is ultimately rejected. Treat cleanup paths as filesystem operations requiring the same containment proof.

## Constructed ordered-entry example

An archive first creates member `cache` as a symbolic link to an external directory, then contains regular member `cache/config`. A validator that checks only the lexical second name against the extraction root can approve it while the later create follows the link outside that root. The finding requires the extractor to create and follow the link in that order under the target platform and options; an extractor that rejects the link or opens relative to a protected directory object can change the result.

## Primitive and impact limits

The direct primitive can be unauthorized file creation, overwrite, truncation, link creation, permission change or special-file interaction. Code execution or privilege escalation requires a downstream loader, service, privileged target or other activation path.

## Related knowledge and primary sources

`reference-parser-archive-extraction-effects`, `reference-parser-archive-member-identity`, and filesystem resolution references cover entry and object selection. This profile repeats ordered filesystem effects and final-object binding locally.

Reviewed 2026-10-09 against libarchive's [disk-writer contract](https://raw.githubusercontent.com/libarchive/libarchive/master/libarchive/archive_write_disk.3), Python [tarfile extraction filters](https://docs.python.org/3/library/tarfile.html), and [MITRE CWE-22](https://cwe.mitre.org/data/definitions/22.html). The scenario is constructed.
