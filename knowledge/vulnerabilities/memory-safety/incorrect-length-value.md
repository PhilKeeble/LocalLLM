---
id: vulnerability-memory-incorrect-length-value
title: Incorrect length value across byte, element, and capacity domains
kind: vulnerability
topics: [memory-safety, length, units, buffer-sizing, bounds]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect length value across byte, element, and capacity domains

## Definition and violated invariant

An incorrect-length vulnerability occurs when validation or an operation interprets a length in a different unit, representation, or object domain from the consumer. Every access must fit both its source and destination objects after converting counts such as elements, bytes, code units, rows, planes, encoded bytes, and decoded bytes into the consumer's unit with representable arithmetic.

The defect is the inconsistent length contract. Classify the resulting access separately as an out-of-bounds read or write; a unit mismatch that is rejected before access or whose accepted values remain within both objects does not establish memory corruption.

## Conditions that establish the issue

Identify the value's producer, declared unit, validation unit, API parameter unit, and final access width. Prove a feasible value that passes the check but causes the operation's full source or destination range to exceed the corresponding live object. For multiple image planes, segments, or records, prove the per-part extent and the checked total rather than assuming one advertised length covers every part.

Keep source availability distinct from destination capacity. A correct destination bound does not prove that a copy can read its requested count from the source, and an encoded input length does not by itself bound decoded or converted output.

## Evidence that is not sufficient

Different parameter names, a multiply near a copy, or a byte-oriented instruction operating on typed data is not sufficient. An earlier range restriction may make the conversion safe, the parameter may intentionally describe payload capacity rather than total object size, or a wrapper may convert the units before the observed call.

A decompiler's type and inferred array length are hypotheses. Recover API contracts, structure fields, allocation extents, operand widths, and the value actually passed at the call site.

## Investigation sequence

Build a ledger for each length containing origin, numeric width, signedness, unit, represented object, and whether it includes headers, padding, or terminators. Follow it through validation, scaling, narrowing, allocation, and use. For each copy or loop, calculate the complete source and destination byte ranges with overflow checked before multiplication or addition.

In assembly, locate scaling instructions and determine whether comparison happens before or after scaling. Verify calling convention registers, extension behavior, and whether a wrapper changes the value. Inspect boundary cases around the largest accepted count only after confirming those values are representable in the input format.

## Constructed source example

This hypothetical function compares a count of 16-bit elements with a destination capacity expressed in bytes:

```c
int copy_words(uint16_t *destination, size_t destination_bytes,
               const uint16_t *source, size_t word_count)
{
    if (word_count > destination_bytes)
        return -1;
    memcpy(destination, source, word_count * sizeof(uint16_t));
    return 0;
}
```

With a 16-byte destination and `word_count == 12`, the check accepts the request but `memcpy` writes 24 bytes. The example also requires a readable 24-byte source and a representable product; a dominating limit of at most eight words would refute the destination overrun.

## Constructed Windows x64 representation

Under Windows x64 the constructed arguments arrive as destination `RCX`, destination bytes `RDX`, source `R8`, and word count `R9`. This abbreviated sequence assumes the product is representable and omits normal call-frame preservation:

```asm
cmp  r9, rdx
ja   reject               ; compares elements with bytes
mov  rdx, r8              ; memcpy source
shl  r9, 1                ; word count becomes byte count
mov  r8, r9               ; memcpy byte count
call memcpy               ; destination remains in RCX
```

The comparison accepts 12 against 16 before the later scale produces 24. Confirm the recovered parameter meanings and object sizes; `SHL` before a byte-domain comparison or a prior eight-word limit would change the conclusion.

## Primitive and impact limits

The direct primitive is an access whose effective byte range exceeds the relevant source or destination because the controlling length described a different domain. Record the first invalid byte, direction, value control, adjacent state, and whether a fault occurs before any security-relevant effect.

Remote code execution, disclosure, or privilege escalation requires additional evidence about reachability, attacker control, layout, subsequent use, and mitigations. A wrong unit may instead cause rejection, truncation, a harmless logical error, or denial of service.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` defines representable scaling, and `reference-native-text-encoding-size-units` distinguishes encoded bytes, code units, and scalar values. This profile repeats the source/destination and consumer-unit proof needed for isolated use.

Reviewed 2026-10-09 against [MITRE CWE-130](https://cwe.mitre.org/data/definitions/130.html), [MITRE CWE-131](https://cwe.mitre.org/data/definitions/131.html), the C object and library rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
