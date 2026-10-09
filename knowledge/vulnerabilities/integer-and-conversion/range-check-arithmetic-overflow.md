---
id: vulnerability-integer-range-check-arithmetic-overflow
title: Overflow inside a range or alignment check
kind: vulnerability
topics: [integer-overflow, bounds, ranges, alignment, validation]
platforms: [cross-platform]
architectures: [any]
---

# Overflow inside a range or alignment check

## Definition and violated invariant

A range-check-overflow vulnerability occurs when the expression intended to prove a range fits can itself wrap, overflow, or lose information. For nonnegative offsets in one representable unsigned domain, validate `offset <= total` and then `length <= total-offset`; evaluating `offset+length <= total` first can accept a wrapped sum.

Power-of-two align-up `(value + alignment - 1) & ~(alignment - 1)` likewise requires a checked addition and a proven nonzero power-of-two alignment. A successful comparison is meaningful only when its operands represent the mathematical values required by the access.

## Conditions that establish the issue

Recover every operand width, signedness, unit, promotion, and conversion in the check and later use. Prove feasible values make the check expression differ from the mathematical range while the access or allocation still uses the larger original components.

Confirm that no earlier bound proves the addition or align-up representable. A check in a wider domain can be adequate even when later addresses use a narrower target only if conversion is also proven safe.

## Evidence that is not sufficient

An addition in a condition, `LEA` before `CMP`, or lack of a carry branch is not sufficient. Operand bounds may exclude wrap, compiler transformations may implement a subtraction-equivalent proof, or the result may be wider than displayed by the decompiler.

Do not treat a rejected wrapped result as an exploitable path; follow the actual branch and consumed values.

## Investigation sequence

Rewrite the intended access as a half-open range and the implemented predicate as exact-width arithmetic. Compare them at zero, endpoints, and the first wrapping values that the input can encode. Trace whether validation and use share the same snapshot and units.

In assembly, identify the instruction setting flags, the branch's signedness, and intervening flag-clobbering instructions. For align-up, verify the alignment predicate and every added header, trailer, and padding contribution.

## Constructed source and Windows x64 example

```c
int consume_range(const uint8_t *buffer, size_t total,
                  size_t offset, size_t length)
{
    if (offset + length > total)
        return -1;
    return consume(buffer + offset, length);
}
```

Under Windows x64 the arguments are `RCX`, `RDX`, `R8`, and `R9`; a matching fragment is `lea rax,[r8+r9]; cmp rax,rdx; ja reject; lea rcx,[rcx+r8]; mov rdx,r9; call consume`. If `offset+length` wraps below `total`, the guard accepts while the original offset and length drive use. Earlier representability checks would refute the example.

## Primitive and impact limits

The direct primitive is a false range proof. The subsequent effect may be an out-of-bounds access, undersized allocation, wrong aligned extent, or logical bypass; identify it independently.

Strong impact requires reachable attacker control and a useful read, write, or authority consequence. A fault or downstream rejection may limit the result to denial of service or no effect.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` defines subtraction and alignment prerequisites. This profile repeats the safe range relation needed alone.

Reviewed 2026-10-09 against [MITRE CWE-190](https://cwe.mitre.org/data/definitions/190.html), [MITRE CWE-131](https://cwe.mitre.org/data/definitions/131.html), C rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
