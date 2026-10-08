---
id: reference-crypto-update-trust-activation
title: Update trust, metadata roles, rollback state and authenticated activation
kind: reference
topics: [cryptography, updates, signatures, metadata, rollback, freshness, installation, activation]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Update authentication and selected activation

## Update signature trust requires an authorized role and target

The Update Framework (TUF) separates root trust, targets/delegation, snapshot
consistency and timestamp freshness. Target metadata binds lengths/hashes and
which roles may supply target files. These are a scoped update model. [1]

For investigation, recover trusted initial state, authorized signer/role, target
identity and the actual accepted metadata. A valid signature under any parseable
key does not establish authorized publication. A signed archive also does not
authorize every extraction destination or application action. Generic update
acceptance properties remain in reference-logic-update-verification-installation;
custom updaters need their own structures and policy, not TUF field assumptions.

## Rollback resistance and expiry depend on trusted retained state

TUF compares metadata versions with trusted state and applies expiration checks.
Authentic metadata can still be stale or inconsistent with that state. [1]

For investigation, trace the actual monotonic/expiry policy, time source, stored
state, persistence and reset authority. A displayed firmware version is not
necessarily the trusted metadata sequence. An older image can be authorized by
recovery policy; an unknown clock cannot establish current expiry. Keep the
accepted comparison and selected target with the finding rather than assuming
'newest version' is every updater's security invariant.

## Download verification must remain bound to consumed bytes

TUF target metadata specifies file lengths/hashes and constrains delegated target
paths through the trusted role chain. [1]

For investigation, follow actual bytes through staging, member selection,
decompression/delta transformation, validation and installation. A later reopen
at the verified pathname can select different content unless continuity is
established. Conversely, multiple stages are not automatically a defect if the
defined transformation preserves authenticated binding. Keep repaired or derived
outputs distinct from original signed input; shared parser/archive facts remain
in their own references.

## Activation and recovery require more than cryptographic success

For analysis, bind authenticated bytes, selected active component, retained trust
state and failure/restart behavior under the updater's promised consistency model.
Separate staging, install, publication and execution evidence.

A rename or verification return does not certify atomic multi-object activation,
durability or successful startup. Recovery may intentionally select a previous
trusted image under policy; it must be evaluated against that policy rather than
a universal newest-image rule. Report the earliest unsupported state/content
relation. Full installation/firmware architecture contracts remain in
reference-logic-update-verification-installation rather than being duplicated here.

## Source and scope

Reviewed 2026-10-08. Rolling TUF specification sections 2, 4 and 5.4-5.7: roles,
target metadata, trusted versions/expiry and target binding. Only the inspected
concepts are used; no client implementation or release-specific layout assumed.

1. [TUF specification](https://theupdateframework.github.io/specification/latest/): scoped authenticated update model.

Workflow: playbook-crypto-update-evidence. Signature, freshness, target binding,
safe extraction and committed activation need distinct supporting relations.
