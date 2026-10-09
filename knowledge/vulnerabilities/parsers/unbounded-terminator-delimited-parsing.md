---
id: vulnerability-parser-unbounded-terminator-delimited-parsing
title: Terminator-delimited parsing without a proven bounded terminator
kind: vulnerability
topics: [parsers, strings, terminators, bounds, nul]
platforms: [cross-platform]
architectures: [any]
---

# Terminator-delimited parsing without a proven bounded terminator

## Definition and violated invariant

A terminator-delimited parsing vulnerability occurs when a consumer scans for NUL, newline, delimiter, sentinel or end marker without proving that a valid terminator occurs within the permitted input range. The scan and every later terminated-string consumer must remain bounded by the same object or protocol field.

Allocation beyond the logical input and a coincidental zero byte do not establish a valid terminator. Counted and terminated representations can also disagree even when the scan stays mapped.

## Conditions that establish the issue

Recover the scan start, permitted extent, terminator width and encoding, escape or quoting rules, scanning API or loop, maximum examined address, and later consumer. Prove a reachable input lacks an eligible terminator in range and the scan crosses the boundary or selects a different logical value than validation.

For multibyte encodings and structured formats, establish parser state: a byte equal to the delimiter inside escaped or length-delimited data may not terminate the field.

## Evidence that is not sufficient

A string API, `strlen` import, delimiter loop, buffer lacking a terminator in a file view, or embedded NUL is not sufficient. The caller may append a sentinel in owned capacity, a prior bounded search may prove it, the API may accept an explicit maximum, or the input format may reject the value before use.

An embedded terminator is a representation mismatch only when different components consume different prefixes or suffixes in a security-relevant decision.

## Investigation sequence

Track available bytes, initialized capacity and logical field extent separately. Follow the exact scan at machine level, including vectorized wide loads and page-boundary handling, until its bounded exit or first out-of-range access. Then compare the value used by validators, loggers, filesystem APIs and downstream parsers.

Account for delimiter fragmentation across receive buffers and for reset or compaction that invalidates retained scan state.

## Constructed C example

```c
const char *name = (const char *)(record + name_offset);
if (is_allowed_name(name))
    open_named_object(name);
```

If both functions expect a NUL-terminated string but the record supplies only a counted byte range with no NUL before its end, either call can scan into the next record or beyond the allocation. The finding requires proof that no caller-owned sentinel or bounded wrapper intervenes. If the validator is counted while the opener is terminated, an embedded NUL can instead make them authorize and use different names.

## Primitive and impact limits

The direct result can be out-of-bounds read, disclosure, fault, record confusion, or check/use identity mismatch. Further impact depends on how the resulting bytes control allocation, path resolution, authorization or dispatch.

## Related knowledge and primary sources

`reference-native-strings-copy-format` and `reference-parser-escaping-nul-url-layers` cover terminated storage and decoded NUL boundaries. This profile repeats terminator eligibility, bounded extent and consumer agreement locally.

Reviewed 2026-10-09 against the C [string function contracts](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), JSON [string escaping](https://www.rfc-editor.org/rfc/rfc8259.html), and [MITRE CWE-170](https://cwe.mitre.org/data/definitions/170.html). The source is constructed.
