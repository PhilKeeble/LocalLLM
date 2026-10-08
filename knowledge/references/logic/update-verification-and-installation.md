---
id: reference-logic-update-verification-installation
title: Update authenticity, target binding, rollback and installation state
kind: reference
topics: [updates, signatures, rollback, manifests, logic-bugs, installation]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Update authenticity, target binding, rollback and installation state

## Scope and separate acceptance properties
Reviewed 2026-10-02. TUF and SUIT-related RFCs below describe particular update
models, not mandatory implementation details of every updater. Separate these
properties in a reverse-engineered acceptance path:

| Property | Question answered |
| --- | --- |
| Authenticity | Did a trusted authorized signer approve the authenticated bytes? |
| Target binding | Is this component/package for this product/device/context? |
| Freshness policy | Is this metadata/image acceptable relative to trusted state? |
| Content binding | Are the bytes consumed those that were authenticated? |
| Installation consistency | Does failure leave an allowed executable state? |

A successful cryptographic verification call is evidence for its actual inputs
and trust configuration, not proof of all these properties.

## Signature input and trust decision
Constructed failure: updater verifies signed metadata containing digest H, but
installs a file selected by an unauthenticated filename without checking its
content against H. Another variant ignores verification failure or treats any
locally parseable certificate as an authorized publisher.

Recover signed byte range/encoding, selected key, trust anchor, signer role,
algorithm parameters, result convention and every accepted failure path. Then
trace authenticated fields to consumed package bytes and security-relevant
operands. Certificate parsing, a signature directory, a hash import or an HTTPS
download alone does not prove update authorization. Record unresolved trust-store
or verifier behavior instead of assuming it from a function name.

## TUF metadata roles and binding
TUF specification v1.0.36 separates trusted root/key policy, timestamp freshness,
snapshot metadata consistency and targets/delegations. A client verifies the
required role thresholds; repeated signatures from one key ID do not count as
distinct keys. It checks metadata versions/expiry and validates downloaded target
hashes against trusted target metadata, with bounded downloads. [1]

Root rotation uses the previous trusted root's threshold and the new root's own
threshold, advancing root versions one step at a time. Snapshot/targets linkage
prevents accepting arbitrary combinations of independently valid metadata. [1]
These are scoped TUF facts; a custom updater can implement equivalent goals by
different structures. A signature on one component does not authenticate every
other component merely because they arrived in the same archive or connection.

## Rollback, freeze and trusted state
TUF's rollback checks compare metadata with retained trusted versions; expiration
checks address stale metadata/freeze attacks. Valid signatures alone do not make
old metadata current. [1] Investigation inference: recover where trusted versions
and time come from, who can reset them, persistence order and recovery behavior.
Deleting an ordinary cache is different from legitimately resetting trust state.

SUIT's RFC 9124 distinguishes manifest sequence number from firmware version:
an authorized new manifest can intentionally install older firmware. Its sequence
number is monotonic without rollover; a timestamp used as that sequence is a
number, not necessarily a wall-clock expiry. [2] Therefore older image version
does not alone prove unauthorized rollback. State the authority's actual policy
and compare the correct field under the correct signedness/width.

## Product identity and version compatibility
RFC 9124 requires firmware compatibility with intended vendor/device type and
relevant hardware/software revisions. [2] Constructed updater case: two products
trust the same signing key, but package selection checks only signature and not
product ID. A correctly signed package for product B may be invalid for A.

Trace target identifiers, component IDs, architecture, dependencies, destination
and version predicates from authenticated metadata to the installer. A display
name shown in a confirmation dialog is not necessarily the value used for this
decision. Version comparison may be numeric, tuple-based or policy-specific;
lexical string order is not a universal semantic-version rule.

## Verification-to-use continuity
RFC 9124 explicitly identifies changing a manifest after authentication as a
TOCTOU threat. [2] Constructed example: verifier hashes staged file A by path,
then installer reopens that path after another actor replaces it with B.
Evidence requires actual mutability and changed consumption; two opens alone
are insufficient if protected storage or object binding excludes replacement.

Binding must survive decompression, archive extraction, delta application and
selection of install scripts or configuration. Identify which representation is
authenticated and which transformation contract binds the resulting output.
Do not infer that signature coverage of an archive makes unsafe extraction paths
safe, or that a verified payload authenticates unsigned destination instructions.

## Atomic activation and failure recovery
RFC 9019 separates obtaining/installing an image from invoking it and requires
resilience to interruption during update. Invocation includes its own trust
boundary and may involve a bootloader or an OS-level application transition. [3]

Constructed investigation model: staged bytes, authenticated metadata, active
component selection, persistent version state and recovery marker must agree
under the intended policy. Recover failure and restart transitions on both sides
of each publication boundary, distinguishing supported paths from unknown recovery.
An atomic rename of one path does not prove a multi-file package or version
database changed atomically; storage durability is distinct from visibility.
Recovery may legitimately select a previous authenticated image, but must not
silently bypass the policy that governs recovery/rollback. Preserve that policy
instead of assuming every recovery path must always pick the newest image.

## Primary sources
Reviewed 2026-10-02. This is an investigation reference, not a complete TUF or
SUIT implementation specification. Constructed examples are not claimed CVEs.

1. [TUF specification v1.0.36, client workflow §§5.3–5.7](https://theupdateframework.github.io/specification/v1.0.36/).
2. [RFC 9124 (2022), manifest model and security requirements](https://www.rfc-editor.org/rfc/rfc9124.html).
3. [RFC 9019 (2021), firmware architecture §§3–4](https://www.rfc-editor.org/rfc/rfc9019.html).
