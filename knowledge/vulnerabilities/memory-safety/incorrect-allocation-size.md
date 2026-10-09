---
id: vulnerability-memory-incorrect-allocation-size
title: Incorrect allocation size for the intended object layout
kind: vulnerability
topics: [memory-safety, allocation-size, object-layout, flexible-array, alignment]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect allocation size for the intended object layout

## Definition and violated invariant

An incorrect-allocation-size vulnerability requests storage that does not cover the object layout later constructed or accessed. The allocation must include every required element, header, trailer, flexible-array payload, alignment contribution, and terminator in the units and layout of the active ABI or format version, with all arithmetic representable.

This differs from arithmetic overflow: every calculation may be representable yet use the wrong type size or omit a component. The issue becomes spatial memory corruption only when a reachable later access crosses the returned object's valid extent.

## Conditions that establish the issue

Recover the allocator request, successful returned object, actual layout contract, and maximum range later initialized or consumed. Prove that the requested byte count is smaller than that range for a feasible input. For a flexible-array member, include the fixed prefix and requested elements; for aligned data, prove both padding and final access width.

Structure layouts are ABI and packing dependent. Establish field offsets and total size from trustworthy type metadata, allocation/access strides, or consistent machine evidence rather than transferring a layout from another build.

## Evidence that is not sufficient

Use of `sizeof(pointer)`, a small allocation constant, or different allocation and loop scales is not sufficient without the intended object type and reachable access. The allocation may intentionally hold pointers, an opaque header may own trailing storage elsewhere, or the later scale may address a different object.

Allocator rounding or adjacent mapped memory does not enlarge the requested C object contract. Conversely, an apparently omitted trailer may be optional for the active structure version, so recover the selected version and consumer path.

## Investigation sequence

Trace the object from type or format selection through size calculation, allocation, initialization, and every field or element access. Record fixed prefix, element count and width, alignment, optional regions, and terminators. Compare the requested byte interval with the highest accessed interval, checking multiplication and addition independently for overflow.

In a stripped binary, compare allocator arguments with address scales and loop bounds, then corroborate inferred layout through repeated field offsets and call contracts. Check error and zero-count paths, because an allocator's zero-size behavior does not authorize dereference.

## Constructed source example

This hypothetical 64-bit layout needs 16 bytes per record but allocates using the size of a record pointer:

```c
struct record {
    uint64_t key;
    uint32_t flags;
    uint32_t length;
};

struct record *make_records(size_t count)
{
    struct record *records = malloc(count * sizeof(struct record *));
    if (records == NULL)
        return NULL;
    for (size_t i = 0; i < count; ++i)
        initialize_record(&records[i]);
    return records;
}
```

Under the stated layout, allocation scales by eight bytes while indexing scales by 16. The exact sizes are not portable; a dominating count of zero or an initializer that does not access the full record could alter the first concrete violation.

## Constructed Windows x64 representation

This abbreviated Windows x64 sequence receives `count` in `RCX`. It preserves the original count, allocates at an eight-byte scale, and later calculates record addresses at a 16-byte scale; the omitted prologue must preserve the nonvolatile registers and call space:

```asm
mov  rbx, rcx             ; original count
shl  rcx, 3               ; count * sizeof(pointer)
call malloc
test rax, rax
je   allocation_failed
mov  rdi, rax
xor  rsi, rsi
test rbx, rbx
je   records_done
loop_records:
mov  rax, rsi
shl  rax, 4               ; i * sizeof(record)
lea  rcx, [rdi+rax]
call initialize_record
inc  rsi
cmp  rsi, rbx
jb   loop_records
records_done:
```

The scale mismatch is meaningful only after proving the allocator and indexed base refer to the same live object and that `initialize_record` writes into the computed record. Check the real product for overflow separately.

## Primitive and impact limits

The direct primitive is an undersized live object followed by an access to layout bytes that were never allocated for it. Record whether the result is an out-of-bounds read, write, construction, or destructor action and identify the first unsupported range.

Exploitability depends on count control, written data, heap placement, failure behavior, subsequent use, and mitigations. An incorrect request can instead yield immediate failure, a deterministic crash, or inaccessible optional data.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` distinguishes requested storage from surrounding mapped or allocator space, while `reference-native-integer-size-buffer-arithmetic` covers checked totals. The profile includes the decisive layout/request mismatch locally.

Reviewed 2026-10-09 against [MITRE CWE-131](https://cwe.mitre.org/data/definitions/131.html), C `sizeof`, object, and flexible-array rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [object size](https://eel.is/c++draft/expr.sizeof), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The layout, source, and assembly are constructed.
