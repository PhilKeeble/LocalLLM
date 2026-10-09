---
id: vulnerability-memory-intra-object-out-of-bounds-access
title: Intra-object or subobject out-of-bounds access
kind: vulnerability
topics: [memory-safety, subobjects, structure-layout, adjacent-fields, bounds]
platforms: [cross-platform]
architectures: [any]
---

# Intra-object or subobject out-of-bounds access

## Definition and violated invariant

An intra-object out-of-bounds vulnerability crosses the intended array member, field, base-class, or embedded-object boundary while remaining inside the enclosing allocation. Allocation-level bounds are therefore insufficient: the access must fit the subobject authorized by the operation and preserve adjacent semantic state.

Whole-object byte copying, serialization, initialization, or comparison can legitimately span members under its applicable language and representation contract. Establish that the operation is intended for the narrower subobject before calling the crossing invalid.

## Conditions that establish the issue

Recover the enclosing allocation, applicable ABI layout, active object and subobject lifetimes, target subobject range, access width, and adjacent fields. Prove a reachable operation whose authorized source or destination is the subobject but whose range crosses its end or begins before it.

For C++ bases, tail padding, unions, and reused storage, apply the target language and ABI rules rather than tiling the allocation with guessed `sizeof` values. Then trace corrupted or disclosed neighboring state to a security-relevant consumer.

## Evidence that is not sufficient

An access spanning two displayed decompiler fields, remaining within `malloc` size, or touching apparent padding is not sufficient. The recovered structure may be incomplete, one machine load may intentionally cover several source fields, or the operation may be defined over the complete record.

Allocator rounding and a mapped neighboring byte do not authorize a subobject overrun. Conversely, padding corruption has no established semantic effect unless it is later copied, compared, exposed, or reinterpreted under a supported contract.

## Investigation sequence

Maintain separate ranges for allocation, complete object, each relevant subobject, logical payload, and initialized bytes. Derive field offsets from type metadata or consistent access/layout evidence. Identify the operation's intended destination or source and calculate its complete byte interval.

Follow adjacent fields into authorization, length, pointer, tag, dispatch, or output uses. In assembly, account for wide and vector accesses, masks, and read-modify-write operations; the instruction width can exceed the source-level field width without necessarily violating its contract.

## Constructed source example

Under the stated constructed layout, `name` occupies offsets 0 through 7 and `flags` occupies offsets 8 through 11:

```c
struct record {
    char name[8];
    uint32_t flags;
};

int set_name(struct record *record, const char *input, size_t length)
{
    if (length > sizeof(*record))
        return -1;
    memcpy(record->name, input, length);
    return 0;
}
```

A 12-byte copy stays within the 12-byte record but overwrites `flags`, because the operation is a name copy whose destination subobject has capacity eight. If the contract intentionally initializes a serialized whole-record representation, this narrower conclusion would not follow.

## Constructed Windows x64 representation

Under Windows x64 the constructed arguments arrive as record `RCX`, input `RDX`, and length `R8`:

```asm
cmp  r8, 0Ch
ja   reject               ; checks complete record size
call memcpy               ; destination RCX is also name at offset zero
```

Lengths 9 through 12 pass the allocation-level check and cross into the adjacent field under the stated layout. Confirm the real field offset, packing, object purpose, and input readability; a different structure layout invalidates the numeric example.

## Primitive and impact limits

The direct primitive is a subobject over-read or overwrite. Record the crossed boundary, exact adjacent bytes, operation direction, and later semantic use. Remaining within one allocation may make the access less likely to fault but does not determine its security impact.

Privilege or code execution claims require the adjacent state to control an authorized action, address, length, type tag, or dispatch target. Corruption of unused padding or subsequently overwritten state may have no observable consequence.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` distinguishes object and subobject extents, while `reference-native-structure-layout-access` covers partial layout evidence. This profile repeats the operation-scope requirement needed when retrieved alone.

Reviewed 2026-10-09 against C object and array rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [object model](https://eel.is/c++draft/intro.object) and [pointer arithmetic](https://eel.is/c++draft/expr.add), Microsoft [x64 aggregate layout](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions), and [MITRE CWE-787](https://cwe.mitre.org/data/definitions/787.html). The layout, source, and assembly are constructed.
