---
id: vulnerability-type-structure-layout-abi-mismatch
title: Structure layout, packing, alignment, or ABI mismatch across a boundary
kind: vulnerability
topics: [structure-layout, packing, alignment, abi, ffi, memory-safety]
platforms: [cross-platform]
architectures: [any]
---

# Structure layout, packing, alignment, or ABI mismatch across a boundary

## Definition and violated invariant

A layout mismatch occurs when producer and consumer disagree about member offsets, total size, alignment, padding, packing, array stride, calling convention, or native data model for the same transferred object. Each side must use one compatible representation contract or marshal fields explicitly.

Native `sizeof` and field layout are compiler-, ABI-, target-, and attribute-dependent and are not automatically a wire format. Matching total sizes also do not prove matching member positions or meanings.

## Conditions that establish the issue

Recover producer and consumer declarations or machine layouts, packing state, scalar widths, alignment, byte order, structure version, and exact transferred extent. Prove a field or call is decoded at a different byte range or register location and that the disagreement reaches a security-relevant operation.

For nested records, determine each nested type's own representation; packing an outer structure need not recursively repack an independently defined member.

## Evidence that is not sufficient

An unaligned access, padding gap, `memcpy` of a record, or different decompiler type is not sufficient. The code may intentionally decode bytes, use matching packed declarations, or operate on an opaque blob.

A successful call or nonfaulting load does not establish agreement; an out-of-range read or semantic field swap can remain silent.

## Investigation sequence

Create producer and consumer byte maps with field ranges, alignment, size, and array stride. Compare the exact boundary bytes and any marshalling stub. Recover the calling convention separately from in-memory aggregate layout.

At binary level, identify access offsets and widths on both sides and verify the supplied object extent. Keep serialized coordinates separate from native pointers and structures.

## Constructed packed-record example

```c
#pragma pack(push, 1)
struct wire_record { uint8_t tag; uint32_t length; };
#pragma pack(pop)

struct native_record { uint8_t tag; uint32_t length; };

uint32_t consume(const struct native_record *record)
{
    return record->length;
}
```

On a constructed ABI where the packed record is five bytes with `length` at offset one and the native record places `length` at offset four with size eight, passing packed bytes directly to `consume` reads bytes four through seven, crossing the five-byte input and decoding the wrong field. A matching assembly load is `mov eax,dword ptr [rcx+4]`; verify real packing and extent before applying the example.

## Primitive and impact limits

The direct result can be out-of-bounds access, wrong length, pointer corruption, misaligned operation, or calling-convention argument confusion. Impact depends on the consumed field and target hardware/runtime behavior.

## Related knowledge and primary sources

`reference-native-structure-layout-access`, `abi-data-models-api-types`, and calling-convention references supply layout fundamentals. This profile repeats the two-sided byte-map requirement locally.

Reviewed 2026-10-09 against Microsoft [`pack`](https://learn.microsoft.com/en-us/cpp/preprocessor/pack), Microsoft [x64 aggregate layout](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions), GCC [type attributes](https://gcc.gnu.org/onlinedocs/gcc/Common-Type-Attributes.html), and [MITRE CWE-119](https://cwe.mitre.org/data/definitions/119.html). The layouts, source, and assembly are constructed.
