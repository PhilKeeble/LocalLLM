---
id: vulnerability-authorization-user-interface-intent-mismatch
title: User-interface trust or user-intent mismatch authorizes a different sensitive action
kind: vulnerability
topics: [authorization, user-intent, ui-redressing, clickjacking, overlays, framing]
platforms: [cross-platform]
architectures: [any]
---

# User-interface trust or user-intent mismatch authorizes a different sensitive action

## Definition and violated invariant

A user-interface intent vulnerability occurs when an attacker-controlled presentation causes a user gesture to authorize a different security-sensitive actor, object or operation from the one the trusted interface represents. Framing, overlays, obscured or displaced controls, misleading identity indicators and display-to-action disagreement are mechanisms; the defect requires a protected action whose authorization relies on the misdirected gesture.

A physical click or touch proves input at coordinates and time under the platform's routing rules. It does not inherently prove that the user saw and approved the identity, object and consequence consumed by the application.

## Conditions that establish the issue

Recover the attacker's control of framing, windows, overlays, focus, accessibility or rendered content; trusted surface and displayed identity/object/action; input coordinates and routing; occlusion or displacement state; activation and confirmation policy; authenticated user/session; actual sensitive operation and effective authority. Prove the gesture reaches the protected control while the user is presented with materially different intent.

Account for dynamic layout, scaling, animation, multiple windows, navigation and accessibility transformations. State which platform or browser protections apply to the actual surface and configuration.

## Evidence that is not sufficient

A frameable page, overlay permission, transparent window, misleading text, sensitive button, obscured-touch flag, screenshot or click event is not sufficient. The protected surface may reject embedding or obscured input, require reauthentication or display a trusted confirmation that binds the final action and object.

Attacker-controlled presentation without a resulting sensitive operation establishes social-engineering surface, not this authorization primitive.

## Investigation sequence

Construct a timeline of visible layers, focus and input routing from attacker presentation to trusted control. Record the identity, object and action displayed immediately before confirmation and compare them with the values consumed at commit. Trace frame-ancestor, window, overlay and obscured-input policy, then follow the gesture through callbacks and asynchronous state changes to the final effect.

At binary or managed-code level, follow touch/click event flags, window ownership, confirmation-state objects and operation parameters. A label string and committed object must be joined by data flow rather than screen proximity.

## Hypothetical UI-redressing flow

```text
attacker-controlled surface displays: "Play video"
user gesture is routed to an obscured trusted control: "Approve transfer to account X"
trusted application commits transfer under the user's authenticated session
```

The flow is vulnerable only if the attacker can construct the presentation and routing, the trusted control accepts the gesture, and the transfer occurs without a trusted confirmation that accurately binds account X and the operation. The mere ability to draw over another window is not enough.

## Primitive and impact limits

The direct primitive is a user-authorized application action with mismatched represented intent. Impact is bounded by the action and the user's effective authority. Credential theft, code execution or privilege elevation requires the action to expose or grant those separate capabilities.

## Related knowledge and primary sources

Browser framing, platform input/overlay, authentication and authorization references provide mechanism-specific rules. This profile keeps presentation, routed gesture and committed operation in one chain.

Reviewed 2026-10-09 against W3C [Content Security Policy `frame-ancestors`](https://www.w3.org/TR/CSP3/#directive-frame-ancestors) for restricting hostile framing and Android [tapjacking guidance](https://developer.android.com/privacy-and-security/risks/tapjacking) plus the [`View` security contract](https://developer.android.com/reference/android/view/View#security) for obscured-touch handling. The example is hypothetical; browser and OS protections differ by surface and configuration.
