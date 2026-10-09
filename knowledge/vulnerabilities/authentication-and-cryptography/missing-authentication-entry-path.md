---
id: vulnerability-authentication-missing-entry-path
title: Missing authentication on a sensitive entry point or alternate path
kind: vulnerability
topics: [authentication, entry-points, alternate-paths, protocols, identity]
platforms: [cross-platform]
architectures: [any]
---

# Missing authentication on a sensitive entry point or alternate path

## Definition and violated invariant

Missing authentication occurs when a sensitive operation accepts a request without establishing the claimant, peer, device, workload or other principal required by its security policy. Every reachable route to that operation must derive authenticated identity from an accepted mechanism and bind that identity to the current connection, channel, session or request.

Authentication and authorization are separate. A route can authenticate a principal but omit permission checks, or perform a public operation that intentionally needs no principal. Network location, process name, client UI, obscurity and expected caller behavior do not establish identity unless the trust model explicitly authenticates them.

## Conditions that establish the issue

Recover all external and internal entry points, route/operation dispatch, middleware or interceptor ordering, protocol upgrade and fallback paths, peer/session credentials, authentication results and errors, identity propagation, retries, callbacks, background queues and final sensitive operation. Prove an attacker-reachable path reaches the operation without the authentication event or identity binding required by policy.

For local IPC, establish which lower-authority principals can connect or send. For remote interfaces, establish listener exposure, transport and routing. An alternate path matters only if it reaches equivalent sensitive behavior.

## Evidence that is not sufficient

An unauthenticated socket, public route, missing credential parameter, internal method, debug label, health endpoint or absent authentication library is not sufficient. The operation may be intentionally public, protected by a preceding component, unreachable from the attacker, or independently authenticate through transport or platform credentials.

A successful response does not prove a sensitive operation occurred. Bind the request to the resulting object or effect.

## Investigation sequence

Enumerate routes from listener or IPC registration through parsing, dispatch, middleware, authentication, identity construction and handler invocation. Build a path matrix showing entry point, required identity, actual credential source, failure behavior and final operation. Trace aliases, legacy versions, batch endpoints, callbacks, recovery interfaces and direct internal handler registration.

At binary level, locate dispatch tables and compare control-flow predecessors of the sensitive handler. Follow authentication return values and identity arguments rather than relying on nearby strings or imports.

## Constructed alternate-route example

```text
/api/admin/reindex -> authenticate_admin -> reindex_handler
/internal/reindex  ->                      reindex_handler
```

If both routes are remotely reachable and `reindex_handler` performs the same sensitive operation, the second route omits the required authentication step. The finding requires actual route registration, reachability, absence of another authenticating layer and the resulting operation; the word `internal` supplies no boundary by itself.

## Primitive and impact limits

The direct primitive is invocation of a sensitive entry point without the principal assurance required by policy. Consequences depend on the operation and can include data access, state change, account action, administrative control or code execution. Impact is bounded by reachability, later authorization, process authority and the objects or actions exposed.

## Related knowledge and primary sources

Protocol authentication-state, transport identity, authorization and endpoint references provide mechanism detail. This profile keeps path reachability, identity establishment and sensitive effect as separate required evidence.

Reviewed 2026-10-09 against NIST [SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) for verifier/authentication concepts, [RFC 9110 section 11](https://www.rfc-editor.org/rfc/rfc9110.html#section-11) for HTTP authentication semantics, and [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750.html) for one bearer-token protected-resource contract. The route example is constructed; no one mechanism is required for every application.
