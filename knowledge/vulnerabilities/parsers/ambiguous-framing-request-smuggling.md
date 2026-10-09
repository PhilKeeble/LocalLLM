---
id: vulnerability-parser-ambiguous-framing-request-smuggling
title: Ambiguous framing, duplicate lengths, and request/response smuggling
kind: vulnerability
topics: [parsers, framing, request-smuggling, lengths, protocols]
platforms: [cross-platform]
architectures: [any]
---

# Ambiguous framing, duplicate lengths, and request/response smuggling

## Definition and violated invariant

A framing-smuggling vulnerability occurs when adjacent components disagree about where one message ends and the next begins because of conflicting lengths, transfer modes, duplicate fields, delimiter handling, malformed syntax, protocol translation or partial-body recovery. Every hop that shares a byte stream must consume the same message boundary before applying authorization, routing or connection reuse.

Protocol-specific precedence matters. Rules for one HTTP version, request role or response status cannot be generalized to every framed protocol.

## Conditions that establish the issue

Recover exact bytes at each hop, request/response role, protocol version and translation, framing fields and duplicates, parser leniency, selected body length, bytes consumed, forwarded representation, connection reuse and the security context assigned to following bytes. Prove two components choose different boundaries and that attacker-controlled remainder reaches another request or response context.

For length-delimited messages, trace premature EOF, timeout and error recovery. An incomplete body must not silently become a shorter successful message unless the protocol defines that behavior.

## Evidence that is not sufficient

Both `Content-Length` and `Transfer-Encoding`, duplicate lengths, chunk syntax, extra bytes, keep-alive, or different parser errors is not sufficient. A front end may reject the message, normalize it to one unambiguous framing, close the connection, or both hops may apply the same precedence.

The presence of bytes after a parsed message does not prove smuggling when the protocol legitimately pipelines messages and both peers agree on the boundary.

## Investigation sequence

Replay the byte stream conceptually through each actual component and record the consumed prefix, body rule, error and forwarded bytes. Preserve raw octets rather than a Unicode or reconstructed header view. Include connection pooling and which principal or route owns the next parsed message.

Then connect the boundary disagreement to a concrete cross-request effect, such as bypassing a front-end check, poisoning another user's response or causing a privileged backend request.

## Constructed HTTP/1.1 differential

Assume a front end treats `Content-Length: 4` as the request body size while a backend gives a valid `Transfer-Encoding: chunked` field precedence and interprets the following octets as chunk framing. The two parsers can consume different prefixes, leaving attacker-selected bytes to begin a backend request. RFC 9112 specifies precedence and error handling that must be applied to the actual request; merely including both fields does not prove either component violates it.

## Primitive and impact limits

The direct primitive is control over bytes interpreted in a different message or principal context. Consequences can include authorization bypass, cache poisoning, response mix-up or backend request injection; impact depends on connection reuse, routing and the authority of the desynchronized hop.

## Related knowledge and primary sources

`reference-parser-framing-normalization-differences`, `reference-parser-stream-recovery-limits`, and protocol references define concrete framing contracts. This profile repeats per-hop bytes, boundary and context binding locally.

Reviewed 2026-10-09 against HTTP/1.1 [message parsing, framing and request-smuggling guidance](https://www.rfc-editor.org/rfc/rfc9112.html), HTTP semantics [field combination rules](https://www.rfc-editor.org/rfc/rfc9110.html), and [MITRE CWE-444](https://cwe.mitre.org/data/definitions/444.html). The scenario is constructed.
