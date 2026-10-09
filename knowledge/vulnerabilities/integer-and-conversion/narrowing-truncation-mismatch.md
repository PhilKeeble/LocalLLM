---
id: vulnerability-integer-narrowing-truncation-mismatch
title: Narrowing truncation across storage and API boundaries
kind: vulnerability
topics: [integers, narrowing, truncation, fields, abi, lengths]
platforms: [cross-platform]
architectures: [any]
---

# Narrowing truncation across storage and API boundaries

## Definition and violated invariant

A narrowing vulnerability occurs when conversion to a smaller integer representation discards significant bits and validation, allocation, storage, or use later refers to a different representation of the same logical value. The required invariant is consistency: either the original value is representable in the destination or every consumer intentionally uses the narrowed domain under its stated contract.

Truncation alone is not a vulnerability. Protocol fields, masks, modular counters, and instruction results can deliberately retain low bits.

## Conditions that establish the issue

Recover source and destination widths, signedness, conversion rule, intended domain, and all consumers. Prove a feasible value changes on conversion and that one path validates or sizes with the narrowed value while another consumes the original or differently extended value in a security-relevant operation.

At ABI boundaries, determine whether the callee reads a narrow subregister, a full register with unspecified excess bits, or stack storage. Do not assume a decompiler cast matches the calling contract.

## Evidence that is not sufficient

A narrow store, low-register move, mask, or cast is not sufficient. An earlier range check may prove representability, all later uses may consume the narrowed value, or the high bits may be flags intentionally excluded from the payload.

An input that cannot be encoded in the original wire field is not a feasible boundary case for that path.

## Investigation sequence

Maintain original, converted, re-extended, and consumed values separately. Follow storage reloads, call arguments, validation, allocation, indexes, and copies. Compare the accepted original range with the destination type's exact range.

In assembly, distinguish writes to low registers and memory widths, then identify sign or zero extension on reload. Check whether the original wider value remains live in another register or object field.

## Constructed source and machine example

This hypothetical path sizes storage with a narrowed 16-bit length but copies using the original 32-bit value:

```c
int receive_item(const void *source, uint32_t length)
{
    uint16_t stored_length = (uint16_t)length;
    void *destination = malloc(stored_length);
    if (destination == NULL)
        return -1;
    memcpy(destination, source, length);
    return consume(destination, stored_length);
}
```

For `length == 65537`, `stored_length` is one while the copy count remains 65537. A binary may show `movzx allocation_arg, length_low16` for allocation and the preserved 32-bit original at the copy. Prove allocation success and lack of an earlier `length <= 65535` check.

## Primitive and impact limits

The direct primitive is disagreement between representations. It may create an undersized allocation, wrong selector, truncated object identity, or policy mismatch; classify the first concrete effect separately.

Code execution or disclosure requires a later controllable write or observable read. Consistent intentional narrowing has no such consequence.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` owns narrowing and representability, and `abi-data-models-api-types` covers platform widths. This profile repeats the cross-consumer mismatch needed in isolation.

Reviewed 2026-10-09 against [MITRE CWE-197](https://cwe.mitre.org/data/definitions/197.html), C conversions in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and C++ [integral conversions](https://eel.is/c++draft/conv.integral). The source and machine pattern are constructed.
