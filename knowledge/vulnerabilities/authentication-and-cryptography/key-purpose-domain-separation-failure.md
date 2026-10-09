---
id: vulnerability-authentication-key-purpose-domain-separation-failure
title: Cryptographic key-purpose or domain-separation failure
kind: vulnerability
topics: [cryptography, key-purpose, domain-separation, kdf, protocols, cross-context]
platforms: [cross-platform]
architectures: [any]
---

# Cryptographic key-purpose or domain-separation failure

## Definition and violated invariant

A key-purpose or domain-separation vulnerability occurs when the same key material or indistinguishably derived material is used across algorithms, protocols, tenants, environments or purposes whose outputs can be accepted in one another's security domains. Ordinary reuse is not sufficient: the finding requires conflicting contracts and a reachable cross-domain consumer.

Domain separation can come from distinct keys or a cryptographically bound, unambiguous context in derivation or protected input. RFC 5869's HKDF `info` input is one mechanism for binding derived key material to application and context information; it is not a universal repair for every protocol.

## Conditions that establish the issue

Recover actual key material or a supported handle relationship, derivation tree and inputs, algorithm and operation on each path, domain labels and encoding, tenant/environment/purpose, protected message formats, attacker access to an output or oracle in one domain, and acceptance in the other. Prove an output or capability from one permitted use satisfies the other consumer's verification or decryption contract without the authority that domain requires.

For derivation, compare complete encoded contexts and output lengths. Different variable names or key IDs do not establish separation, while equal source material can still yield separated keys under a sound labeled construction.

## Evidence that is not sufficient

The same key ID, provider, master secret, hash function, HMAC primitive or KDF call is not sufficient. Handles may select different material, a derivation context may separate outputs, message encodings may be disjoint, or the two uses may intentionally share one security domain and authority.

Conversely, different labels are inconclusive if their encodings collide or the consumer ignores them.

## Investigation sequence

Build a key derivation and use graph from root material through salt, label, context, length and provider selection to each operation. For every output or oracle available to the attacker, compare its exact protected bytes and result with other consumers under the same or related material. Preserve tenant, environment, protocol version and key generation at every edge.

At binary level, trace key handles and KDF arguments rather than relying on symbol names. Reconstruct label lengths and concatenation boundaries to determine whether contexts are unambiguous.

## Hypothetical cross-purpose MAC example

```text
authentication_token_tag = HMAC(K, payload)
update_manifest_tag       = HMAC(K, payload)
```

If the same `K`, byte representation and tag verification rule are used and an attacker can obtain a valid authentication-token tag for bytes that the updater also accepts as a manifest, one domain can mint an accepted object for the other. Reuse alone is inconclusive when formats are disjoint or an authenticated purpose label distinguishes them.

## Primitive and impact limits

The direct primitive is cross-domain acceptance of a cryptographic output or unauthorized access to an operation under shared material. Impact depends on the stronger domain reached and the messages the lower-authority actor can obtain or choose. Key recovery is not implied; a signing or MAC oracle can be sufficient for a narrower forgery.

## Related knowledge and primary sources

Key lifecycle, signed-object and algorithm-selection references provide surrounding key identity and consumer contracts. This profile keeps derivation context, available oracle and cross-domain acceptance together.

Reviewed 2026-10-09 against [RFC 5869 section 3.2](https://www.rfc-editor.org/rfc/rfc5869.html) for HKDF `info` as application- and context-specific binding. The example is hypothetical and requires a demonstrated shared representation and consumer; the RFC does not define every protocol's domain-separation needs.
