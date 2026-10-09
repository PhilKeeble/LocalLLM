---
id: vulnerability-authentication-inadequate-cryptographic-property
title: Cryptographic algorithm, mode, parameter, or key does not provide the required property
kind: vulnerability
topics: [cryptography, algorithms, modes, parameters, key-size, policy, agility]
platforms: [cross-platform]
architectures: [any]
---

# Cryptographic algorithm, mode, parameter, or key does not provide the required property

## Definition and violated invariant

An inadequate-cryptography vulnerability occurs when the effective algorithm, protocol, mode, parameter set or key fails to provide a security property required at the investigated boundary under the applicable threat, policy and time context. A recognized or historically deployed algorithm name is not a timeless finding; the analyst must identify the missing property, selected parameters and authoritative requirement.

Algorithm availability and cryptographic agility differ from permission to use every supported choice. Confidentiality, integrity, origin authentication, collision resistance, offline-guessing cost and forward secrecy are distinct properties.

## Conditions that establish the issue

Recover the protected asset and threat model, required property and policy source, actual algorithm and construction, mode, key material and effective strength, parameters, message and key lifecycle, negotiation or configuration source, hardware/provider implementation, accepted result and security-sensitive consumer. Show that the reachable selection fails the stated requirement and that an attacker can exercise the relevant capability.

Retain the assessment date and policy scope when cryptanalytic knowledge or organizational requirements can change. Distinguish a structural property mismatch from a time-dependent strength judgment.

## Evidence that is not sufficient

A legacy name, short-looking key, deprecated option, library support, checksum, unusual mode, static scanner label or configuration string is not sufficient. The path may be unreachable, the value may describe a different operation, an outer authenticated channel may supply the required property, or the governing policy may permit the construction for that nonsecurity role.

Conversely, a current algorithm name does not prove correct mode, parameters, key generation, nonce lifecycle, verification or consumer binding.

## Investigation sequence

Start with the boundary's required security property, then trace configuration and negotiation to the effective primitive and parameters used for the accepted operation. Record provider identity and fallbacks, key provenance, complete inputs and result handling. Compare only with a primary specification or policy applicable to the product, protocol and assessment context.

At binary level, distinguish identifiers used for parsing or display from constants and dispatch targets that select the executed primitive. Follow transformed parameter widths and defaults into initialization and final use.

## Hypothetical selection example

```text
algorithm = message.algorithm
if crypto_provider.supports(algorithm):
    result = verify_or_decrypt(algorithm, key, message)
    accept(result)
```

Provider support is a capability check, not the application's security policy. This path is vulnerable only if attacker influence selects a construction that lacks a required property, the provider accepts it, and the result reaches the protected consumer without an independent policy check. The example intentionally names no universally weak algorithm.

## Primitive and impact limits

The direct effect is loss or weakening of the specific required cryptographic property. Disclosure, forgery, impersonation or recovery of protected material depends on the construction, attacker observations or queries, computational feasibility and consumer. Do not claim compromise solely from noncompliance when no applicable attack relation has been established.

## Related knowledge and primary sources

Negotiation, key lifecycle, nonce, signature and password-verifier references supply property-specific contracts. This profile provides the evidence threshold for a policy or strength mismatch without duplicating changing recommendation tables.

Reviewed 2026-10-09 against [RFC 7696](https://www.rfc-editor.org/rfc/rfc7696.html) for algorithm agility, selection and transition considerations. Algorithm-specific claims require the selected primitive's primary specification and the policy applicable to the target; no version-sensitive approved-algorithm list is embedded here.
