---
id: vulnerability-lifetime-stale-pointer-after-relocation
title: Stale pointer after realloc, container growth, or moving collection
kind: vulnerability
topics: [lifetime, realloc, containers, moving-gc, stale-pointer]
platforms: [cross-platform]
architectures: [any]
---

# Stale pointer after realloc, container growth, or moving collection

## Definition and violated invariant

A relocation stale-pointer vulnerability occurs when code retains an address into storage that can move, then dereferences the old address after successful reallocation, container growth, compaction, or moving garbage collection. The owner can remain logically alive while earlier base and interior pointers become invalid.

Invalidation depends on the operation and runtime. C `realloc` invalidates the old pointer on success even when the returned address compares equal; on failure the original allocation remains valid. C++ container operations have type-specific rules, and managed native pointers require the selected pinning contract.

## Conditions that establish the issue

Identify pointer acquisition, owning object, relocation-capable operation, its success result, applicable invalidation rule, and later use of the unreacquired pointer. Prove relocation or contractual invalidation is feasible on that path and that the consumer uses the stale alias.

For interior pointers, reacquiring only the base is insufficient unless the interior offset and object identity are correctly re-established.

## Evidence that is not sufficient

`realloc`, `push_back`, garbage collection, or changed capacity is not sufficient. Reallocation may fail, a vector may retain capacity, a container may preserve element references, or an object may be pinned.

Stable numeric address in one run does not override a language invalidation rule, but a contract violation alone does not prove a particular binary exploit effect.

## Investigation sequence

Track owner base, saved aliases, size/capacity, mutation, returned replacement, and all later uses. Branch on success and failure separately. For containers, identify the exact implementation and operation; for managed runtimes, trace pinning and native-call lifetime.

In assembly, compare the saved pointer with the updated owner field and follow both through calls. Establish whether the apparent pointer is an element reference, iterator, numeric index, or container address.

## Constructed example

```c
uint8_t *interior = buffer + field_offset;
uint8_t *replacement = realloc(buffer, larger_size);
if (replacement == NULL)
    return -1;
buffer = replacement;
consume(interior);
```

After successful `realloc`, `interior` is derived from the invalidated old pointer and must not be used, regardless of whether the new base happens to have the same numeric value. On failure, the original object remains live and the shown early return avoids the stale use.

## Primitive and impact limits

The direct primitive is a stale read, write, or call through the pre-relocation address. Exploitability depends on movement, reuse, controlled contents, access type, and mitigations; logical misbinding can occur even without a fault.

## Related knowledge and primary sources

`reference-native-container-invalidation` provides operation-specific C++ rules, and runtime references cover moving collectors and pinning. This profile repeats the success/invalidation distinction needed alone.

Reviewed 2026-10-09 against C [`realloc`](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [`vector` capacity](https://eel.is/c++draft/vector.capacity), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The example is constructed.
