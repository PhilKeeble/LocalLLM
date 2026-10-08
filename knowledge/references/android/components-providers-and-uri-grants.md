---
id: reference-android-component-uri-authority
title: Android exported components, content providers, permissions and URI grants
kind: reference
topics: [android, manifest, exported-components, providers, uri-grants, permissions, authorization]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Component and content authority

## Component exposure needs effective configuration and caller policy

Android activities, services, receivers and providers form different entry types.
For providers, exported controls general cross-app availability, subject to
permissions; same-UID access and temporary URI grants have separate rules. [1][2]

Recover installed declaration, enabled state, caller and actual callback.
Exported does not mean every request is authorized, and nonexported is not a
universal no-cross-process-access verdict. Defaults can depend on component and
target/platform contract; this reference adopts no release-default table.

## A URI grant is scoped resource authority rather than a global permission

Provider grants can temporarily permit access despite ordinary provider read,
write or exported restrictions. Provider read and write permissions are distinct.
[2]

Recover grant recipient, exact URI/path scope, operation flags and applicable
lifetime. The ability to grant is different from an effective grant. A URI string
alone does not carry proven authority for every resource it might resolve to.
Persistence, prefix scope and revocation need the actual API contract and state;
they cannot be inferred from the word grant.

## Provider selection must stay bound to the authorized object

For analysis, follow URI authority/path, decoding, backing file/query selection,
handle and returned data. Authorization of one URI does not prove a subsequent
path transformation or reopened file names the same object.

An accepted query may be intentional sharing; establish the caller-to-object
policy and returned effect before reporting disclosure. A grant rejected before
the provider accesses data is not observed disclosure. Distinguish semantic object
selection from parcel/parser bounds checks.

## Sources and scope

Reviewed 2026-10-08. [Application fundamentals](https://developer.android.com/guide/components/fundamentals)
[1], component types; [provider element](https://developer.android.com/guide/topics/manifest/provider-element)
[2], exported, grantUriPermissions and read/write permission descriptions.
No universal component defaults, grant persistence or undocumented URI policy.
Workflow: playbook-android-service-authority.
