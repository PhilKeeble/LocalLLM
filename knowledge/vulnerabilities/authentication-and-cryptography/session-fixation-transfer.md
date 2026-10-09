---
id: vulnerability-authentication-session-fixation-transfer
title: Session fixation, predictable session identity, or unsafe session transfer
kind: vulnerability
topics: [authentication, sessions, fixation, cookies, session-secrets, identity]
platforms: [cross-platform]
architectures: [any]
---

# Session fixation, predictable session identity, or unsafe session transfer

## Definition and violated invariant

Session fixation occurs when an attacker can choose, know or preserve the session secret that becomes bound to a victim's successful authentication, allowing the attacker to use the same authenticated session. More broadly, session identity is unsafe when it is predictable, transferred across principals or trust contexts, retained beyond policy, or upgraded to an assurance level not established by its authentication event.

A session identifier used as a bearer secret authenticates possession of that secret. Changing a display username or server-side flag does not rotate the bearer capability. Session continuation, remember-device state, refresh tokens and proof-of-possession sessions have different contracts and must be traced separately.

## Conditions that establish the issue

Recover session-secret generation and entropy, pre-authentication session creation, cookie/header/storage transport, attacker ability to set or learn the value, authentication transition, rotation and invalidation, mapping to principal and assurance, concurrent use, logout/expiry, cross-domain/device transfer and final protected operation. Prove an attacker-known or attacker-selected session remains accepted after victim authentication or is rebound to another principal/context.

For adoption of a caller-supplied session ID, establish that the server accepts that value rather than replacing it. For predictability, show feasible inference within the lifetime and request limits.

## Evidence that is not sufficient

A session cookie, unchanged-looking value, URL parameter, pre-authentication session, low-entropy-looking sample, persistent login or concurrent session is not sufficient. The server may store separate secret material, rotate internally, bind proof of possession, reject attacker-supplied IDs or intentionally permit concurrent sessions.

A stolen post-authentication session is session theft; fixation specifically requires attacker knowledge or control before the victim's authentication binds authority to it.

## Investigation sequence

Build a session lifecycle table containing pre-auth value, creation actor/time, authentication event, post-auth value, server-side record generation, principal/assurance, transfer channel, expiry, logout and invalidation. Follow redirects, federation handoffs, privilege elevation, account switching and recovery flows. Confirm reuse from the attacker's context reaches a protected action.

At binary level, trace random generation, lookup keys, record mutation versus replacement and response headers around authentication. Distinguish pointer/object reuse from externally stable secret bytes.

## Constructed fixation example

```text
session_id = request.cookie["SID"] ?? generate_session_id()
if verify_password(request.user, request.password):
    sessions[session_id].principal = request.user
    response.cookie["SID"] = session_id
```

If the server accepts an attacker-chosen pre-authentication `SID`, the attacker can induce a victim to use it and later present the same value after the victim authenticates. The finding requires actual adoption, victim use, no secret rotation or additional binding, and successful attacker reuse. A server-generated replacement after authentication changes the conclusion.

## Primitive and impact limits

The direct primitive is reuse of authenticated session authority through an attacker-known, predictable or wrongly transferred session secret. Consequences are impersonation within that session's account and assurance. Cookie scope, channel protection, additional proof of possession, reauthentication, later authorization and session lifetime bound impact.

## Related knowledge and primary sources

Randomness, authentication-state, token-binding and browser-cookie references provide underlying contracts. This profile keeps pre-auth attacker knowledge and post-auth authority binding explicit.

Reviewed 2026-10-09 against NIST [SP 800-63B section 5](https://pages.nist.gov/800-63-4/sp800-63b/session/) for session binding and secret lifecycle, and [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265.html) for HTTP cookie storage and transport semantics. The example is constructed; not every session uses cookies or bearer secrets.
