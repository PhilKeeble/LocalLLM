---
id: vulnerability-authentication-key-algorithm-verifier-confusion
title: Key, algorithm, or verifier-selection confusion
kind: vulnerability
topics: [authentication, cryptography, keys, algorithms, jwt, signatures, key-selection]
platforms: [cross-platform]
architectures: [any]
---

# Key, algorithm, or verifier-selection confusion

## Definition and violated invariant

Key or algorithm confusion occurs when attacker-controlled metadata selects a cryptographic algorithm, key, key source, key identifier, certificate, verifier mode or token-validation rule that is not authorized for the message's issuer and purpose. The verifier must choose an allowed algorithm and trusted key from local policy, then require the protected metadata and operation to agree with that choice.

Algorithm agility does not mean accepting any algorithm named by the message. Symmetric MAC keys, asymmetric public keys, encryption keys and signature keys have different purposes and representations. A mathematically successful operation with an attacker-supplied or wrong-purpose key does not authenticate the claimed principal.

## Conditions that establish the issue

Recover protected and unprotected algorithm/key metadata, locally allowed algorithms, key type and purpose, issuer-to-key binding, `kid` or equivalent lookup, remote key URLs or embedded keys, certificate validation, cache and rotation behavior, cryptographic API mode, result handling and final identity. Prove attacker influence makes the verifier use an unauthorized algorithm or key and that a forged or wrong-context message is accepted.

For remote key discovery, establish URL trust, fetched bytes, key-set selection and issuer binding. For asymmetric/symmetric confusion, prove the same attacker-known material is accepted under the wrong primitive rather than assuming conversion is possible.

## Evidence that is not sufficient

An `alg`, `kid`, `jku`, `x5u` or embedded-key field, multiple supported algorithms, remote key set, key conversion, verification success or unfamiliar certificate is not sufficient. Local policy may constrain each field, bind keys to one issuer/algorithm/purpose and validate the fetched source.

The mere presence of `none` is not universally invalid; RFC 8725 permits explicit use when other end-to-end cryptographic protection supplies the intended property. Establish the application's required protection.

## Investigation sequence

Build a verifier-selection ledger containing token/message type, attacker-controlled metadata, allowed algorithms, chosen API, key source, key identity/type/purpose, issuer binding, protected status and result. Follow key lookup inputs into databases, files or network requests and record cache/rotation generation. Compare successful cryptographic verification with the principal and purpose finally asserted.

At binary level, recover algorithm dispatch tables, key-object construction, mode flags and branches for unsigned or fallback cases. Confirm which bytes form the authenticated input and which header fields remain unprotected.

## Constructed attacker-selected JWS key source

```text
header = parse_jws_header(token)
keys = fetch_jwk_set(header.jku)
key = keys.find(header.kid)
claims = verify_jws(token, algorithm=header.alg, key=key)
authenticate_as(claims.sub)
```

If `jku`, `kid` and `alg` are accepted from the token without local allowlists and issuer-to-key binding, an attacker can direct verification to attacker-controlled key material and algorithm policy. The finding requires the fetch and selection to succeed, the relevant header fields to control them, cryptographic acceptance and principal creation. A pinned key-set location plus algorithm/key-purpose checks changes the conclusion.

## Primitive and impact limits

The direct primitive is cryptographic acceptance under an unauthorized verifier configuration or key identity. Consequences include token or message forgery, impersonation and cross-protocol substitution. Later authorization and the scope of principals/messages trusted under that verifier determine impact; key-source SSRF can be an additional independent primitive.

## Related knowledge and primary sources

Checksums/MAC/signature, certificate identity, key lifecycle and signed-object binding references provide deeper contracts. This profile repeats local-policy selection and issuer/key/purpose binding locally.

Reviewed 2026-10-09 against [RFC 7515](https://www.rfc-editor.org/rfc/rfc7515.html) for JWS headers and validation, [RFC 7517](https://www.rfc-editor.org/rfc/rfc7517.html) for JSON Web Keys, and [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html) for algorithm verification, key use, indirect key-source risks and cross-token confusion. The example is constructed and does not assert that every use of remote key discovery is unsafe.
