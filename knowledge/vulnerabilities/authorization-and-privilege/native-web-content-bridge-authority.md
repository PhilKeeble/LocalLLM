---
id: vulnerability-authorization-native-web-content-bridge-authority
title: Native and web-content bridge exposes application authority without origin and operation binding
kind: vulnerability
topics: [authorization, webview, javascript-bridge, web-messaging, origins, native-capabilities]
platforms: [windows, macos, ios, android, cross-platform]
architectures: [any]
---

# Native and web-content bridge exposes application authority without origin and operation binding

## Definition and violated invariant

A native/web bridge vulnerability occurs when web content can invoke an application capability through a JavaScript interface, host object, message handler, navigation callback or extension channel without policy binding the invoking frame and origin, channel generation, requested action and resolved object. Web sandbox restrictions do not constrain authority that the native host deliberately exposes through the bridge.

Origin, top-level document, frame, navigation generation and application user are different identities. A trusted main page does not automatically make every subframe or later navigation trusted.

## Conditions that establish the issue

Recover the native host's effective authority, every loaded top-level and child-frame origin, navigation and redirect policy, bridge installation/removal timing, API visibility by frame, sender/source metadata and its trustworthiness, message framing and parsing, attacker control of content or navigation, requested operation and object, native authorization and final effect. Prove an untrusted content principal can invoke a capability outside its intended policy.

Include local files, data/content schemes, injected content, compromised trusted origins, popups and messages retained across navigation. If the bridge API cannot identify the calling frame, that limitation must be reflected in what content is allowed to coexist with the bridge.

## Evidence that is not sufficient

A WebView, JavaScript enabled, host object, message event, wildcard-looking origin, navigation handler, external link or sensitive native method is not sufficient. The bridge may be absent on untrusted pages, exposed only to restricted origins/frames, carry an unforgeable channel capability or enforce action/object authorization natively.

Checking the currently displayed top-level URL is not necessarily proof of the calling frame's origin. Determine the exact platform API's sender semantics.

## Investigation sequence

Map every document and frame that can exist while each bridge is available. Trace navigation, redirect and document-created callbacks into bridge lifetime. For each native entry method, record sender evidence, decoded message, operation/object selection, user/session state and effective native authority. Follow asynchronous replies and retained ports across navigation generations.

At binary or managed-code level, enumerate projected methods, script-message names and dispatch switches. Trace origin comparisons through URL parsing and normalization, and confirm that the compared source belongs to the message being authorized.

## Hypothetical bridge example

```text
on_web_message(message):
    if message.action == "write_file":
        native_write(message.path, message.contents)
```

The path is vulnerable only if an untrusted frame or navigated document can reach the handler, choose a forbidden path and obtain a native-host write without origin/channel and object authorization. A bridge confined to an application-owned document with a strict native object policy can make the same message shape safe.

## Primitive and impact limits

The direct primitive is invocation of a native application capability by an unauthorized web-content principal. Impact is bounded by exposed methods, object constraints and host process authority. Native code execution requires the method itself to execute code or a separate injection, loading or memory-safety primitive.

## Related knowledge and primary sources

Origin, URI activation, message parsing, authorization and platform WebView references provide deeper contracts. This profile keeps frame identity, bridge lifetime and native effect together.

Reviewed 2026-10-09 against Android's [WebView native bridge guidance](https://developer.android.com/privacy-and-security/risks/insecure-webview-native-bridges) for all-frame exposure and origin limitations of `addJavascriptInterface`, and Microsoft [WebView2 security guidance](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/security) for origin, navigation, host-object and message validation. The example is hypothetical; bridge semantics vary by platform.
