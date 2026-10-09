---
id: vulnerability-injection-multi-language-decoding-interpretation-chain
title: Multi-language or multi-decoding interpretation chain
kind: vulnerability
topics: [injection, decoding, polyglot, escaping, normalization, parser-differential]
platforms: [cross-platform]
architectures: [any]
---

# Multi-language or multi-decoding interpretation chain

## Definition and violated invariant

A layered-interpretation vulnerability occurs when data passes through multiple languages, encodings, templates, or decoders and validation under an earlier representation does not constrain the syntax or object produced for a later consumer. Each layer must remove exactly its own encoding and hand the next layer a value that satisfies that next grammar's security contract; escaping or validation for one language cannot be assumed valid for another.

Legitimate nesting is common: JSON can carry a URL, HTML can contain JavaScript, configuration can contain a query, and a protocol field can contain compressed or encoded data. The defect is a demonstrated check/use disagreement or unintended reinterpretation, not the number of parsing calls.

## Conditions that establish the issue

Recover every representation in order, including bytes, character encoding, container grammar, escaping, percent/base/character decoding, normalization, template expansion, field merge, parser mode, and final consumer. Prove attacker-controlled data is inert or accepted at one checked layer but becomes security-relevant syntax, a delimiter, or another object identity at a later layer that lacks an equivalent check.

Name which component owns each decode. Repeated decoding of the same representation differs from correctly decoding separately encoded outer and inner formats. Preserve exact input and output at every stage.

## Evidence that is not sufficient

Multiple parsers, encoded delimiters, percent signs, nested JSON/URL data, double escaping, a polyglot-looking file, or differing display output is not sufficient. The layers may be intentional, the later grammar may keep the value inert, or final validation may cover the fully decoded object.

Do not assume that decoding twice is always unsafe or that one decoder call is always enough. Establish the format ownership and changed security decision.

## Investigation sequence

Build a stage ledger containing input bytes, grammar, decoder/parser, options, output type and bytes, validation decision, ownership, and consumer. Mark where delimiters, names, lengths, or object identities first change. Compare the representation covered by authorization, signing, caching, filtering, or bounds checks with the representation used for the final operation.

At binary level, follow buffers and lengths across each transform, including in-place decoders, string builders, native/managed transitions, and reparsing. Confirm whether a later API decodes internally instead of counting only visible helper calls.

## Constructed repeated URI-decoding example

```text
once = percent_decode(raw_path)
if contains_parent_segment(once):
    reject()
twice = percent_decode(once)
open_joined_path(root, twice)
```

For `raw_path` containing `%252e%252e%252fsecret`, one decode produces `%2e%2e%2fsecret`, which need not contain a literal parent segment, while the second produces `../secret`. The finding requires these exact decoding stages, a validator that misses the encoded form, and a filesystem resolution that can escape the intended root. If the second decode belongs to a deliberately encoded inner URI and the final resolved path is checked, the conclusion changes.

## Constructed x86-64 stage shape

```asm
; Illustrative System V AMD64 shape. r12 = mutable path buffer.
mov     rdi, r12
call    percent_decode_in_place
mov     rdi, r12
call    contains_parent_segment
test    eax, eax
jnz     .reject
mov     rdi, r12
call    percent_decode_in_place ; later transform occurs after the security check
mov     rdi, r12
call    open_selected_path
```

The call order identifies a possible check/use mismatch; it does not prove the two decoders operate on the same representation, that `%2e` is accepted, or that the final path escapes. Recover lengths, decoder contracts, return handling, and filesystem resolution.

## Primitive and impact limits

The direct primitive is introduction of syntax, delimiters, or object identity after the relevant check. Consequences can include path or authorization bypass, command/query/markup injection, request smuggling, signature mismatch, wrong-object access, or parser-bound memory errors. Impact belongs to the final reachable consumer and its authority, not merely to the existence of layered decoding.

## Related knowledge and primary sources

`reference-parser-framing-normalization-differences`, `reference-parser-escaping-nul-url-layers`, canonicalization profiles, and consumer-specific injection profiles provide the individual grammar contracts. This profile repeats transformation ownership and final-object validation locally.

Reviewed 2026-10-09 against [RFC 3986 sections 2.2-2.4](https://www.rfc-editor.org/rfc/rfc3986.html) for URI component and percent-decoding order, [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html) for JSON string encoding, and the WHATWG [URL Standard](https://url.spec.whatwg.org/) for a distinct browser-oriented URL parser. The source and assembly are constructed.
