---
id: vulnerability-memory-static-mapped-out-of-bounds-write
title: Global, static, TLS and mapped-region out-of-bounds write
kind: vulnerability
topics: [memory-safety, out-of-bounds-write, globals, tls, memory-mapping]
platforms: [cross-platform]
architectures: [any]
---

# Global, static, TLS and mapped-region out-of-bounds write

## Definition and violated invariant

This vulnerability is a write outside the intended extent of an object whose storage comes from a static/global image region, thread-local storage or an explicit memory mapping. For an object occupying `[base, base + N)`, the full write range must remain inside that object even if surrounding pages are writable.

Storage location changes the likely neighbors and address calculation, not the object-bound rule. Global/static duration, TLS per-thread instances and mapped file or shared-memory views have different identity and lifetime contracts and must not be conflated.

## Conditions that establish the issue

Prove the object's actual base and extent, a reachable write range that crosses it, and less-trusted influence over the index, offset, count or bytes. For a mapped view, also recover mapping length, file offset, protection, sharing mode and whether the logical object is smaller than the mapping.

For TLS, identify the current thread's instance and applicable TLS model. For globals, recover relocation and linker placement from the loaded image rather than assuming source declaration order. Establish any corrupted neighbor independently.

## Evidence that is not sufficient

A RIP-relative or thread-segment-relative store, a writable image section, a mapping API or a global array is not sufficient. A dominating bound may protect the store, the symbol may represent a deliberately overallocated region, or the apparent array may be one field in a larger byte-addressed object.

Do not infer stable adjacency from symbol tables or one build. Linker ordering, padding, section merging, TLS layout, loader relocation and mapping placement can change. Crossing the logical object is the defect; corruption of a chosen neighbor needs target-specific layout and use evidence.

## Investigation sequence

Classify storage first: image global/static, TLS, anonymous mapping, file mapping, shared memory or device mapping. Recover the allocation or mapping contract, symbol/subobject extent and loaded address. Calculate the entire write range with representable arithmetic and trace every guard that dominates it.

Then recover permissions and sharing. A write into a private mapping can affect only that process, while a shared mapping can alter state consumed by another component. A file-backed dirty page can have persistence consequences only if the mapping and flush/writeback contract support them.

## Constructed source and Windows x64 evidence

This hypothetical global array has 16 valid byte indices:

```c
static unsigned char table[16];

void set_entry(size_t index, unsigned char value)
{
    table[index] = value;
}
```

One possible Windows x64 lowering receives `index` in `RCX` and `value` in the low byte of `RDX`:

```asm
lea  rax, [rip+table]
mov  byte ptr [rax+rcx], dl
ret
```

The RIP-relative `lea` identifies image-relative storage; it does not reveal `table`'s extent by itself. If `index >= 16` is feasible, the byte store is outside this object. Confirm relocations, symbol or use-derived size and all callers; the absent comparison in this leaf is not proof that callers fail to bound `index`.

## Primitive and impact limits

The direct primitive is an out-of-bounds write relative to a static, TLS or mapped object. Record controlled range, byte values, thread instance and sharing. A fault supports denial of service; persistent file modification requires file-backed shared-write semantics; cross-process corruption requires a shared mapping consumed by another process.

Code execution or privilege escalation requires a demonstrated control-bearing or authority-relevant target and later use. Writable adjacency to a function pointer, lock, credential flag or dispatch table is a lead, not proof of reach or invocation.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns object and subobject ranges. Executable-format, TLS and mapping references own platform layout details. This profile repeats the storage classification and object-bound proof needed to evaluate the write in isolation.

Reviewed 2026-10-09 against [MITRE CWE-787](https://cwe.mitre.org/data/definitions/787.html), C object and storage-duration rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), the [PE/COFF specification](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The example does not assert a stable linker layout.
