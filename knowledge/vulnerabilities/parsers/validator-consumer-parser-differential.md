---
id: vulnerability-parser-validator-consumer-differential
title: Validator and consumer parser differential
kind: vulnerability
topics: [parsers, parser-differential, validation, normalization, canonicalization]
platforms: [cross-platform]
architectures: [any]
---

# Validator and consumer parser differential

## Definition and violated invariant

A parser-differential vulnerability occurs when two components assign different structure, field values, object identity or validity to the same attacker-controlled representation and a security decision made under one interpretation governs an effect under the other. The validator and final consumer must agree on framing, decoding, duplicate handling, normalization and error recovery for every security-relevant value.

Disagreement or nonconformance alone is not a vulnerability. The two interpretations must be connected through the actual data path and change a bound, authority decision, selected object, operation or state transition.

## Conditions that establish the issue

Capture the exact bytes supplied to each component and recover their grammar, configuration, decoding order, duplicate policy, malformed-input behavior, selected values and outputs. Prove validation permits the representation, the consumer selects a conflicting security-relevant interpretation, and the resulting operation crosses the intended boundary.

Account for intermediaries that reserialize, merge, normalize or truncate data. An already collapsed dictionary can hide original duplicates, so retain raw bytes.

## Evidence that is not sufficient

Two parser libraries, different error messages, duplicate fields, encoded delimiters, case differences, or one acceptance/rejection mismatch is not sufficient. Both components may select the same effective value, the discrepancy may be inert, or a canonical intermediate representation may remove it before the security decision.

An analyst tool disagreeing with the target is evidence about the tool boundary, not proof of target concealment or exploitation.

## Investigation sequence

Make a side-by-side table of raw input, stage, grammar, decoded representation, selected field, error state and output bytes. Follow the representation used for authorization to the representation used for the effect without assuming a library's default behavior.

Test duplicate, whitespace, encoding, normalization and malformed-input rules only where the selected formats permit them. State the exact divergent value and consequence.

## Constructed duplicate-field example

```json
{"operation":"read","operation":"delete"}
```

If a validator retains the first `operation` and authorizes `read`, while the executor's parser retains the last and performs `delete`, the same bytes cross the boundary under different selected values. JSON recommends unique names but implementations differ in duplicate handling, so the finding requires observation or recovery of both actual policies; the duplicate object alone proves neither winner.

## Primitive and impact limits

The direct primitive is interpretation chosen under a weaker or different security decision. Consequences can include request smuggling, path or identity bypass, unauthorized operation selection, signature bypass, or bounds disagreement; impact is limited by the downstream consumer's authority.

## Related knowledge and primary sources

`reference-parser-framing-normalization-differences` and `reference-parser-duplicate-fields-decoded-values` define common differential sources. This profile repeats the two-parser data path and consequence proof locally.

Reviewed 2026-10-09 against JSON [object-name guidance](https://www.rfc-editor.org/rfc/rfc8259.html), HTTP/1.1 [parsing and smuggling guidance](https://www.rfc-editor.org/rfc/rfc9112.html), and [MITRE CWE-436](https://cwe.mitre.org/data/definitions/436.html). The JSON example is constructed.
