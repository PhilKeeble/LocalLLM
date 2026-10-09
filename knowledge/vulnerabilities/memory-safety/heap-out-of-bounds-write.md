---
id: vulnerability-memory-heap-out-of-bounds-write
title: Heap-based out-of-bounds write
kind: vulnerability
topics: [memory-safety, out-of-bounds-write, heap, buffer-overflow]
platforms: [cross-platform]
architectures: [any]
---

# Heap-based out-of-bounds write

## Definition and violated invariant

A heap-based out-of-bounds write occurs when code writes outside the intended extent of a live dynamically allocated object. If an allocation requests `N` bytes, a write through that object must remain within `[base, base + N)` unless the allocator API explicitly exposes a different usable extent. The defect begins at the first byte outside the object even if allocator rounding leaves that address mapped.

This profile covers spatial corruption of a live heap object. A stale write after release is use-after-free, and an undersized allocation caused by wrapped arithmetic is an allocation-size-overflow chain with this write as a later consequence.

## Conditions that establish the issue

Establish a reachable write, the allocation generation, requested object extent, destination offset and complete write width or count. A security-relevant path also needs influence from a less-trusted source over the data, offset, length, loop bound, terminator or transformation that makes the range exceed the object.

Track the requested allocation separately from allocator bucket size, mapped pages, logical payload and initialized bytes. A write can violate the object without crossing a page or allocator block. Conversely, writing across members of one intentionally byte-addressed record is not a field overflow unless the operation's contract limits it to a smaller subobject.

## Evidence that is not sufficient

A heap allocation followed by `memcpy`, a crash in allocator code, a large input, or bytes adjacent to another object does not establish this issue. A dominating bound may constrain the count, the decompiler may infer the wrong object type, the destination may be a flexible or deliberately overallocated object, or the helper may stop before the requested count.

Do not infer overwrite of allocator metadata, a function pointer or another chosen object from the bounds violation alone. Heap identity, size class, placement, reuse, quarantine and competing allocations determine what physically follows the object.

## Investigation sequence

Start at the allocation and record allocator identity, requested size, returned pointer, object generation and failure handling. Trace every value contributing to the destination address and write extent with its width, signedness and unit. For a write at offset `O` with length `M` into an `N`-byte object, first prove the arithmetic representable, then require `O <= N` and `M <= N - O`.

Follow all predecessor paths for an adequate bound and all loop iterations for their actual scalar or vector width. Include encoding expansion, structure stride, terminators, partial-copy results and integer conversions. After establishing the object violation, separately identify what bytes can be controlled and which corrupted value is subsequently consumed.

## Constructed source example

This hypothetical function allocates a fixed 32-byte heap object and copies a caller-supplied count:

```c
void copy_record(const unsigned char *source, size_t length)
{
    unsigned char *record = malloc(32);
    if (record == NULL)
        return;
    memcpy(record, source, length);
    consume_record(record, 32);
    free(record);
}
```

On the shown path, `length > 32` writes beyond the requested object if `memcpy` attempts the full count. The example is not a finding if every feasible caller proves `length <= 32`, the copy resolves to a helper with a different contract, or the allocation is intentionally larger than the source representation suggests.

## Constructed Windows x64 representation

This is one possible unoptimized Windows x64 lowering. At entry, `source` is in `RCX` and `length` is in `RDX`. The omitted prologue saves the nonvolatile `RBX`, `RSI` and `RDI` registers and reserves the required call area:

```asm
mov  rsi, rcx             ; source
mov  rbx, rdx             ; length
mov  ecx, 20h             ; malloc(32)
call malloc
test rax, rax
je   done
mov  rdi, rax             ; returned 32-byte object
mov  rcx, rdi             ; memcpy destination
mov  rdx, rsi             ; memcpy source
mov  r8,  rbx             ; memcpy count
call memcpy
```

The constant passed to `malloc` and the independent value passed to `memcpy` expose the required comparison. Absence of a comparison in this excerpt is only a lead: confirm callers and dominating blocks. A compiler may inline either call, choose other nonvolatile registers or prove the bound and remove a redundant check.

## Primitive and impact limits

The direct primitive is a write beyond a live heap object's boundary. Record maximum overrun, controlled bytes, offset control, repeatability and whether execution continues. A detected fault supports denial of service on the exercised path. Disclosure requires a separate read or observable effect; arbitrary write requires control of destination as well as data.

Code execution requires evidence that the corruption reaches control-bearing state or develops another usable primitive under the target allocator, object layout and active mitigations. A nearby callback, virtual table pointer or allocator structure is a candidate target, not proof of influence or invocation.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns object-range reasoning, and `reference-native-integer-size-buffer-arithmetic` owns arithmetic prerequisites. Platform allocator references supply target-specific size and heap contracts; the necessary object-bound rule is repeated here so this profile stands alone.

Reviewed 2026-10-09 against [MITRE CWE-122](https://cwe.mitre.org/data/definitions/122.html), the C language object and array rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), the [C++ object model](https://eel.is/c++draft/intro.object), the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention), and the diagnostic-only excess-space limitation documented for [Linux `malloc_usable_size`](https://man7.org/linux/man-pages/man3/malloc_usable_size.3.html). The source and assembly are constructed examples, not observed compiler output.
