---
id: vulnerability-integer-underflow-range-calculation
title: Integer underflow in remaining-length and index calculations
kind: vulnerability
topics: [integer-underflow, unsigned-wraparound, bounds, remaining-length, indexes]
platforms: [cross-platform]
architectures: [any]
---

# Integer underflow in remaining-length and index calculations

## Definition and violated invariant

Integer underflow occurs when subtraction produces a mathematical result below the type's minimum and the program consumes the resulting wrapped, undefined, or exceptional value. For an unsigned buffer extent `total`, computing `total-offset` is a valid remaining length only after proving `offset <= total`.

The underflow is distinct from an under-read: it often creates an incorrectly large remaining count that later permits a separate out-of-bounds access.

## Conditions that establish the issue

Recover subtraction width and signedness, operand units, accepted input domain, and every consumer. Prove a feasible `offset > total` or analogous state reaches the subtraction and that the underflowed result passes validation or controls an unsafe operation.

For signed arithmetic, account for source-language undefined or exceptional cases rather than assuming unsigned modulo behavior. For machine analysis, recover borrow/carry interpretation for the actual architecture.

## Evidence that is not sufficient

A subtraction, negative-looking decompiler value, or unsigned variable is not sufficient. A preceding comparison may prove operand order, the result may be used only under a branch that excludes underflow, or modular subtraction may be the intended counter contract.

An underflowed count that is rejected by allocation or API limits before access does not establish memory corruption.

## Investigation sequence

Find the subtraction and walk backward to all definitions and guards. Express the required order relation before evaluating the remainder. Follow the exact result through conversions, comparisons, allocation, pointer arithmetic, and copy or loop counts.

At instruction level, note operand order, width, and the branch condition consuming flags. A later unsigned comparison against the wrapped result can appear to provide a strong bound while admitting almost every length.

## Constructed source and assembly example

This hypothetical check subtracts before establishing that the offset is within the buffer:

```c
int read_part(const uint8_t *buffer, size_t total,
              size_t offset, size_t length)
{
    size_t remaining = total - offset;
    if (length > remaining)
        return -1;
    return consume(buffer + offset, length);
}
```

For a 64-bit `size_t`, `total == 16` and `offset == 32` produce a wrapped `remaining` near the maximum, so an ordinary small `length` passes. A matching fragment is `mov rax,total; sub rax,offset; cmp length,rax; ja reject`; an adequate `offset > total` rejection before `SUB` would refute it.

## Primitive and impact limits

The direct primitive is an invalid arithmetic bound. The later pointer formation or access must be assessed separately for out-of-bounds read, write, fault, or rejection.

Availability, disclosure, or execution depends on the consumer, mappings, controllability, and subsequent use. Underflow alone does not identify severity.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` defines subtraction prerequisites and mixed signedness. This profile repeats the operand-order proof needed for isolated review.

Reviewed 2026-10-09 against [MITRE CWE-191](https://cwe.mitre.org/data/definitions/191.html), C integer rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and C++ [integral conversions](https://eel.is/c++draft/conv.integral). The source, values, and instruction fragment are constructed.
