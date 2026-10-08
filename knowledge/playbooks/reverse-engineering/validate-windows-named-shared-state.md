---
id: playbook-re-windows-named-shared-state
title: Validate Windows named-object and shared-memory trust boundaries
kind: playbook
topics: [windows, namespaces, shared-memory, initialization, bounds, authorization]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Investigate one shared-object protocol
Use for binaries exchanging authority or state through named synchronization
objects and mappings. Separate namespace resolution, create/open outcome,
authorization, record validity, publication and resource lifetime.

## Establish the actual namespace and creation outcome
Reviewed 2026-10-02. Preserve API, full name, encoding/case, host/session,
private-boundary descriptor and object type. Trace name construction and who
can influence it. Recover create/open result and immediate documented last-error
status before another call changes it. Inspect the returned object's security
and size/state; supplied creation parameters do not prove a new object existed.

For a collision candidate, establish the other actor's ability to occupy that
exact namespace and type, the victim's reachable response, and the resulting
policy violation. Distinguish denied startup, accepted foreign data and merely
different objects with similar spellings. Do not create competing objects on
a live service's namespace to test a hypothesis. Factual basis:
reference-windows-object-namespaces-collisions.

## Recover the shared record and every participant's view
Trace mapping-handle acquisition, rights, backing, local mapping offsets/bases,
extents, protection and result. Identify all writers and initialization owners.
Recover field widths, offset origin, byte order, record version, generation and
length/capacity relationships. Validate the full offset/length range against
retained actual bounds, not a requested size or merely readable pages.

Identify the publication protocol and whether validation consumes the same
retained bytes later used. Include read-only peer views, private-copy limits,
reloads, nested offsets, copy-on-write mode and crash recovery. A ready flag,
successful wait or known object name is not enough to prove authenticated,
consistent payload. Facts: reference-windows-shared-mapping-evidence and
reference-concurrency-mutable-validation-double-fetch.

## Follow failures, shutdown and the exact observed effect
Follow existing-object initialization paths, map failure, deferred paging faults,
abandoned mutexes, partial writes, peer restart and unmap/close races. Retain
original view bases and aliases through cleanup. Distinguish publication,
visibility, persistence and application acknowledgement.

Constructed candidate: a consumer trusts a requested mapping size and rereads
a peer-controlled length. Preserve both the actual extent mismatch and the
specific check/use sequence; either issue may be independently prevented by
another check. Report a concrete invalid access, unauthorized state transition
or bounded availability effect, plus the required actor control. Keep contract
inference separate from observed target behavior. Use authorized isolated
experiments only; arithmetic models do not emulate Windows namespaces or IPC.

## Source basis
Reviewed 2026-10-02; workflow synthesis, not a reproduced target finding.

- [CreateMutexW](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createmutexw): create/open result distinction.
- [CreateFileMappingW](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-createfilemappingw): existing-object extent and local views.
- [Sharing files and memory](https://learn.microsoft.com/en-us/windows/win32/memory/sharing-files-and-memory): interprocess coordination.
