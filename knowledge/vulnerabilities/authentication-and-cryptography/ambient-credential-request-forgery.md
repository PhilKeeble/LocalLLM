---
id: vulnerability-authentication-ambient-credential-request-forgery
title: Cross-site request forgery or ambient-credential action without request intent
kind: vulnerability
topics: [authentication, csrf, request-intent, cookies, browser, origin]
platforms: [cross-platform]
architectures: [any]
---

# Cross-site request forgery or ambient-credential action without request intent

## Definition and violated invariant

Cross-site request forgery occurs when an attacker can cause a user agent to send a request carrying the victim's ambient authority and the receiving application treats that authority as proof that the victim intended the sensitive action. Authentication and authorization identify what the credential may do; a protected state change also needs evidence that the request arose through an accepted interaction context.

Cookies are a common ambient credential because a user agent selects applicable cookies for a request without requiring the initiating document to read them. Client certificates and automatically attached platform credentials can create a similar question. A bearer token explicitly added by trusted application code has a different request path and is not automatically vulnerable to browser CSRF.

## Conditions that establish the issue

Recover the initiating origin or site, browser request primitive, final URL and redirects, method and content type, credential attachment rules, cookie attributes, request-intent mechanism, server validation, victim session and sensitive effect. Prove an attacker-controlled context can produce the accepted request with the victim's credential and without possessing an additional value or context that the attacker cannot supply.

Account for same-origin and same-site distinctions, sibling domains, top-level navigation, legacy or embedded clients and endpoints that change state through nominally safe methods. The server-side acceptance path, rather than the visible form or client route, decides reachability.

## Evidence that is not sufficient

A cookie-authenticated endpoint, POST route, missing field named `csrf`, cross-origin page, absent CORS response permission or state-changing handler is not sufficient. Cookie `SameSite` policy, origin or Fetch Metadata checks, an unpredictable session-bound request token, reauthentication, a custom-header contract or another non-ambient proof may prevent acceptance.

A request token is not decisive merely because it exists: establish that it is required on every equivalent sensitive path, bound to the relevant session or transaction as designed, unavailable to the attacker and compared before the effect.

## Investigation sequence

Enumerate every route to the state change and construct an acceptance table with method, media type, authentication source, cookie policy, origin/site metadata, request token or user-confirmation state, redirects and final effect. Trace middleware ordering and failure handling into the handler. Distinguish a request being sent from its response being readable, and distinguish user navigation from proof that the user approved the selected action and object.

In a binary or managed service, follow header and cookie parsing into authentication, then locate request-intent checks and all early dispatch paths. Preserve proxy-added or stripped headers and the trust boundary at which their values become authoritative.

## Hypothetical ambient-cookie example

```text
POST /account/email
Cookie: SID=<victim session>
Content-Type: application/x-www-form-urlencoded

email=attacker@example.test

handler: if session.authenticated: account.email = form["email"]
```

The example is vulnerable only if an attacker-controlled browser context can submit this request, the browser attaches the victim's accepted session credential, and no validated token, origin/site policy, reauthentication or equivalent intent proof blocks the update. The HTTP method alone does not establish intent.

## Primitive and impact limits

The direct primitive is a sensitive application action performed with the victim's ambient authority but attacker-selected request data. Impact is limited to reachable operations and the victim's effective privileges. Read access often requires a separate disclosure channel because causing a cross-site request does not by itself expose its response.

## Related knowledge and primary sources

Browser cookie, origin, request parsing and authentication-state references provide deeper mechanics. This profile keeps credential attachment, attacker request construction and the consuming state change together.

Reviewed 2026-10-09 against [RFC 6265](https://www.rfc-editor.org/rfc/rfc6265.html) for user-agent cookie selection and attachment, the W3C [Fetch Metadata Request Headers](https://www.w3.org/TR/fetch-metadata/) specification for request-context signals, and the OWASP [CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) for the attack and defense evidence model. The example is hypothetical; deployed browser and cookie policy must be recovered rather than assumed.
