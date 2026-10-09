---
id: vulnerability-authentication-authenticated-request-replay
title: Replay of an authenticated request without freshness or consumed-state checks
kind: vulnerability
topics: [authentication, replay, freshness, nonces, sequence-numbers, signatures]
platforms: [cross-platform]
architectures: [any]
---

# Replay of an authenticated request without freshness or consumed-state checks

## Definition and violated invariant

An authenticated replay vulnerability occurs when a previously valid authenticated message can be presented again and cause an operation whose policy permits it only once or only within a specific fresh transaction, channel or state generation. Authentication proves an origin/integrity relation under its protocol; it does not automatically prove freshness, uniqueness, ordering or non-repetition.

Freshness mechanisms include nonces, sequence numbers, timestamps with an authoritative window, challenge-response binding, transaction identifiers with atomic consumption and channel/session context. The correct mechanism and replay scope depend on the protocol. Idempotent operations can tolerate duplicate delivery even when the transport retries them.

## Conditions that establish the issue

Recover exact authenticated bytes and covered fields, signer/MAC identity, operation and object binding, nonce/sequence/time/challenge fields, issuance and acceptance window, replay cache or consumed-state key/scope, atomic check-and-consume behavior, retries, clustering and restart persistence, transaction result and duplicate side effect. Prove an attacker can capture or reproduce a valid message and have another acceptance cause an unauthorized repeated or out-of-context effect.

If timestamps are used, establish clock authority and window. If uniqueness state is distributed, establish whether every accepting node shares the required consumed state.

## Evidence that is not sufficient

A repeated packet, identical signature, absent nonce, retry, duplicated log, timestamp or non-idempotent endpoint is not sufficient. The protocol may bind a transport sequence, consume server-side state, make the operation idempotent, or return a cached result without repeating the effect.

A nonce's presence is not proof of replay resistance unless it is unpredictable or unique as required, authenticated, scoped to the operation and rejected after use.

## Investigation sequence

Build an acceptance ledger containing message identity, authenticated fields, principal, operation/object, freshness value, state generation, accepting node, replay lookup, consumption commit and effect. Trace failure, retry, timeout and crash paths for check/commit gaps. Separate duplicate transport delivery from duplicate application execution.

At binary level, locate signature/MAC verification, freshness comparisons, replay-cache keys and storage updates. Check whether success is returned or effects occur before uniqueness state is committed.

## Constructed signed-operation example

```text
request = { account, amount, destination }
signature = sign(request, client_key)
server: if verify(signature, request, client_public_key): transfer(request)
```

The signature binds the shown transfer fields but supplies no request uniqueness or transaction state. Capturing and resending the same pair can repeat the transfer if the server accepts every valid signature and `transfer` is not idempotent. The finding requires replay feasibility and a second committed effect; absence of a visible nonce does not rule out hidden server-side consumed state.

## Primitive and impact limits

The direct primitive is repeated acceptance of previously authenticated authority. Consequences can include duplicate payment, command, enrollment, state transition or resource consumption. Capture ability, message lifetime, freshness scope, operation idempotency, transaction semantics and later authorization bound impact.

## Related knowledge and primary sources

`reference-crypto-authenticated-freshness-replay-state`, retry/transaction and protocol replay references provide deeper mechanisms. This profile repeats authentication-versus-freshness and atomic consumption locally.

Reviewed 2026-10-09 against [RFC 9421 section 7.2](https://www.rfc-editor.org/rfc/rfc9421.html#section-7.2) for HTTP message-signature replay considerations, [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html) for protocol-scoped replay distinctions including early data, and NIST [SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) for verifier and session scope. The example is constructed.
