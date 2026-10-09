---
id: vulnerability-parser-state-machine-transition-bypass
title: State-machine bypass, illegal transition, or message-order confusion
kind: vulnerability
topics: [parsers, state-machines, protocols, authentication, message-order]
platforms: [cross-platform]
architectures: [any]
---

# State-machine bypass, illegal transition, or message-order confusion

## Definition and violated invariant

A protocol state-machine vulnerability occurs when a message or event is accepted in a phase where its semantics, identity, protection or prerequisite state is not valid, or when transitions update only part of the state on which later dispatch relies. Every accepted message must be legal for the current connection, transaction and authentication generation, and the transition must establish or clear all dependent state as one coherent protocol step.

Recognizing a message type is not permission to process it. Parse success, factor success, negotiation readiness and final authenticated completion are distinct states.

## Conditions that establish the issue

Recover the complete state tuple, legal incoming events, guards, transition writes, failure/reset behavior, queued and concurrent messages, identities captured by outstanding work, and the operation enabled after each transition. Prove an attacker-controlled ordering or event reaches a handler without its required predecessor or retains state that should have been cleared, then trace the resulting sensitive effect.

Include retries, reauthentication, reconnect, cancellation, error recovery and multiplexed streams. A connection-wide flag may be insufficient when authorization belongs to a user, stream, request or factor sequence.

## Evidence that is not sufficient

A switch on message type, unexpected packet, missing local state comparison, permissive parser, partial authentication response, or out-of-order capture is not sufficient. An earlier dispatcher may enforce phase, transport reordering may be corrected, the event may be safely ignored, or the protocol may permit concurrency.

A state label in a decompiler is a hypothesis until its writers, readers and security meaning are recovered.

## Investigation sequence

Draw the state machine from actual dispatch and transition code, naming every field that contributes to the effective phase and identity. Walk valid and invalid event sequences through error and reset paths, including bytes already buffered at transitions. Bind each sensitive handler to the exact predecessor evidence it requires.

For asynchronous handlers, preserve the state or identity captured at admission rather than substituting the connection's current fields when completion runs.

## Constructed authentication example

```c
switch (message.type) {
case FACTOR_OK:
    session->factor_one = true;
    break;
case COMMAND:
    if (session->factor_one)
        execute_command(message.body);
    break;
}
```

If policy requires two factors and `FACTOR_OK` denotes only partial success, this dispatcher enables commands in an intermediate state. The finding requires the protocol's actual completion contract and a reachable command path; a separate outer gate requiring final authentication would refute the bypass.

## Primitive and impact limits

The direct primitive is sensitive processing under an invalid phase, identity or protection context. Consequences can include authentication or authorization bypass, plaintext processing after an upgrade boundary, transaction confusion, replay or stale-session actions.

## Related knowledge and primary sources

`reference-parser-protocol-authentication-state`, `reference-parser-protocol-upgrade-negotiation`, and replay/error-scope references define concrete transitions. This profile repeats current-state, predecessor, identity and effect binding locally.

Reviewed 2026-10-09 against SSH user-authentication [partial and final success](https://www.rfc-editor.org/rfc/rfc4252.html), LDAP [Bind sequencing](https://www.rfc-editor.org/rfc/rfc4511.html#section-4.2.1), and SMTP AUTH [state and completion](https://www.rfc-editor.org/rfc/rfc4954.html). The source is constructed.
