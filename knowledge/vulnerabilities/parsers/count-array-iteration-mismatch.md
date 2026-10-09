---
id: vulnerability-parser-count-array-iteration-mismatch
title: Count, array-size, and attacker-controlled iteration mismatch
kind: vulnerability
topics: [parsers, counts, arrays, loops, bounds, allocation]
platforms: [cross-platform]
architectures: [any]
---

# Count, array-size, and attacker-controlled iteration mismatch

## Definition and violated invariant

A count/array mismatch occurs when a decoded element count, byte length, allocated capacity, initialized element total and loop bound do not describe the same collection. Every iteration must address a complete element inside the validated encoded range and any destination allocation, using the correct element size and variable-length decoding rules.

An element count is not a byte count. Native `sizeof(T)` is not an encoded stride unless the format and implementation establish that layout, and variable-length elements require per-element boundary recovery.

## Conditions that establish the issue

Recover count encoding and width, element grammar and stride, multiplication and rounding, available payload bytes, allocation capacity, initialized elements, loop comparison and increment, and all early exits. Prove a feasible attacker-controlled count causes an iteration to read or write beyond the validated collection, consume an incomplete element, or perform security-relevant unbounded work.

Check disagreement among duplicate counts or lengths and determine which value each stage uses. A safe allocation multiplication does not prove the input contains that many elements, and sufficient input does not prove the destination has matching capacity.

## Evidence that is not sufficient

An attacker-controlled loop bound, large count, multiplication, flexible array, or loop lacking a local bounds check is not sufficient. A dominating verifier, fixed protocol maximum, iterator end condition, checked decoder, or bounded downstream API may constrain it.

A count that causes rejection or resource use within an intentional documented limit is not automatically a vulnerability.

## Investigation sequence

Create a ledger for encoded count, decoded count, bytes available, element width or decoder, allocation bytes, constructed elements and iterations completed. Preserve arithmetic widths and signedness through conversions. For variable-size elements, advance a checked cursor and record consumed bytes per element.

At machine level, recover loop compare, induction variable, scale and access width. Verify every exit and error path, including whether partially constructed arrays are later treated as complete.

## Constructed fixed-width example

```c
uint32_t count = read_u32(input);
const uint8_t *entries = input + 4;
for (uint32_t i = 0; i < count; ++i)
    consume_u64(load_u64(entries + (size_t)i * 8));
```

If the supplied extent is only twelve bytes, it contains the count plus one complete eight-byte element. A count of four drives later iterations beyond that input unless a dominating check proves at least `4 + count*8` bytes with checked arithmetic. The loop is not vulnerable merely because `count` is untrusted when an earlier verifier establishes the required span.

## Primitive and impact limits

The direct result can be out-of-bounds read or write, use of uninitialized elements, excessive work, partial-object confusion, or allocation/iteration disagreement. Impact depends on the consumer, destination and attacker control over adjacent data.

## Related knowledge and primary sources

`reference-parser-wire-fields-lengths-tags`, `reference-parser-container-boundaries-integrity`, and native integer-size references cover count and span recovery. This profile repeats the full collection ledger locally.

Reviewed 2026-10-09 against XDR [array and variable-length encoding](https://www.rfc-editor.org/rfc/rfc4506.html), Protocol Buffers [encoding rules](https://protobuf.dev/programming-guides/encoding/), and [MITRE CWE-130](https://cwe.mitre.org/data/definitions/130.html). The source and extent example are constructed.
