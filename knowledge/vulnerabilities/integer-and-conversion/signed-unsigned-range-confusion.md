---
id: vulnerability-integer-signed-unsigned-range-confusion
title: Signed and unsigned range confusion
kind: vulnerability
topics: [integers, signedness, comparisons, conversions, bounds]
platforms: [cross-platform]
architectures: [any]
---

# Signed and unsigned range confusion

## Definition and violated invariant

Signed/unsigned confusion occurs when comparison or conversion changes the accepted numeric domain so validation and use do not constrain the same value. A negative signed count converted to an unsigned type becomes a large value modulo the destination range; mixed-type comparisons can convert the signed operand before comparison.

Signedness is a value interpretation, not a property recoverable from most register bits alone. Establish the source type or branch semantics and the consumer's domain before assigning the defect.

## Conditions that establish the issue

Recover original field or return type, promotions, comparison signedness, casts, ABI argument width, and the value consumed. Prove a feasible negative or high-bit-set value passes a check intended for nonnegative sizes or indexes and reaches an operation under a different interpretation.

Also consider documented negative sentinels. Rejecting or converting them is wrong only when it conflicts with the selected API contract and later use.

## Evidence that is not sufficient

A signed conditional branch, `MOVSX`, `MOVZX`, high bit, or negative decompiler display is not sufficient. The domain may legitimately be signed, a preceding lower-bound check may exclude negatives, or conversion may deliberately implement modulo behavior.

Do not infer the source declaration from one comparison; machine code can choose an equivalent branch after range analysis.

## Investigation sequence

Record each value as bit width, signed interpretation, unsigned interpretation, and unit at every edge. Apply language promotions at comparisons and arithmetic, then compare with emitted branch conditions. Follow the exact post-check representation into the consumer.

Inspect zero, one, signed maximum, first high-bit-set value, and negative sentinels only when the input or API can produce them. Keep decompiler casts provisional until callers and callees agree.

## Constructed source example

This hypothetical function compares a signed length against a signed capacity but converts the accepted length to `size_t` for copying:

```c
int copy_data(void *destination, const void *source,
              int32_t length, int32_t capacity)
{
    if (length > capacity)
        return -1;
    memcpy(destination, source, (size_t)length);
    return 0;
}
```

With nonnegative capacity and `length == -1`, the signed comparison accepts the value and conversion produces `SIZE_MAX` on a 64-bit target. A required `length < 0` rejection would prevent this path.

## Constructed Windows x64 representation

The arguments arrive as destination `RCX`, source `RDX`, length `R8D`, and capacity `R9D`:

```asm
cmp    r8d, r9d
jg     reject             ; signed comparison accepts negative length
movsxd r8, r8d            ; -1 becomes 0xffffffffffffffff
call   memcpy
```

The branch and extension jointly establish the constructed mismatch. Confirm the actual prototype and any lower-bound guard before relying on the decompiler's signed names.

## Primitive and impact limits

The direct primitive is inconsistent range interpretation. Consequences can include an oversized copy, invalid index, bypassed threshold, or error sentinel treated as data.

The consumer may reject the large unsigned value or fault without corruption. Stronger claims require the resulting operation and reachable effect.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` defines promotions and mixed comparisons, while `architecture-machine-representation` covers extension evidence. This profile repeats the accepted-domain mismatch locally.

Reviewed 2026-10-09 against [MITRE CWE-195](https://cwe.mitre.org/data/definitions/195.html), [MITRE CWE-196](https://cwe.mitre.org/data/definitions/196.html), C rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [usual arithmetic conversions](https://eel.is/c++draft/expr.arith.conv), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
