---
id: vulnerability-authentication-signed-object-consumer-binding-gap
title: Signed object verified without binding the exact representation and consumer
kind: vulnerability
topics: [cryptography, signatures, canonicalization, object-binding, manifests, parsing]
platforms: [cross-platform]
architectures: [any]
---

# Signed object verified without binding the exact representation and consumer

## Definition and violated invariant

A signed-object binding vulnerability occurs when signature verification succeeds for one byte representation, interpretation, object or context but a security-sensitive consumer acts on a different one. A signature relates a signature value, verification key and exact message under a selected algorithm; it does not automatically bind an independently selected file, parser interpretation, operation, audience or environment.

Canonicalization is safe only under the specified representation and input restrictions shared by verification and consumption. Re-serialization, duplicate fields, numeric conversion, Unicode handling, detached content selection and archive member lookup can create different objects even when a log labels them alike.

## Conditions that establish the issue

Recover the verification key and its authorization policy, algorithm and parameters, exact signed bytes or digest input, canonicalization and parser rules, signature result, identifiers or digests carried by the signed object, object resolution after verification, bytes and interpretation actually consumed, and resulting operation. Prove attacker influence can make the verified representation and security-relevant consumer select materially different content or context.

For a time-of-check/time-of-use path, establish that the consumed object can change or be reselected after verification. For parser differentials, demonstrate the relevant divergent interpretations rather than inferring them from format complexity.

## Evidence that is not sufficient

A valid signature, detached content, JSON document, duplicate-looking field, reserialization, filename reopen, hash comparison or second parser is not sufficient. The signature may cover a trusted digest that uniquely selects the consumed bytes, both parsers may enforce the same canonical contract, or the verified object may be held by stable identity through use.

An untrusted expected digest that matches content does not authenticate its producer. Conversely, a signature failure says nothing by itself about whether other trusted policy authorized the object.

## Investigation sequence

Label every representation from received bytes through decoding, canonicalization, hashing, verification, parsing, object lookup and final use. Record byte extents, parser modes, duplicate and normalization rules, identifier namespaces, filesystem/archive resolution and object identity at check and use. Join the verification result to the authorized signer policy, then join the signed selection to the exact consumed bytes and operation.

At binary level, follow pointers and lengths entering digest or verify calls and compare them with buffers, handles or objects reaching the consumer. A shared filename string is weaker evidence than a retained handle or verified content identity.

## Hypothetical detached-manifest example

```text
if verify(release_key, request.manifest_bytes, request.signature):
    install(open(request.package_path))
```

The signature authenticates `manifest_bytes`, but the shown installation uses an independently caller-selected path. The path is vulnerable only if no signed field or trusted policy binds the selected package and an attacker can cause installation of different bytes. A signed manifest digest compared with the exact retained package object would change the analysis.

## Primitive and impact limits

The direct primitive is trusted consumption of content, an object or a context not established by the successful signature relation. Consequences can include unauthorized installation, policy selection, configuration or command acceptance. Code execution requires the mismatched object to be activated as code or to reach another execution primitive under relevant authority.

## Related knowledge and primary sources

`reference-crypto-signed-object-consumer-binding` provides signature, digest and canonicalization fundamentals; parser and update references cover object selection and stable consumption. This profile keeps exact verified representation and final consumer in one chain.

Reviewed 2026-10-09 against NIST [FIPS 186-5](https://csrc.nist.gov/pubs/fips/186-5/final) for the signature-generation and verification relation, and [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html) for one explicitly scoped JSON canonicalization contract. The example is hypothetical; other formats require their own representation rules.
