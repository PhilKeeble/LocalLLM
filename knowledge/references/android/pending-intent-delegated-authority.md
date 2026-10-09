---
id: reference-android-pending-intent-delegated-authority
title: Android PendingIntent creator authority, mutability and delivered action
kind: reference
topics: [android, pendingintent, delegation, intents, mutability, authorization]
platforms: [android]
architectures: [any]
---

# Android PendingIntent delegated authority

## A PendingIntent delegates the creator's ability to perform a defined operation

Android documents `PendingIntent` as a token another application can use to perform the described action using the creator application's identity. The token's creator and eventual sender are therefore different principals. Possession is a delegated capability for the represented operation, not proof the sender independently holds the creator's permissions.

Recover creator UID/package and code identity, operation family, base Intent, request identity, target component, flags, recipient and lifetime. A serialized-looking Intent or matching request code does not establish the same system-managed token.

## Mutability controls which fields a sender can supply

An immutable PendingIntent prevents the invoker from modifying the wrapped Intent through ordinary fill-in arguments. A mutable token can permit fields to be filled or changed according to its construction and send contract. Mutability is not automatically unsafe: some intended uses require system or recipient-supplied data, but every mutable field must remain within the creator's delegation policy.

Identify which component, action, data URI, categories, extras, clip data and flags are fixed versus fillable, and which final fields the receiver consumes. An explicit component narrows routing but does not authorize every object named in mutable extras.

## Identity and replacement depend on the token's matching rules

PendingIntent retrieval flags can return, update, cancel or avoid creating an existing matching token. Extras are not generally the sole token identity. Recover the documented matching fields and construction flags before concluding that two call sites share authority or that attacker-controlled extras create a fresh token.

Track cancellation, one-shot use and component/package lifecycle. A reference retained by another process can outlive the UI or call site that created it.

## Investigation consequence

Trace untrusted influence into token creation or send, then into the final resolved component and effect. Prove the attacker obtains the token and controls the field needed for an action outside the intended delegation. A `PendingIntent` API reference, mutable flag, notification, or exported component alone is only a review surface.

## Primary sources and scope

Reviewed 2026-10-09 against Android [`PendingIntent` API semantics](https://developer.android.com/reference/android/app/PendingIntent) and Android [unsafe PendingIntent guidance](https://developer.android.com/privacy-and-security/risks/pending-intent). Platform behavior and effective manifest/component configuration must match the target.
