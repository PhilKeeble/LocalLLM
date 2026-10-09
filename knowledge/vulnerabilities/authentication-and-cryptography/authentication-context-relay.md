---
id: vulnerability-authentication-context-relay
title: Authentication or credential use not bound to intended peer, channel, session, or request
kind: vulnerability
topics: [authentication, relay, channel-binding, forwarding, peer-identity, context-binding]
platforms: [cross-platform]
architectures: [any]
---

# Authentication or credential use not bound to intended peer, channel, session, or request

## Definition and violated invariant

An authentication-context vulnerability occurs when valid proof or a credential created for one peer, secure channel, session or request can be forwarded or substituted so that another context accepts it with unintended authority. Authentication of a principal does not automatically prove that the principal sees the same endpoint, channel or operation as the verifier.

Channel binding is one protocol family for establishing that higher-layer authenticated endpoints correspond to a lower-layer secure channel. Other protocols bind audience, server identity, transcript, request fields or proof-of-possession context differently; no universal channel-binding token exists.

## Conditions that establish the issue

Recover the claimant and verifier identities, intended peer or service, credential or proof inputs, challenge provenance, authenticated transcript, channel/session identifier, audience and request fields, intermediary behavior, acceptance context, freshness and final authorized operation. Prove an attacker can obtain or relay valid proof from one context and cause acceptance in another context that the credential holder did not authorize.

Establish the attacker's positions on both legs and whether mutual authentication, endpoint identity or protected confirmation closes the relay. Simple credential theft is a different path when the attacker learns reusable secret material.

## Evidence that is not sufficient

A proxy, forwarded token, challenge-response protocol, shared identity provider, missing channel-binding API, two connections or successful authentication is not sufficient. The proof may bind the intended audience and request, the intermediary may be trusted and authorized, the channel may be confirmed inside the transcript, or the operation may require separate user approval.

Channel encryption on each leg does not by itself prove or disprove end-to-end context binding. Recover what the authenticated data covers.

## Investigation sequence

Draw both communication legs with endpoint identities, channel keys or identifiers, challenges, signed or MACed fields, token audience, session state and requested operation. Label which actor constructs each field and which verifier checks it. Compare the user's perceived peer and action with the target's accepted peer and action, then follow acceptance into effective authority.

At binary or managed-code level, trace challenge and channel-binding inputs into proof generation and verification. Confirm that a field logged or displayed to the user is part of the authenticated representation rather than untrusted presentation.

## Hypothetical relay flow

```text
attacker -> target: begin authentication
target -> attacker: challenge C
attacker -> victim: presents C as a challenge for another service
victim -> attacker: proof Sign_victim(C)
attacker -> target: Sign_victim(C)
target: accepts victim identity and attacker's pending operation
```

The flow is vulnerable only if the proof omits the intended service, channel and operation context required by the protocol, the victim can be induced to produce it, and the target associates it with the attacker's pending request. A challenge alone can provide freshness while still lacking peer or request binding.

## Primitive and impact limits

The direct primitive is forwarding valid authentication authority into an unintended context. Consequences can include impersonation, transaction substitution or access through an attacker-controlled channel. Scope is bounded by the authenticated principal, accepted request, session lifetime and later authorization; relay does not imply disclosure of the underlying credential.

## Related knowledge and primary sources

Certificate identity, signed-object, replay and session references cover neighboring bindings. This profile keeps the two contexts and their final operation explicit.

Reviewed 2026-10-09 against [RFC 5056](https://www.rfc-editor.org/rfc/rfc5056.html) for the general concept of binding higher-layer authentication endpoints to a lower-layer secure channel. The flow is hypothetical; each authentication protocol defines its own binding and failure semantics.
