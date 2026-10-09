---
id: vulnerability-resource-storage-disk-log-cache-exhaustion
title: Disk, log, database, cache or temporary-storage exhaustion
kind: vulnerability
topics: [resource-exhaustion, disk, logging, database, cache, temporary-files]
platforms: [cross-platform]
architectures: [any]
---

# Disk, log, database, cache or temporary-storage exhaustion

## Definition and violated invariant

This vulnerability lets an actor grow persistent or temporary storage until a filesystem, database, journal, log, cache, quota or device can no longer serve required operations. The violated invariant is that stored data must be size- and lifetime-bounded, charged to the responsible principal and reclaimed without sacrificing required security or integrity records.

Byte capacity, inode or record counts, journal space, database transaction state and write endurance are distinct resources. Free bytes alone do not establish available capacity for the requested operation.

## Conditions that establish the issue

Identify the attacker-controlled content or event, storage amplification, destination, quota scope, rotation or eviction, transactional overhead, cleanup and the first exhausted resource. Prove reachable requests can outpace reclamation or fill a retained set enough to deny a security-relevant write or read.

Include alternate partitions, replicas, indexes, snapshots, temporary staging and failure logs. A rejected request can still consume space if diagnostics or rollback artifacts are retained.

## Evidence that is not sufficient

A file write, verbose logging, cache insertion, database row or large upload is not sufficient. Effective quotas, bounded rotation, transactional rollback, eviction, isolated volumes or caller backpressure may prevent shared exhaustion. A disk-full error does not identify which actor or retention policy caused it.

Do not recommend deleting audit or integrity records without preserving their security requirement; the vulnerability analysis concerns missing bounds and isolation, not indiscriminate reclamation.

## Investigation sequence

Trace input into every stored representation and count primary data, metadata, indexes, journals, copies and temporary files. Recover quotas by principal, directory, database, tenant and device. Follow commit, rollback, crash recovery, rotation, eviction and deletion paths, including errors caused by full storage.

At binary level, locate append/write/insert operations, generated names, retention checks and cleanup dispatch. Determine whether size checks reserve capacity atomically or race with concurrent writers. Record which operations fail and whether failure handling loops or corrupts state.

## Constructed example

A hypothetical unauthenticated parser logs the complete rejected message before returning an error. Each 1 MiB input produces a 1 MiB retained log record, rotation is disabled and the log shares a filesystem with service state. Repeated invalid requests can exhaust that filesystem if no upstream body or actor quota intervenes.

The mere logging call is not proof; effective request limits, log truncation, rate limits, compression and separate storage change the result.

## Primitive and impact limits

Report bytes or records per action, amplification, write rate, retained duration, quota and affected storage scope. Direct effects include denied writes, failed transactions, unavailable service or lost diagnostics. Data corruption or privilege change requires a separate unsafe failure path.

## Related knowledge and primary sources

Upload, logging and cleanup profiles describe common producers. This profile owns storage accounting and exhaustion consequences.

Reviewed 2026-10-09 against POSIX [`write()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/write.html) error contracts including `ENOSPC` and quota failure, [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html) and [MITRE CWE-400](https://cwe.mitre.org/data/definitions/400.html) mapping guidance. Filesystem, database and cache capacity rules remain implementation-specific.
