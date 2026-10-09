---
id: reference-activation-uri-handler-selection-delivery
title: Custom URI scheme registration, handler selection and activation delivery
kind: reference
topics: [uri-schemes, protocol-handlers, deep-links, app-links, activation]
platforms: [windows, macos, ios, android]
architectures: [any]
---

# Custom URI scheme registration, handler selection and activation delivery

## Registration selects a handler, not trusted input

A custom URI scheme lets the operating environment select and activate an application for a URI. Registration establishes routing capability; it does not authenticate the URI's producer, validate its parameters or authorize the requested application action. Treat every externally invokable activation as an input boundary unless a separate platform contract proves a stronger origin guarantee.

Recover the scheme registration visible to the initiating context, the selected handler and its executable or package identity, and the data delivered to the application. A declaration or registry entry alone does not prove the handler is selected or invoked on the target system.

## URI structure and scheme-specific parsing

RFC 3986 defines `scheme`, optional `authority`, `path`, `query` and `fragment`, while each scheme defines additional semantics. Some custom schemes treat everything after the colon as opaque; others use hierarchical forms. Parse under the handler's actual contract before decoding component data, because decoding a reserved character early can change component boundaries.

Record the raw URI, every decoding or normalization stage, extracted action and operands, and the final object or operation. The same spelling can be interpreted differently by a browser, OS activation layer, framework URI class and application parser. A malformed or surprising URI is only a candidate until it reaches a sensitive effect.

## Platform handler identity differs

Windows packaged applications can declare protocol activation and receive a URI through activation arguments; unpackaged applications can register a protocol through the applicable app-lifecycle mechanism. Android intent filters can route custom schemes to matching activities, while verified App Links add a domain-to-application association for declared HTTPS links. Apple custom URL schemes can be claimed by multiple apps, with target selection unspecified, whereas universal links bind web domains through associated-site configuration.

These mechanisms are not interchangeable identity guarantees. Establish package signing, user choice, manifest or entitlement scope, per-user versus machine registration, domain verification and current default selection under the investigated platform. A unique-looking scheme name does not make a custom scheme exclusive.

## Delivery and application authority

Activation can start a new process or deliver another event to an existing instance. Recover both cold-start and already-running paths, including single-instance redirection, queued events and retained session state. The receiving process's existing authentication state can make an otherwise simple navigation link security-sensitive.

Source-application identifiers and referrer-like metadata can aid investigation but are not universal authorization tokens. Bind any sensitive action to the user, session and selected object under an explicit platform/application contract. Determine whether activation merely displays content or performs deletion, payment, file access, command execution or privileged IPC.

## Transition to commands and files

If a handler constructs a command line, interpreter program or shell operation, preserve executable selection and argument boundaries through the final process-creation API. Quoting a whole URI is not equivalent to encoding one argument for every downstream parser. If the URI selects a file, recover the decoded path, namespace, link traversal, final object identity, access mode and application chosen to open it.

Protocol activation, command injection and unsafe file handling are distinct steps. Establish each transition rather than treating registration as code execution. On Windows, `ShellExecute` can dispatch through registered verbs and shell extensions; determine the verb and selected handler rather than assuming direct `CreateProcess` behavior.

## Primary sources and scope

Reviewed 2026-10-09 against [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html), Microsoft [URI activation](https://learn.microsoft.com/en-us/windows/apps/develop/launch/handle-uri-activation) and [`ShellExecuteW`](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew) documentation, Android [deep-link](https://developer.android.com/training/app-links) and [App Link](https://developer.android.com/training/app-links/about) documentation, and Apple [custom URL scheme](https://developer.apple.com/documentation/Xcode/defining-a-custom-url-scheme-for-your-app) and [universal-link](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content) documentation. Exact handler precedence and delivery behavior remain platform, app model and configuration specific.
