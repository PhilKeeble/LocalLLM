---
id: vulnerability-external-resource-custom-uri-handler-activation
title: Externally invokable custom URI handler and deep-link activation
kind: vulnerability
topics: [uri-schemes, protocol-handlers, deep-links, activation, authorization]
platforms: [windows, macos, ios, android]
architectures: [any]
---

# Externally invokable custom URI handler and deep-link activation

## Definition and violated invariant

A custom URI handler or deep-link vulnerability exists when an external actor can activate an application with controlled URI components and reach an action or object that the actor is not authorized or intended to invoke. The invariant is that handler selection is trustworthy for the application model and every delivered action and operand is parsed, validated and authorized under the receiving application's current identity and state.

Registering a scheme and receiving a URI are normal platform capabilities. The vulnerability requires a reachable sensitive effect, such as state change, protected data access, privileged IPC or transition into a command or file handler.

## Conditions that establish the issue

Establish who can cause activation, which handler the platform selects, the exact URI delivered, every parse and decode stage, the action and object resolved, and the receiving process's authority. Prove that the selected action lacks the user-intent, authentication, authorization or object binding required by the application's contract.

For verified web links, confirm the actual domain association, package or signing identity and matched path scope. Verification can bind a web domain to an application, but it does not automatically authorize every application action encoded in that URL.

## Evidence that is not sufficient

A manifest declaration, registry protocol entry, `OnActivated` callback, intent filter, custom scheme string or invocation from a browser is not sufficient. The platform may select another handler, prompt the user, reject the URI, deliver only a constrained representation, or route the action through application-level authorization.

A unique-looking custom scheme is not proof of exclusive ownership. Apple documents that multiple apps can register the same custom scheme and target selection is undefined; Android custom deep links and verified App Links have different selection contracts. Apply the target platform's mechanism rather than generalizing one model.

## Investigation sequence

Recover registration scope and precedence for the initiating user, package or profile. Identify the selected executable, package and activation entry point for both cold start and an existing instance. Preserve raw URI, scheme, authority, path, query and fragment, then record every percent-decoding, form-decoding, Unicode normalization and application-specific split.

Trace the decoded action through routing, session lookup, object resolution, confirmation and authorization to the final effect. Check whether single-instance redirection, queued activation or retained UI/session state changes the authority available to the link. Treat source-application metadata as diagnostic unless the platform explicitly makes it an authenticated security identity.

## Constructed application example

This hypothetical handler maps a URI action directly to a state-changing operation in the currently signed-in session:

```text
on_uri_activation(uri):
    route = parse_application_uri(uri)
    if route.action == "delete-document":
        delete_document(current_session.user, route.query["id"])
```

The path is vulnerable only if an external actor can invoke the handler, control `id`, bypass a required intent or authorization decision, and cause deletion of an object outside the actor's permitted scope. If deletion always checks the current user's permission for the resolved document and the product intentionally allows link-triggered deletion, external activation alone is not a defect.

## Platform-specific evidence

On Windows, distinguish packaged manifest activation from unpackaged protocol registration and recover the activation arguments delivered to the selected app. On Android, recover exported activity state, intent-filter matching, resolved component, extras and verified App Link association. On Apple platforms, distinguish custom schemes from universal links and recover the delegate or scene delivery path.

These are routing contracts, not interchangeable authorization systems. In every case, confirm the installed configuration and actual selected handler; static declarations do not prove runtime precedence or user choice.

## Primitive and impact limits

The direct primitive is externally triggered application behavior with controlled parameters. Report the specific action and application authority. Navigation to a public screen is not equivalent to data access; a state-changing action under the current user's session is not automatically operating-system privilege escalation.

Code execution requires an additional transition into a command, interpreter, loader or memory-corruption issue. File access requires final namespace and permission evidence. Keep those downstream chains separate and link them only when their prerequisites are demonstrated.

## Related knowledge and primary sources

`reference-activation-uri-handler-selection-delivery` owns platform routing and delivery distinctions, while `reference-parser-escaping-nul-url-layers` owns decoding-layer disagreements. The action/object authorization rule is repeated here so the profile does not depend on those links.

Reviewed 2026-10-09 against [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html), Microsoft [URI activation](https://learn.microsoft.com/en-us/windows/apps/develop/launch/handle-uri-activation), Android [deep links and App Links](https://developer.android.com/training/app-links), and Apple [custom URL scheme](https://developer.apple.com/documentation/Xcode/defining-a-custom-url-scheme-for-your-app) and [universal-link](https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content) documentation. The pseudocode is constructed.
