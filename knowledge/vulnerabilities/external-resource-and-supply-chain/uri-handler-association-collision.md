---
id: vulnerability-external-uri-handler-association-collision
title: URI handler association collision or hijacking
kind: vulnerability
topics: [uri-handler, custom-scheme, deep-link, association, activation, hijacking]
platforms: [cross-platform, windows, linux, macos, ios, android]
architectures: [any]
---

# URI handler association collision or hijacking

## Definition and violated invariant

This vulnerability occurs when a URI scheme or link association expected to reach one trusted application can instead be registered, selected, or claimed by another actor, causing payloads, credentials, authorization codes, files, or user actions to reach an unintended handler. The invariant is that routing identity and sensitive action authorization must not depend solely on a familiar scheme string or assumed recipient.

Custom schemes usually identify a protocol name, not a globally authenticated application. Verified web-link mechanisms can bind a domain and application under platform-specific rules, but the receiving application must still validate and authorize the delivered action.

## Conditions that establish the issue

Identify registration scope and precedence, competing handlers, installation order, user choice/default state, verified app/domain ownership where applicable, invoking mechanism, selected recipient, exact delivered URI, parsing/decoding, and sensitive consumer. Prove an attacker can become the recipient or redirect the invocation and obtain or cause a security-relevant effect.

For callback flows, bind nonce/state, redirect target, application instance and authenticated session. A correctly routed link can still contain an unauthorized object or action.

## Evidence that is not sufficient

A custom scheme, registry/plist/manifest entry, competing application, familiar brand name, or launch event is not sufficient. Platform verification, explicit application targeting, user choice, existing default precedence, or application-level state binding may prevent the claimed interception or effect.

Do not treat caller/source-application fields as universal authenticated identity. Determine the platform guarantee and independently authorize sensitive operations.

## Investigation sequence

Recover all registrations and effective resolution rules in the target user/system/package context. Trigger or trace the actual invocation mechanism and identify the selected handler rather than assuming first-install or last-install behavior. Follow the URI through each decoding layer into authentication, object lookup, command arguments, filesystem access, or application action.

Preserve scheme, authority, path, query and fragment boundaries. Association proof answers who receives a link; it does not validate the link's data or confer permission for the requested effect.

## Primary sources and scope

Reviewed 2026-10-09 against IANA [URI scheme registration procedures](https://www.rfc-editor.org/rfc/rfc7595), Microsoft [reserved and application URI schemes](https://learn.microsoft.com/en-us/windows/apps/develop/launch/reserved-uri-scheme-names), Android [App Links verification](https://developer.android.com/training/app-links/verify-android-applinks), Apple [supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains), and freedesktop.org [MIME application associations](https://specifications.freedesktop.org/mime-apps-spec/latest/). Selection and verification behavior is platform-specific.
