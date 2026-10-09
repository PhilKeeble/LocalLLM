---
id: vulnerability-type-pointer-handle-scalar-confusion
title: Pointer, integer, handle, and scalar representation confusion
kind: vulnerability
topics: [type-confusion, pointers, handles, integers, representations, truncation]
platforms: [cross-platform]
architectures: [any]
---

# Pointer, integer, handle, and scalar representation confusion

## Definition and violated invariant

Representation confusion occurs when a scalar, integer ID, offset, opaque handle, encoded fixup, or pointer is consumed as another category without the required decoding, width preservation, address-space selection, or object validation. Pointer-sized storage does not make an opaque handle dereferenceable, and an integer resembling a mapped address does not establish a live object.

Legitimate pointer-integer round trips and tagged or relative pointer schemes are language-, ABI-, and runtime-specific. The finding requires a producer/consumer disagreement, not the mere presence of casts.

## Conditions that establish the issue

Recover the producer's semantic type, bit width, signedness, encoding, address space, conversion path, and final consumer. Prove significant information is lost or a value lacking pointer/object authority reaches a load, store, release, or indirect transfer as if it were valid.

For handles, use the defining API contract and required operation rather than native pointer syntax. For file-relative or module-relative values, establish the correct base and range before address formation.

## Evidence that is not sufficient

`reinterpret_cast`, `uintptr_t`, pointer-sized typedef, high bits, or a decompiler labeling a field as a pointer is not sufficient. The value may be an opaque token, compressed pointer, tagged reference, RVA, index, or intentionally round-tripped representation.

A nonfaulting dereference does not prove the object type, lifetime, or authorization.

## Investigation sequence

Track raw bits and semantic category through each boundary. Record every truncation, extension, mask, tag operation, base addition, table lookup, and API call. Identify the address space and full accessed range at the final use.

Compare callers and callees under the actual data model and ABI. Preserve handle-table selection and process context; equal handle bits in different processes do not imply one object.

## Constructed source and x86-64 example

```c
uint32_t read_field(uint32_t wire_value)
{
    const uint32_t *pointer = (const uint32_t *)(uintptr_t)wire_value;
    return *pointer;
}
```

On x86-64 a constructed fragment can show `mov eax,ecx; mov eax,dword ptr [rax]`: writing `EAX` zero-extends the 32-bit input into `RAX`, then treats it as a virtual address. The issue requires the wire field to be an untrusted scalar rather than a specified pointer encoding and the resulting address to reach the load; mapping determines fault versus readable data.

## Primitive and impact limits

The direct primitive can be invalid or attacker-directed memory access, wrong resource selection, or release of an unrelated object. Stronger disclosure, write, or control-flow claims require a usable target, permissions, and observable effect.

## Related knowledge and primary sources

`architecture-machine-representation` defines pointer-looking values and extension behavior, while `abi-data-models-api-types` distinguishes opaque Windows handles and pointer-width types. This profile repeats semantic-category and address-space proof locally.

Reviewed 2026-10-09 against C integer/pointer conversions in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [`reinterpret_cast`](https://eel.is/c++draft/expr.reinterpret.cast), Microsoft [Windows data types](https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types), and [MITRE CWE-704](https://cwe.mitre.org/data/definitions/704.html). The source and assembly are constructed.
