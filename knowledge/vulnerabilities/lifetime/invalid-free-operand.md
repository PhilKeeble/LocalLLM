---
id: vulnerability-lifetime-invalid-free-operand
title: Invalid release of an interior, stack, static, foreign, or transferred pointer
kind: vulnerability
topics: [lifetime, invalid-free, ownership, interior-pointer, deallocation]
platforms: [cross-platform]
architectures: [any]
---

# Invalid release of an interior, stack, static, foreign, or transferred pointer

## Definition and violated invariant

An invalid-free vulnerability passes a value to a deallocator even though that value is not a currently owned release operand under the selected allocation contract. Examples include interior pointers, automatic or static storage, foreign-runtime memory, a borrowed pointer, or an allocation whose ownership was already transferred.

The valid operand is deallocator-specific. Ordinary C `free` requires a null pointer or the value returned by a compatible allocation function that has not already been freed. C++ deletion has additional object, array, base-subobject, dynamic-type, and deallocation-selection rules, so not every adjusted base pointer is invalid.

## Conditions that establish the issue

Recover allocation origin, returned base, object type, ownership transitions, pointer adjustments, and exact deallocator. Prove the value reaching release does not satisfy that contract on a feasible path. For handles or FFI resources, identify the provider's matching release function and whether the caller owns a release obligation.

Separate invalid release from a later allocator failure. The release call is the violated operation even if diagnostics appear only on a subsequent allocation.

## Evidence that is not sufficient

A nonzero pointer offset, stack-looking address, custom wrapper, or different function name is not sufficient. C++ deletion through an appropriate base can be valid, an exported release wrapper can own a foreign object, and a pointer may have been adjusted back to its allocation base before the call.

An allocator rejecting the operand can contain the issue; it does not prove heap metadata was modified.

## Investigation sequence

Trace the value from acquisition through casts, field or element addressing, container extraction, ownership transfer, and release. Maintain allocation base and logical object pointers separately. Resolve imported, inlined, or virtual deallocation behavior rather than trusting a guessed function name.

At assembly level, calculate the exact release operand and compare it with the recorded returned base. Then inspect provider identity, array/single-object form, and dynamic deletion rules where applicable.

## Constructed source and Windows x64 representation

```c
void discard_payload(void)
{
    uint8_t *base = malloc(64);
    if (base != NULL)
        free(base + 16);
}
```

The argument is an interior pointer rather than the value returned by `malloc`. Under Windows x64 a matching call site can show `call malloc; test rax,rax; je done; lea rcx,[rax+10h]; call free`. Confirm the allocator call really returns the base and that the release target is ordinary compatible `free`, not a custom suballocation API.

## Primitive and impact limits

The direct primitive is an invalid deallocation request. Results can include immediate rejection, process termination, allocator-state corruption, or release of the wrong foreign resource. Stronger exploitation claims require the actual allocator behavior and controllable follow-on operations.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling` supplies C and C++ release contracts. This profile repeats the provenance and exact-operand requirements needed alone.

Reviewed 2026-10-09 against [MITRE CWE-590](https://cwe.mitre.org/data/definitions/590.html), C [`free`](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [delete expressions](https://eel.is/c++draft/expr.delete), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The example and assembly are constructed.
