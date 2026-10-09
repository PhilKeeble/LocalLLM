---
id: vulnerability-authentication-sensitive-data-boundary-protection-gap
title: Sensitive data lacks required confidentiality, integrity, or peer authentication
kind: vulnerability
topics: [cryptography, sensitive-data, confidentiality, integrity, transport-security, storage]
platforms: [cross-platform]
architectures: [any]
---

# Sensitive data lacks required confidentiality, integrity, or peer authentication

## Definition and violated invariant

A data-protection vulnerability occurs when sensitive data crosses a storage, process, device or network boundary without the confidentiality, integrity, authenticity or peer-identity property required for that boundary. These properties must be evaluated separately: encryption without intended-peer authentication can protect a channel to the wrong endpoint, while integrity without confidentiality can leave data readable.

Sensitivity and required protection come from the asset and threat model. Plaintext in a process that must consume it is not automatically a defect; the question is whether an actor outside the permitted trust boundary can observe or alter it.

## Conditions that establish the issue

Recover the exact data and representation, classification or security contract, producer and consumer, trust boundary, storage object or route, effective peer identity, protection mechanism and covered bytes, key and nonce state, access controls, intermediate copies, logs and caches, attacker read or write capability, and final use. Prove the missing property allows access or modification outside the authorized scope.

For transport, follow name resolution, redirects, proxies, tunneling and certificate identity to the final peer. For storage, include snapshots, backups, temporary files, memory-mapped copies and key accessibility under the same attacker model.

## Evidence that is not sufficient

A plaintext string in a binary, HTTP-looking URL, unencrypted buffer, database field, filesystem write, disabled-looking option or absence of a crypto import is not sufficient. The data may be public, a protected outer layer may apply, the storage boundary may already enforce the required access policy, or another component may transform it before crossing the boundary.

Encryption presence is also inconclusive without covered extent, verification, key authority and peer or object binding.

## Investigation sequence

Draw the data path from creation through serialization, queues, IPC, network hops, storage, backups and consumption. For each boundary, record who can read or modify bytes, which property is required, what mechanism supplies it and where verification occurs. Trace failures and fallbacks for paths that bypass protection, and join the exposed or modifiable representation to its security-sensitive meaning.

At binary level, follow buffer extents into I/O and crypto calls, then recover endpoint or object selection and result handling. Strings and API names are starting points, not proof of the effective channel.

## Hypothetical transport example

```text
connection = tcp_connect(configured_host, configured_port)
send(connection, "Authorization: Bearer " + access_token)
```

The shown path supplies neither transport confidentiality nor peer authentication. It is a vulnerability only if the token requires those properties at this boundary and an attacker can observe or substitute the connection. An authenticated encrypted tunnel outside the shown component can change the conclusion.

## Primitive and impact limits

The direct primitive is unauthorized observation or modification of the protected representation at the identified boundary. Consequences depend on data meaning, lifetime, replayability and downstream validation. Credential capture can support impersonation only within the credential's scope; ciphertext modification matters only if it survives integrity and consumer checks.

## Related knowledge and primary sources

Certificate identity, AEAD, signed-object and key-lifecycle references provide mechanism-specific contracts. This profile keeps asset, boundary, required property and attacker capability explicit.

Reviewed 2026-10-09 against [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html) for the distinct authentication, confidentiality and integrity properties of a TLS channel, and NIST [SP 800-111](https://csrc.nist.gov/pubs/sp/800/111/final) for storage-encryption threat and access distinctions. The example is hypothetical; neither source defines every application's data-classification policy.
