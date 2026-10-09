---
id: vulnerability-integer-allocation-size-overflow
title: Allocation-size overflow producing an undersized object
kind: vulnerability
topics: [integer-overflow, allocation-size, buffer-sizing, memory-safety]
platforms: [cross-platform]
architectures: [any]
---

# Allocation-size overflow producing an undersized object

## Definition and violated invariant

Allocation-size overflow occurs when arithmetic or conversion produces a smaller allocation request than the logical object count requires, while later code accesses the allocation using the larger count or extent. For `count` elements of `element_size` bytes, the required product and all added headers, alignment and terminators must be representable in the arithmetic domain used before allocation.

The integer error is the root cause; an out-of-bounds read or write is a later consequence only when execution reaches an access beyond the allocated object. A wrapped value that is rejected, cannot allocate, or is used consistently within a deliberately reduced domain does not establish the memory-corruption chain.

## Conditions that establish the issue

Identify the attacker-influenced count, every operand type and promotion, the value actually passed to the allocator, the returned allocation, and a later access calculated from a larger or differently interpreted value. Prove a feasible input for which the required size is not representable or is narrowed, yet allocation succeeds and later processing continues.

For unsigned values with maximum `MAX`, `count * element_size` is representable when `element_size == 0` or `count <= MAX / element_size`. Addition of `extra` bytes requires `extra <= MAX - base`. Apply the formula in the actual promoted width; assigning a wrapped result to a wider allocation parameter does not restore lost high bits.

## Evidence that is not sufficient

A multiply before an allocator call, a shift used for structure scaling, a 32-bit operand in a 64-bit function, or a missing checked-arithmetic helper is not sufficient. Protocol limits or earlier comparisons may prove the product safe, an instruction may execute in a wider domain than the decompiler type suggests, or all later consumers may intentionally use the same narrowed value.

Allocation failure is also not proof of safety unless every relevant allocator and zero-size result stops the path. Confirm that error handling prevents later accesses and does not retain a stale pointer or inconsistent logical count.

## Investigation sequence

Trace the count from decoding through validation, casts, arithmetic, alignment, allocation and every later loop or copy. Record width, signedness and units at each edge. In assembly, distinguish operations on a 32-bit subregister, which can discard high bits, from 64-bit operations; locate zero/sign extension relative to the multiply or shift.

Compare the successful allocation request with the maximum byte range later addressed. Check boundary values around the first overflowing count and ensure those values survive the input representation. Treat signed overflow according to the source-language contract and recover emitted machine behavior separately when optimization or decompiler types are uncertain.

## Constructed source example

This hypothetical C path deliberately performs the size product in `uint32_t` before converting it to `size_t`:

```c
struct item { uint64_t first, second; };

int build_items(uint32_t count)
{
    uint32_t bytes32 = count * (uint32_t)sizeof(struct item);
    struct item *items = malloc((size_t)bytes32);
    if (items == NULL)
        return -1;
    for (uint32_t i = 0; i < count; ++i)
        initialize_item(&items[i]);
    consume_items(items, count);
    free(items);
    return 0;
}
```

With 16-byte items, `count = 0x10000001` makes the 32-bit product wrap to 16 while the loop retains the original count. The concrete corruption still requires allocation success and progress to an index whose 16-byte range exceeds the object. A dominating maximum-count check would refute the constructed path.

## Constructed Windows x64 representation

This abbreviated Windows x64 sequence matches the constructed one-argument function, so `count` arrives in `ECX`. An omitted prologue preserves the nonvolatile registers used below:

```asm
mov  ebx, ecx             ; RBX = original count, zero-extended
shl  ecx, 4               ; 32-bit count * 16, high bits discarded
call malloc               ; RCX carries the zero-extended wrapped size
test rax, rax
je   allocation_failed
mov  rdi, rax             ; allocation base
xor  esi, esi             ; i = 0
loop_items:
mov  rax, rsi
shl  rax, 4               ; later offset computed in 64 bits
lea  rcx, [rdi+rax]
call initialize_item
inc  rsi
cmp  rsi, rbx
jb   loop_items
```

Writing `ECX` zero-extends into `RCX` on x86-64, so the allocator receives the wrapped 32-bit result. The later 64-bit scale preserves a larger offset. Confirm the real ABI, operand widths, loop reachability, allocation check and helper write contract; the instruction pattern alone is not a vulnerability signature.

## Primitive and impact limits

The direct primitive is an undersized live allocation paired with a larger logical access domain. Classify each resulting access separately as out-of-bounds read or write and record the first violating index. A huge loop may cause resource exhaustion or a fault before useful corruption; it does not automatically provide controlled heap overwrite.

Claims of disclosure, arbitrary write or code execution require evidence about accessed direction, controlled values, allocator placement, subsequent use and mitigations. Keep the arithmetic root cause visible even when the observed crash occurs later in a copy, constructor or allocator routine.

## Related knowledge and primary sources

`reference-native-integer-size-buffer-arithmetic` supplies the full conversion and checked-formula contract, while `reference-native-bounds-objects-terminators` supplies the later object-range proof. This profile repeats the decisive allocation/use mismatch so it can be interpreted without following those links.

Reviewed 2026-10-09 against [MITRE CWE-190](https://cwe.mitre.org/data/definitions/190.html), [MITRE CWE-131](https://cwe.mitre.org/data/definitions/131.html), the C integer rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), the C++ rules for [integral conversions](https://eel.is/c++draft/conv.integral) and [usual arithmetic conversions](https://eel.is/c++draft/expr.arith.conv), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The numeric case and assembly are constructed examples.
