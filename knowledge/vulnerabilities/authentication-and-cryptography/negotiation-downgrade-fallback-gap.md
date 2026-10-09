---
id: vulnerability-authentication-negotiation-downgrade-fallback-gap
title: Downgrade or fallback state not bound to authenticated negotiation
kind: vulnerability
topics: [cryptography, negotiation, downgrade, fallback, transcript, protocol-state]
platforms: [cross-platform]
architectures: [any]
---

# Downgrade or fallback state not bound to authenticated negotiation

## Definition and violated invariant

A negotiation downgrade vulnerability occurs when an attacker can cause peers to accept protection weaker than their effective security policy because the offered, selected or fallback state is not authenticated, not checked against that policy, or is replaced after a failure without preserving the intended peer and protection requirements. Negotiation inputs may be public and attacker-influenced; the defect is acceptance of an impermissible result, not influence alone.

Protocol-specific transcript and downgrade mechanisms define what is bound. TLS 1.3, for example, authenticates a defined handshake transcript and specifies scoped version downgrade signaling; those rules cannot be generalized to arbitrary protocols.

## Conditions that establish the issue

Recover local minimum policy, offered values, peer identity, on-wire negotiation and authenticated transcript coverage, selected parameters, validation result, retry and fallback triggers, cached state, reconnect behavior and first protected application effect. Prove an attacker can alter, suppress or fail a stronger path and make the implementation accept a result forbidden by the applicable policy.

For fallback, preserve whether the retry reaches the same intended peer and whether authentication, confidentiality, integrity or algorithm constraints changed. A deliberately configured compatibility mode is still evaluated against the actual required policy.

## Evidence that is not sufficient

Support for an older protocol, a fallback-named function, multiple offered algorithms, cleartext negotiation bytes, a failed handshake or a weaker selected mode is not sufficient. The selected result may remain within policy, later transcript authentication may detect alteration, fallback may abort before sensitive use, or an administrator may have authorized the relevant scope.

A current configuration does not prove the policy applied to cached or already established sessions. Bind policy generation and session state.

## Investigation sequence

Construct a state diagram containing configured offers, transmitted offers, peer response, authenticated transcript fields, selection, validation, failure class, retry state and application release. Trace timeout, parsing, certificate, integrity and unsupported-mode errors separately because they may trigger different fallbacks. Follow cached negotiation decisions through identity, expiry and configuration changes.

At binary level, locate comparison of selected parameters to policy and the branches from negotiation failure into reconnect or alternate transport. Confirm whether application data or credentials are released only after the accepted state is authenticated.

## Hypothetical fallback example

```text
connection = connect_authenticated(endpoint, minimum_policy)
if connection.failed:
    connection = connect_plain(endpoint)
send_credentials(connection)
```

If an active attacker can cause the authenticated attempt to fail and the same security-sensitive operation then proceeds over the unauthenticated fallback contrary to policy, the failure trigger becomes a downgrade primitive. The example is not a finding if plain transport is independently authorized for that operation or credentials never reach the fallback.

## Primitive and impact limits

The direct primitive is attacker-influenced acceptance of a weaker or differently authenticated channel, algorithm or mode. Consequences depend on the lost property and network position: observation, modification, peer substitution or later protocol abuse may follow. Remote code execution requires a separate execution or memory-safety path reached through the downgraded context.

## Related knowledge and primary sources

`reference-crypto-negotiation-fallback-policy`, protocol-state and failure-policy references provide deeper transcript and transition contracts. This profile repeats the required path from effective policy to accepted mode and sensitive effect.

Reviewed 2026-10-09 against [RFC 8446 sections 4.1.3 and 4.4](https://www.rfc-editor.org/rfc/rfc8446.html) for TLS 1.3's scoped downgrade signal and authenticated transcript. The example is hypothetical and does not apply TLS rules to other negotiations.
