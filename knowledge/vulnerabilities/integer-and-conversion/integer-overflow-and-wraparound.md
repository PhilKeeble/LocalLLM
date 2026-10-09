---
id: vulnerability-integer-overflow-wraparound
title: Integer overflow and wraparound in security-relevant arithmetic
kind: vulnerability
topics: [integer-overflow, wraparound, arithmetic, quotas, sizes]
platforms: [cross-platform]
architectures: [any]
---

# Integer overflow and wraparound in security-relevant arithmetic

## Definition and violated invariant

Integer overflow occurs when a mathematical result is outside the representable range of the operation's type. Unsigned C and C++ arithmetic is reduced modulo one more than the maximum value; signed overflow is undefined behavior. Addition, multiplication, and alignment must be representable before their result controls a size, offset, quota, state transition, or security decision.

The arithmetic defect is a root cause. Report a later undersized allocation, out-of-bounds access, quota bypass, or state error only after tracing the wrapped or otherwise undefined result into that effect.

## Conditions that establish the issue

Recover operand widths, signedness, promotions, constants, and the value consumed after the operation. Prove feasible inputs whose mathematical result is out of range and a path on which the resulting machine or compiled behavior reaches a security-relevant consumer. A wider destination does not recover bits lost in a narrower operation.

For unsigned maximum `MAX`, addition `a+b` is representable when `b <= MAX-a`; multiplication `a*b` is representable when `b == 0` or `a <= MAX/b`. Align-up addition needs the same proof before masking.

## Evidence that is not sufficient

An `ADD`, `IMUL`, shift, missing overflow flag branch, or large attacker-controlled value is not sufficient. Earlier bounds may prove the operation safe, the instruction may execute at a wider width than the decompiler suggests, or the result may be deliberately modular and never used outside that domain.

Do not assign deterministic wrapping semantics to signed source overflow merely because a particular instruction wraps. Recover compiler assumptions and analyze the emitted binary separately.

## Investigation sequence

Trace the value from input through promotions, arithmetic, casts, storage, and every consumer. Calculate the first mathematical boundary and verify it survives the field or API representation. Inspect instruction operand width and extension order, then identify whether flags are consumed before another instruction overwrites them.

For each resulting discrepancy, compare the value used by validation with the value used by allocation, iteration, accounting, or dispatch. Keep resource affordability separate from integer representability.

## Constructed source and assembly example

This hypothetical unsigned quota check validates a wrapped sum:

```c
bool reserve(uint32_t used, uint32_t requested, uint32_t limit)
{
    uint32_t after = used + requested;
    if (after > limit)
        return false;
    commit_reservation(requested);
    return true;
}
```

With `used == 0xfffffff0`, `requested == 0x30`, and `limit == 0x1000`, the 32-bit sum becomes `0x20` and passes. Under Windows x64 those three arguments arrive in `ECX`, `EDX`, and `R8D`, so a matching fragment is `mov eax, ecx; add eax, edx; cmp eax, r8d; ja reject`; absence of a carry check matters only after the parameter mapping and reachable values are established.

## Primitive and impact limits

The direct primitive is a misrepresented arithmetic result. Its consequence may be an accounting bypass, undersized object, incorrect loop bound, wrong state, or denial of service. State the first consumer that violates its contract.

Code execution or privilege escalation requires a further controllable memory or authority chain. A harmless modular counter or rejected overflow has no such implication.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` supplies promotion and checked-formula detail. This profile repeats the representability and consumer requirements needed in isolation.

Reviewed 2026-10-09 against [MITRE CWE-190](https://cwe.mitre.org/data/definitions/190.html), C arithmetic in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [usual arithmetic conversions](https://eel.is/c++draft/expr.arith.conv), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The numeric case and instruction fragment are constructed.
