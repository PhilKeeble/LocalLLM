---
id: reference-concurrency-mutable-validation-double-fetch
title: TOCTOU, double fetch and mutable validation inputs
kind: reference
topics: [concurrency, toctou, double-fetch, validation, shared-memory]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# TOCTOU, double fetch and mutable validation inputs

## Scope and validation identity
Reviewed 2026-10-02. The general requirement is investigative: identify whether
the object, bytes, authority and state consumed are those actually validated.
TOCTOU (time of check to time of use) concerns a relevant change between validation
and consumption, not simply two separated instructions. A check can remain sufficient
when the relevant state is immutable
or a proven protocol excludes the change. Conversely, a guard dominating a sink
does not establish that a reloaded value or re-resolved name is unchanged.
API examples below are specifically Windows drivers and Linux file resolution.

## Double fetch from mutable shared memory
Constructed example: first load of request.length is 16 and passes capacity=64;
another actor changes it to 4096; a second load supplies 4096 to a copy into the
64-byte destination. Evidence needs two actual fetches, a feasible mutation
interval, use of the changed value and insufficient subsequent validation.
Decompiler reuse of one variable name does not establish one machine load.

Two reads alone are not a vulnerability: the second may be checked again, the
input may be immutable, or both values may remain safe. Check reloads through
aliases, helper calls, DMA/shared mappings and nested pointer fields. Atomic
individual fields avoid tearing only within their applicable guarantees; they
do not make an entire request a consistent multi-field snapshot.

## What a private copy does and does not establish
A private, stable copy can bind validation and consumption if both use the same
copied bytes and no later path returns to the mutable original. Copying a header
containing pointers does not copy the pointed-to payload. Copying several fields
while the producer writes can capture a mixed version; validate that resulting
snapshot completely or establish a coherent snapshot protocol.

Constructed example: copied offset from version A and length from version B
may each be individually plausible but fail their combined range constraint.
For retained nonnegative byte counts in the same representable integer domain,
validate offset <= extent before length <= extent-offset. These conditions do
not establish lifetime or semantic validity. A version counter checked before/after needs correct ordering, change
discipline and wrap/reuse analysis; a counter's mere presence is not proof.
Bounds, semantic relationships and authority binding remain separate checks.
For checked serialized buffers later read through offset accessors, use
reference-parser-offset-based-serialization.

## Windows ProbeForRead is not an immutable snapshot
In Windows kernel drivers, ProbeForRead checks the specified user address range
and alignment, raising exceptions on failures. A zero length performs no address
check. Probing and subsequent user-buffer accesses require the documented
exception handling: another user thread can change mappings/protections even
during or after a successful probe. [1]

Therefore a successful probe does not freeze contents or establish application
validity. Trace actual buffer transfer mode and capture, not just the probe
import. Subsequent reads of a length, pointer or discriminator can disagree
with the values previously checked. Fault handling prevents an unhandled access
exception only if correctly applied; it does not itself enforce semantic bounds.

## Linux path check and subsequent open
Linux access() followed by open() can resolve a pathname after an intervening
change; access() is not an authorization token for a later open. [2] A path
string is a lookup instruction, not a stable object identity. Constructed case:
validation inspects file A, an attacker replaces a writable path component,
and the later operation reaches B.

Investigation requires control over the relevant directory/name/link and a
feasible replacement; a static string match alone is insufficient. Opening
and operating on the retained descriptor can preserve file-object binding,
but does not freeze file contents, permissions, or all application policy.
Directory-relative lookup narrows the starting object; confinement depends
on the actual resolution flags and handling of links, mounts and errors.

## Authorization and object changes
Constructed policy race: session S is authorized for object O under owner A;
before commit, O is reassigned or S is revoked; the operation uses a stale
decision. Whether this violates policy depends on the contract: some operations
intentionally retain an authority granted at open/start, others require current
authorization at commit. State the intended revocation/transaction semantics.

Record which identity, object generation, operation and operands the decision
binds, and the synchronization or version check protecting that binding. Repeating
a check against the old cached identity is not revalidation of a new identity.
Do not label every policy change during a long operation a vulnerability without
establishing the required authorization time and the resulting forbidden effect.

## Primary sources and related evidence
Reviewed 2026-10-02. API facts are scoped to the documentation below; constructed
snapshot and authorization examples express proof obligations, not OS guarantees.

1. [Windows ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread).
2. [Linux access(2), notes](https://man7.org/linux/man-pages/man2/access.2.html).

Related: reference-native-integer-size-buffer-arithmetic for checked ranges;
reference-native-type-confusion-object-validity for mutable discriminators;
playbook-re-sensitive-data-flow for guard-to-consumer value/version tracing.
