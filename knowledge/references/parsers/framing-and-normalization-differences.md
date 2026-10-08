---
id: reference-parser-framing-normalization-differences
title: Framing, malformed-input handling and normalization disagreements
kind: reference
topics: [parsers, parser-differentials, http, message-framing, uri, normalization]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Framing and normalization disagreements

## HTTP/1.1 Transfer-Encoding and Content-Length precedence

For HTTP/1.1 requests containing both fields, RFC 9112 gives Transfer-Encoding
precedence and recommends error handling. A forwarding intermediary must remove
the received Content-Length and process Transfer-Encoding before forwarding. [1]

This is not a universal framing algorithm: response method/status exceptions
precede that rule. Do not apply request rules to HEAD responses or successful
CONNECT tunnel transitions. [1]

## HTTP/1.1 repeated lengths and incomplete bodies

In HTTP/1.1 requests without Transfer-Encoding, invalid Content-Length is an unrecoverable framing
error, except a successfully parsed list of identical valid values can supply
one length. A valid Content-Length is a byte count; premature EOF or
timeout makes that length-delimited message incomplete, not a shorter success. [1]

## HTTP/1.1 malformed bytes and parser disagreement

HTTP/1.1 framing operates on octets, not pre-decoded Unicode text. RFC 9112 warns
that differing handling of invalid multibyte sequences containing LF can create
security problems. It also warns that inconsistent leniency among recipients
can enable request smuggling: disagreement about request interpretation. [1]

These selected rules are investigation anchors, not the complete HTTP parser
specification. Custom code and HTTP-version translation require their own evidence.

## URI percent decoding can turn data into a delimiter

RFC 3986 requires separating relevant URI components before decoding reserved
octets inside them. Decoding an unreserved character is different: its escaped
and literal forms are equivalent. Unreserved characters are ASCII letters,
digits, hyphen, period, underscore and tilde. [2]

Investigative inference: identify whether a slash is still encoded data when
authorization runs but becomes a path separator during resolution. The answer
depends on the actual URI scheme and consumer; this is not a universal filesystem
path-normalization rule. See reference-logic-authorization-object-binding.

## Repeated URI decoding is not harmless normalization

RFC 3986 warns against percent-decoding the same string more than once because
a decoded percent sign can be reinterpreted as another escape introducer. [2]

Constructed decoding example: one pass transforms `%252F` into `%2F`; another
transforms it into `/`. Establish actual transformation order and which form is
checked versus consumed. Separately encoded outer and inner formats can legitimately
need their own decoding stages; counting decoder calls alone does not prove a bug.
JSON escapes, decoded NULs, form plus handling and WHATWG URL separators have
separate scoped rules in `reference-parser-escaping-nul-url-layers`.

## Interpretation disagreement needs a security-relevant consequence

Analytical distinction: parser A accepting bytes that parser B rejects can be a
compatibility difference. To establish a vulnerability, connect a caller-controlled
representation to a violated bound, authority decision, object identity or state
transition. Neither format nonconformance nor disagreement alone establishes that.

For malware analysis, an analyst's decoder rejecting data does not establish that
the target rejects it; accepting data does not establish that the target uses it.
Recover the target's selected value, branch and resulting operation. Decoder
differences are leads, not proof of concealment intent or malicious execution.

## Primary sources and related references

Reviewed 2026-10-02. RFC 9112 (2022) covers HTTP/1.1, not HTTP/2 or HTTP/3 framing.
RFC 3986 (2005) provides URI generic syntax, not every URL library or OS path API.
Use reference-parser-duplicate-fields-decoded-values for duplicate-value rules;
playbook-re-parser-differentials for comparing actual components.

1. [RFC 9112 §§2.2, 6.3, 11.2: parsing, framing precedence and request smuggling](https://www.rfc-editor.org/rfc/rfc9112.html).
2. [RFC 3986 §§2.2-2.4: reserved characters and decoding order](https://www.rfc-editor.org/rfc/rfc3986.html).
