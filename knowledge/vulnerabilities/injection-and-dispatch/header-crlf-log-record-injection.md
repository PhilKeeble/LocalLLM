---
id: vulnerability-injection-header-crlf-log-record
title: HTTP, mail-header, or log-record injection
kind: vulnerability
topics: [injection, http, headers, crlf, email, logs, framing]
platforms: [cross-platform]
architectures: [any]
---

# HTTP, mail-header, or log-record injection

## Definition and violated invariant

Header or record injection occurs when attacker-controlled data introduces delimiters or syntax that a downstream HTTP, mail, log, or other line/record parser treats as additional fields, messages, recipients, commands, or records. A value must remain one value under the exact serialization and framing grammar used by every downstream consumer.

CR and LF are not universal record rules. HTTP versions, mail formats, syslog transports, newline-delimited files, structured logs, and vendor protocols frame data differently. A library may reject invalid field values or serialize them safely; raw concatenation and a visible newline do not establish the downstream interpretation.

## Conditions that establish the issue

Recover input decoding, field-name and value validation, serialization API, protocol version, delimiter bytes, line folding or continuation rules, proxy or relay normalization, transport framing, log encoder, downstream parser, and security-relevant effect. Prove attacker bytes survive to a consumer and create or alter a field, message boundary, recipient, command, or trusted record attribute.

For logs, identify how events are separated and parsed, whether structured fields are authenticated, and which alerting, audit, or automation decision changes. A forged display line without a trusted consumer effect has narrower impact.

## Evidence that is not sufficient

CR/LF in input, string concatenation, a header API, malformed response, extra displayed log line, or parser rejection is not sufficient. The framework may reject controls, the transport may use independent length framing, the consumer may escape newlines, or the inserted record may be visibly untrusted and ignored.

HTTP request/response splitting, mail recipient injection, and log forgery require different grammars and consequences. Do not transfer one protocol's delimiter rule to another.

## Investigation sequence

Capture the value before validation, serialized bytes on the relevant boundary, and downstream parse result. Mark decoding, canonicalization, field folding, line-ending normalization, proxy relaying, and reserialization. Compare the producer's intended one-field structure with every consumer's actual parsed structure.

Trace resulting cache, routing, recipient, authentication, alert, audit, or automation behavior. At binary level, distinguish structured setter APIs from raw buffer construction and confirm their return/error paths.

## Constructed raw HTTP/1.1 header example

```c
byte_buffer response = bytes("HTTP/1.1 200 OK\r\nX-Label: ");
response.append(submitted_label, submitted_length);
response.append(bytes("\r\nContent-Length: 0\r\n\r\n"));
send_all(socket, response);
```

If `submitted_label` contains CRLF followed by field syntax and no layer rejects it, an HTTP/1.1 recipient can parse an additional field rather than one `X-Label` value. The finding requires exact emitted bytes and recipient behavior; HTTP/2 and HTTP/3 use different framing, and a framework field setter may reject these bytes.

## Constructed line-log example

```text
write_log("user=" + submitted_name + " action=login result=denied\n")
```

If the log format uses newline as its record boundary, an embedded newline can create another apparent record. Security impact requires a consumer that trusts attacker-controlled fields or records for audit, alerting, attribution, or automation; confusing a human-readable display alone does not prove an authorization or execution effect.

## Primitive and impact limits

The direct primitive is creation or alteration of downstream fields, messages, recipients, or records. Consequences can include response/request splitting, cache or routing confusion, mail recipient/header changes, audit-trail ambiguity, false alerts, or automation input. Code execution requires a downstream interpreter or privileged automation path that consumes the injected structure.

## Related knowledge and primary sources

Framing, parser-differential, proxy, and protocol references provide supporting detail. This profile keeps producer bytes, downstream grammar, and effect as required evidence.

Reviewed 2026-10-09 against [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) for HTTP field semantics, [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html) for HTTP/1.1 message syntax and parsing, [RFC 5322](https://www.rfc-editor.org/rfc/rfc5322.html) for Internet message format, and [RFC 5424](https://www.rfc-editor.org/rfc/rfc5424.html) for one structured syslog message format. The examples are constructed; no universal log framing is assumed.
