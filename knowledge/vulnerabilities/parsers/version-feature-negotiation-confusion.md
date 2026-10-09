---
id: vulnerability-parser-version-feature-negotiation-confusion
title: Version, feature, or negotiation confusion selecting the wrong grammar
kind: vulnerability
topics: [parsers, negotiation, versions, features, protocol-selection]
platforms: [cross-platform]
architectures: [any]
---

# Version, feature, or negotiation confusion selecting the wrong grammar

## Definition and violated invariant

A negotiation/grammar vulnerability occurs when peers agree on one version, feature set, protection mode or application protocol but a component parses subsequent bytes under a different grammar, or when fallback selects a mode below required policy. The committed negotiation result, parser, encoder, capability state and security policy must describe the same epoch and direction.

A larger version number or differently named mechanism is not universally stronger. Compatibility fallback is a vulnerability only when it violates the effective policy and changes a reachable security property.

## Conditions that establish the issue

Recover proposals as counted values, supported intersection, policy check, selected value, integrity or authentication of the exchange, commit point, parser dispatch, buffered bytes at transition, per-direction activation and reset of prior capabilities. Prove attacker influence can make the selected parser or feature state disagree with the committed result or reach a prohibited fallback and sensitive effect.

Treat absence, unknown values, malformed values and negotiation failure as separate branches. For protocol names, apply exact length and byte equality rather than inferred string or prefix semantics.

## Evidence that is not sufficient

Version parsing, legacy support, fallback code, multiple parsers, an advertised protocol list, or recognizable payload bytes is not sufficient. Policy may permit the alternate mode, a later exact comparison may bind dispatch, or the observed offer may not be the selected result.

Failure to observe an encrypted negotiation field is not evidence that no selection occurred.

## Investigation sequence

Trace offer, selection, validation and parser installation as separate values. Record the byte offset where each direction changes grammar or protection and account for already buffered data. Compare feature caches before and after the transition according to the selected protocol.

Follow every failure branch into retry or fallback and identify the effective minimum policy. Connect any disagreement to an actual interpretation or authorization difference.

## Constructed ALPN selection example

```c
if (selected_length >= 2 && memcmp(selected, "h2", 2) == 0)
    connection->parser = HTTP2_PARSER;
```

ALPN protocol names are nonempty opaque byte strings, so a selected value `h2x` is distinct from `h2`. The prefix check can install the HTTP/2 parser for a different identifier if such a value can become the committed selection. The finding requires the actual TLS API's selected bytes and length, reachable peer influence and a security-relevant grammar difference; a prior exact allowlist would refute it.

## Primitive and impact limits

The direct primitive is parsing or protection under the wrong negotiated contract. Consequences can include downgrade, framing disagreement, authentication-state loss, request smuggling or bypass of feature-specific validation.

## Related knowledge and primary sources

`reference-parser-protocol-upgrade-negotiation` and configuration/fallback references cover negotiation and policy. This profile repeats selected-value, transition-byte and parser binding locally.

Reviewed 2026-10-09 against ALPN [identifier and selection rules](https://www.rfc-editor.org/rfc/rfc7301.html), TLS 1.3 [extension processing](https://www.rfc-editor.org/rfc/rfc8446.html), and SMTP STARTTLS [transition/reset rules](https://www.rfc-editor.org/rfc/rfc3207.html). The source is constructed.
