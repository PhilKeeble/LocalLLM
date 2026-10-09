---
id: vulnerability-integer-shift-division-edge-case
title: Shift, division, and exceptional arithmetic edge case
kind: vulnerability
topics: [integers, shifts, division, arithmetic, undefined-behavior]
platforms: [cross-platform]
architectures: [any]
---

# Shift, division, and exceptional arithmetic edge case

## Definition and violated invariant

An exceptional-arithmetic vulnerability occurs when a shift count, divisor, or signed division case lies outside the source language or selected runtime's valid domain and the result reaches a security-relevant consumer. In C and C++, a shift count must be nonnegative and less than the promoted left operand's width; integer division by zero is undefined, as is signed minimum divided by `-1` when the quotient is unrepresentable.

Machine instructions need not match source behavior. Some mask shift counts, some trap on division cases, and some architectures define nontrapping quotient values. Apply the actual ISA only to the binary and do not use it to retroactively legalize undefined source.

## Conditions that establish the issue

Recover operation width, signedness, count or divisor origin, accepted range, emitted instruction or helper, and consumer. Prove a feasible exceptional value reaches the operation and produces an unsafe result, unhandled trap, or security-state error under the target contract.

For shifts used as powers, masks, or sizes, also prove the mathematical result is representable and has the intended unit. A valid count can still discard significant bits.

## Evidence that is not sufficient

A variable shift, `DIV`, `IDIV`, helper call, or absent nearby zero check is not sufficient. Earlier bounds, protocol constraints, or dominating dispatch can exclude exceptional values, and a language runtime may define and handle them.

A compiler optimization based on undefined behavior requires a demonstrated reachable effect in the built artifact before assigning exploitability.

## Investigation sequence

Trace the count or divisor from input through promotions and narrowing. Check zero, operand width minus one, operand width, and signed minimum/`-1` where representable. Recover whether hardware masks the count or raises an exception and how that exception is handled.

Follow the result into allocation, indexing, bit selection, authorization, or control flow. Separate a deterministic process fault from an attacker-useful memory or policy primitive.

## Constructed source and x86 example

```c
uint32_t scale_from_field(uint32_t shift)
{
    return 1u << shift;
}
```

For `shift >= 32`, the C expression is outside its valid shift-count domain. A constructed x86 fragment `mov ecx, input; mov eax, 1; shl eax, cl` masks the count to five bits for a 32-bit operand, so input 32 produces one in that binary. A compiler may emit something else because the source path is undefined; analyze the actual instructions and consumer.

## Primitive and impact limits

The direct result may be a wrong numeric value or an arithmetic exception. Consequences include undersized resources, wrong masks or selectors, denial of service, or later memory errors.

Execution or privilege impact requires a demonstrated downstream chain. A handled exception or unused result has no stronger implication.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` covers language shift rules, and `architecture-x86-integer-instruction-evidence` covers x86 count masking and division faults. This profile repeats the language/ISA separation required alone.

Reviewed 2026-10-09 against C operators in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [shift operators](https://eel.is/c++draft/expr.shift) and [multiplicative operators](https://eel.is/c++draft/expr.mul), and Intel's [software developer manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html). The source and x86 fragment are constructed.
