---
id: reference-logic-authorization-object-binding
title: Authentication, authorization, deputies and object binding
kind: reference
topics: [authorization, identity, logic-bugs, confused-deputy, object-ownership]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Authentication, authorization, deputies and object binding

## Scope and policy evidence
Reviewed 2026-10-02. These are platform-independent security distinctions and
constructed investigation examples, not a replacement for an OS access-check
contract. MITRE CWE descriptions classify weaknesses; they do not prove one
exists in a particular binary. Establish the intended policy from an interface
contract, product design, documented isolation promise or other explicit evidence.
A surprising operation is not necessarily unauthorized. Record policy uncertainty
separately from code behavior and external reachability.

## Authentication is not operation authorization
Authentication establishes an identity under a particular mechanism; authorization
decides whether a subject may perform an operation on a resource. A correct
login does not by itself authorize every object or action. Roles alone can miss
restrictions between two users with the same role. These distinctions underlie
CWE-863 and CWE-639. [1][2]

Constructed binary-service case: a dispatcher checks logged_in, then indexes a
global document table using caller-supplied document_id and returns contents.
The missing proof is not another login: it is permission for that subject to
read that particular document. Follow both successful lookup and permission
decision to the same final object; a not-found check is not an ownership check.
For accepted anonymous binding, incomplete factors and requested proxy identities,
use reference-parser-protocol-authentication-state; a protocol status named success
does not always establish the claimed authenticated principal.

## Dimensions of an authorization decision
Use this analytical tuple when tracing a decision; it is not a universal API layout.

| Dimension | Evidence needed at the sensitive operation |
| --- | --- |
| Subject | Authenticated principal and effective execution identity |
| Operation | Read, write, delete, execute, delegate, configure, etc. |
| Object | Resolved object, namespace and live generation |
| Operands | Path, offset, recipient, destination and requested rights |
| Context | Session, tenant, channel and delegation constraints |
| Time/state | Required policy version, revocation and operation phase |

A decision about one tuple does not automatically authorize a changed tuple.
Constructed example: checking read permission on source A does not establish
write permission on destination B for a privileged copy operation.

## Confused deputies and authority provenance
A confused deputy uses its available authority on behalf of a requester without
correctly binding that authority to the request. Hardy's original compiler
example separates the caller-designated output from the compiler's own file
privileges. CWE-441 covers a related intermediary that loses origin context
when forwarding a request. [3][4]

Constructed service case: unprivileged caller selects a destination pathname;
privileged helper opens it under service authority. A privileged helper is not
inherently defective: it may intentionally implement a narrowly authorized
operation. Establish which operands the caller controls, the authority actually
used, the permitted delegation and the forbidden effect. A service-account
access check can succeed while failing to enforce the caller's allowed scope.

## Ownership, tenants and caller-controlled identifiers
A caller-controlled record key can select another user's data unless access is
bound to the authenticated subject; guessing difficulty is not the same property
as authorization. [2] Constructed example: IDs are unique only within a tenant,
but the validator uses (tenant A, id=7) and a later global lookup uses id=7 alone.
The latter may resolve a different object despite an unchanged numeric ID.

Recover where tenant/session context comes from: verified channel context,
server-side state or untrusted request bytes. Client UI filtering is not proof
that a service entry enforces the same restriction. An intentionally unforgeable
capability can itself convey authority under its contract; do not falsely require
an owner-ID comparison in every capability-based interface.

## Validated representation versus consumed representation
Authorization over one spelling or parse can disagree with subsequent resolution.
CWE-551 specifically describes URL authorization before complete parsing and
canonicalization. [5] General investigative extension: map raw bytes, decoded
fields, normalized names and resolved objects; determine which form each check
and consumer uses. Do not assume every normalization is appropriate on every OS.

Constructed example: validator treats a field as eight counted bytes, but an
operation uses its prefix before an embedded NUL as a C string. Establish an
actual forbidden object/effect; representation disagreement alone is a candidate.
Canonicalizing a path once does not freeze later filesystem lookup. See
reference-concurrency-mutable-validation-double-fetch for changing objects.
For duplicate fields, decoding order and parser-specific disagreements, use
reference-parser-duplicate-fields-decoded-values and
playbook-re-parser-differentials.

## Stale decisions, revocation and recycled identifiers
A cached grant has a subject, object, operation and validity interval even if
the implementation stores only allowed=true. Constructed case: pooled session
slot is reassigned to B but retains A's allowed flag; B inherits A's decision.
Likewise an object ID can be recycled while a delayed operation retains the old
authorization result. Numeric equality does not establish the same principal
or object generation.

Whether revocation must invalidate an already opened object is policy/API-specific;
some grants intentionally persist. Recover cache key, invalidation, generation
binding and decision time before claiming a bypass. A fresh policy check on the
old cached subject is not authorization of the new subject. Related lifecycle
facts: reference-concurrency-refcounts-reuse and
reference-concurrency-cancellation-completion-shutdown.

## Primary sources
Reviewed 2026-10-02; CWE 4.20 pages. OS-specific simplifications in classification
pages are not used as access-check specifications here.

1. [CWE-863, incorrect authorization](https://cwe.mitre.org/data/definitions/863.html).
2. [CWE-639, caller-controlled object keys](https://cwe.mitre.org/data/definitions/639.html).
3. [Norm Hardy, The Confused Deputy (1988), university-hosted copy](https://www.cs.umd.edu/~jkatz/security/downloads/capabilities.html).
4. [CWE-441, unintended intermediary](https://cwe.mitre.org/data/definitions/441.html).
5. [CWE-551, parsing before URL authorization](https://cwe.mitre.org/data/definitions/551.html).
