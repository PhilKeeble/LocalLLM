---
id: vulnerability-authentication-token-validation-claim-binding-gap
title: Token signature, issuer, audience, subject, time, or algorithm validation gap
kind: vulnerability
topics: [authentication, tokens, jwt, signatures, claims, issuer, audience]
platforms: [cross-platform]
architectures: [any]
---

# Token signature, issuer, audience, subject, time, or algorithm validation gap

## Definition and violated invariant

A token-validation vulnerability occurs when a relying component accepts a token without all cryptographic and claim checks required to bind it to the trusted issuer, intended recipient, subject, token type, time window and operation. Parsing or decoding a token is not validation, and a valid signature authenticates only the signed representation under the selected key and algorithm; it does not supply missing application claim policy.

JWT is one token format, not a universal token contract. For JWT, registered claims such as `iss`, `sub`, `aud`, `exp`, `nbf`, `iat` and `jti` have defined representations, while their required presence and application meaning come from the using protocol and deployment. Different JWT kinds need mutually exclusive validation rules when substitution is possible.

## Conditions that establish the issue

Recover exact token bytes and type, compact/JSON or other serialization, protected versus unprotected fields, algorithm allowlist, key source and issuer binding, cryptographic result, issuer, subject, audience, type/purpose, expiration/not-before and clock/leeway policy, nonce or token identifier where required, revocation/state, duplicate parsing and final identity/authorization use. Prove a token failing a required check reaches authenticated state or a sensitive operation.

Bind claim comparisons to the correct type and exact consumer. Audience validation must identify this relying party when required; subject identity must be interpreted with its issuer and token purpose.

## Evidence that is not sufficient

A JWT-like string, decoded claims, signature field, successful library call, expired-looking timestamp, missing claim, unfamiliar algorithm or token from another issuer is not sufficient. The using protocol may make a claim optional, another layer may validate it, the token may be encrypted rather than signed, or the suspected path may never establish identity.

Conversely, signature success alone does not prove issuer, audience, subject, time or purpose acceptance is correct.

## Investigation sequence

Trace token receipt through format selection, base/JSON decoding, header processing, key lookup, signature/MAC/decryption, claim parsing, policy checks, identity construction and authorization. Record which fields are cryptographically protected and which configuration supplies expected values. Follow every validation error, retry and fallback.

At binary or managed-code level, recover library overloads/options, return and exception paths, expected issuer/audience constants or configuration, time source and resulting principal claims. Confirm the protected operation uses that principal.

## Constructed incomplete JWT validation

```text
claims = verify_signature_and_decode(token, configured_key)
if claims.exp > current_time:
    authenticate_as(claims.sub)
```

This path checks a signature and expiration but does not show issuer, audience or token-purpose validation. It is vulnerable only when policy requires those checks and a token valid under the configured key for another issuer, recipient or purpose can reach this consumer. The absence of a check from this snippet is not proof that a wrapper or preceding gateway omitted it.

## Primitive and impact limits

The direct primitive is acceptance of a cryptographically invalid token or a valid token outside its intended issuer, recipient, subject, time or purpose context. Consequences include impersonation, cross-service token substitution and access under the resulting principal. Token scope, later authorization, key authority and reachable consumers bound impact.

## Related knowledge and primary sources

Signature/object binding, authenticated freshness, certificate identity and protocol authentication references provide the underlying contracts. This profile keeps cryptographic success and application claim policy distinct.

Reviewed 2026-10-09 against [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519.html) for JWT claims, [RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html) for JWS validation, and [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html) for algorithm, issuer, subject, audience and cross-token validation guidance. The example is constructed; the using protocol determines required claims.
