---
id: reference-linux-desktop-uri-handler-activation
title: Linux desktop URI association, desktop-entry execution and D-Bus activation
kind: reference
topics: [linux, uri-handler, x-scheme-handler, desktop-entry, dbus, activation]
platforms: [linux]
architectures: [any]
---

# Linux desktop URI-handler activation

## x-scheme-handler associations select applications through MIME policy

Freedesktop MIME application associations use pseudo-MIME types such as `x-scheme-handler/<scheme>` to associate URI schemes with desktop applications. Effective selection can combine desktop-specific and generic configuration at user and system locations, including defaults, additions and removals. A desktop file installed on disk is a candidate declaration, not proof it is the selected handler in the initiating user's environment.

Recover the raw scheme, invoking user/session/desktop, applicable configuration files in precedence order, declared handlers, removals, current default and final desktop file. Do not assume installation order alone determines selection.

## Desktop-entry Exec field codes define argument substitution

For an application desktop entry, the `Exec` key defines an executable and arguments with desktop-entry quoting and field-code expansion. `%u` represents one URL and `%U` a list of URLs; other file/URL field codes have distinct roles. Field codes must be treated under the specification rather than as shell variables, and deprecated codes do not supply a portable contract.

Trace the selected desktop entry through its parsed `Exec` tokens and field substitutions to the actual process-creation interface. Then trace the delivered URI through the application parser. A `%u` placeholder preserves one field-code role but does not validate the URI, authorize its action, or prove every implementation avoids another downstream command interpreter.

## D-Bus activation is a different delivery path

When a desktop entry declares D-Bus activation, the desktop environment can invoke application methods through the session bus instead of launching the `Exec` command for ordinary activation. Recover the well-known bus name, current/activated owner, object/interface/method, sender identity and delivered URI list. The desktop file's application identity does not replace method-level authorization.

Fallback behavior can depend on implementation and declaration validity. Do not infer that an `Exec` line necessarily ran when D-Bus activation was selected, or that a D-Bus service name permanently identifies one process generation.

## Sensitive effects remain application authorization decisions

Handler association answers which application receives the URI. The recipient must still parse under one decoding/canonicalization contract and authorize the requested account, file, command, import or other object for the active user/session. A familiar scheme name, signed package or user default does not authenticate the invoking process or grant the payload authority.

For a hijacking claim, prove attacker influence over the effective association and actual selection. For an injection claim, prove a URI component crosses an argument or interpreter boundary after delivery.

## Primary sources and scope

Reviewed 2026-10-09 against freedesktop.org [MIME Applications Associations specification](https://specifications.freedesktop.org/mime-apps-spec/latest/), [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/exec-variables.html), and [D-Bus activation specification](https://dbus.freedesktop.org/doc/dbus-specification.html#message-bus-starting-services). Desktop environment and launcher implementations can add scoped behavior; match the target configuration.
