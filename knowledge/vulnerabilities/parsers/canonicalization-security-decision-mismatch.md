---
id: vulnerability-parser-canonicalization-security-decision-mismatch
title: Canonicalization mismatch across signing, hashing, comparison, and authorization
kind: vulnerability
topics: [parsers, canonicalization, signatures, hashes, authorization, object-binding]
platforms: [cross-platform]
architectures: [any]
---

# Canonicalization mismatch across signing, hashing, comparison, and authorization

## Definition and violated invariant

A canonicalization mismatch occurs when a signature, digest, equality check, cache key, or authorization decision covers one representation while a security-relevant consumer derives a different object or meaning from the same input. The checked representation must bind the exact logical fields, object identity, operation, and context that the consumer uses under one specified transformation contract.

Canonicalization is format-specific. JSON Canonicalization Scheme (JCS), for example, requires a restricted JSON input and deterministic serialization but deliberately preserves string data without Unicode normalization. URI decoding, filesystem resolution, case mapping, XML canonicalization, archive-path handling, and protocol field merging have different contracts and cannot be substituted for one another.

## Conditions that establish the issue

Recover the original bytes and every parse, decode, normalization, merge, default, serialization, hashing, verification, comparison, lookup, and resolution stage. Record which exact bytes or logical fields each security decision covers and which final object or operation the consumer selects. Establish an attacker-controlled representation for which the trusted check succeeds but the later interpretation changes a security-relevant field, identity, authority, destination, or operation.

For signatures, also establish trusted key selection and the binding between the verified representation and the consumed object. A mathematically valid signature over one representation does not authorize an object selected through another representation or through unsigned context.

## Evidence that is not sufficient

Multiple encodings, normalization calls, a canonicalizer, visually similar text, a valid signature, a digest match, duplicate fields, or parser disagreement is not sufficient. Different representations may be intentionally equivalent, the later consumer may use the checked value directly, or the changed field may have no security effect.

A custom deterministic serializer is not evidence that it implements a named canonicalization standard. Conversely, differing display text does not establish differing object identity; trace the actual consumer.

## Investigation sequence

Build a representation ledger from input bytes to the final operation. For each stage record grammar, character encoding, duplicate and unknown-field rules, normalization form, case/locale behavior, escape decoding, ordering, defaults, output bytes, and owner. Mark the exact input to the signature, digest, comparison, cache, and authorization operations.

Compare the field set and transformation order at the check and use sites. Follow reparsing, reserialization, path resolution, member selection, content negotiation, and mutable external context. Retain both forms rather than replacing evidence with a normalized display.

## Constructed duplicate-field example

```c
/* Constructed formats: canonical_for_mac keeps the first duplicate field;
   parse_request keeps the last duplicate field. */
bytes canonical = canonical_for_mac(message);
if (!verify_mac(key, canonical, supplied_mac))
    reject();
request r = parse_request(message);
dispatch(r.operation);
```

For a message whose first `operation` is benign and last `operation` is privileged, the check and dispatch can bind different logical values. The finding requires those actual duplicate rules, a valid MAC under the trusted key, attacker control of the duplicate representation, and a reachable privileged dispatch. Duplicate syntax alone does not establish the issue, and a format that rejects duplicates at both stages changes the conclusion.

## Primitive and impact limits

The direct primitive is acceptance of an object, identity, or operation that was not the object, identity, or operation covered by the trusted check. Consequences can include signature or policy bypass, wrong-object authorization, cache confusion, request smuggling, path substitution, or integrity-check bypass. Code execution requires a downstream operation that supplies that consequence.

## Related knowledge and primary sources

`reference-crypto-signed-object-consumer-binding`, `reference-parser-framing-normalization-differences`, `reference-parser-unicode-normalization-comparison`, and duplicate-field references define the underlying contracts. This profile repeats the required checked-object and consumed-object binding locally.

Reviewed 2026-10-09 against [FIPS 186-5](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf) for the signature relation, [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) for JCS input and serialization rules, [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html) for URI component and percent-decoding distinctions, and [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html) for JSON object syntax. The duplicate-field behavior and code are constructed and must not be attributed to those standards.
