---
id: vulnerability-lifetime-double-free-duplicate-release
title: Double free, duplicate release, or duplicate finalization
kind: vulnerability
topics: [lifetime, double-free, duplicate-release, cleanup, ownership]
platforms: [cross-platform]
architectures: [any]
---

# Double free, duplicate release, or duplicate finalization

## Definition and violated invariant

Double free or duplicate release occurs when one allocation or resource generation is released more times than ownership permits. The repeated operation can target heap storage, a reference, handle, descriptor, lock, transaction, callback registration, or language finalizer; each has its own release and idempotence contract.

Two cleanup sites are not enough. Prove one feasible execution reaches both for the same generation without an intervening reacquisition or documented idempotent release.

## Conditions that establish the issue

Identify acquisition, generation, owners, transfers, aliases, every release path, and the release API's repeated-call behavior. Establish path conditions showing the first release completes and the second receives the same now-invalid ownership token or pointer.

For C++ destruction, distinguish base, complete, and deleting destructor variants and constructor-failure cleanup. A destructor wrapper followed by its intended deallocator is not automatically duplicate release.

## Evidence that is not sufficient

Two calls named `free`, repeated destructor symbols, normal and exceptional cleanup blocks, or the same numeric address in different requests is not sufficient. Branches may be mutually exclusive, wrappers may release different layers, or a new allocation may reuse the address.

Nulling one owner can prevent its second release but does not update copied aliases. `free(NULL)` is defined to have no effect under the C contract; other release APIs can differ.

## Investigation sequence

Create a path-sensitive ownership ledger from acquisition to every exit. Label each operation with resource type, generation, allocator or provider, and whether ownership transfers or is merely borrowed. Follow normal return, error, cancellation, exception, teardown, and retry paths.

At machine level, trace the exact pointer or handle value and any reload between calls. Distinguish an allocator diagnostic at the second release from proof of the original root cause, because earlier memory corruption can also damage allocator state.

## Constructed source example

```c
int decode(void)
{
    void *object = malloc(64);
    if (object == NULL)
        return -1;
    if (!parse(object)) {
        free(object);
        goto failure;
    }
    return publish(object);
failure:
    free(object);
    return -1;
}
```

When `parse` fails, both `free` calls receive the same allocation generation. A representative binary path preserves the allocation base across `call free`, branches to shared cleanup, reloads the same base, and calls `free` again. If the first helper only releases an interior resource rather than `object`, the conclusion changes.

## Primitive and impact limits

The direct primitive is a repeated invalid release. Effects depend on allocator or resource implementation and can include heap corruption, releasing a reused object, count underflow, denial of service, or no additional effect for an idempotent API.

Arbitrary write or execution requires implementation-specific evidence about reuse, metadata, controllable operations, and mitigations. Do not infer a heap exploit from the second call alone.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling` defines allocation generations and C++ deletion distinctions, while `reference-native-cpp-lifecycle-unwind` covers mutually exclusive cleanup. This profile repeats the same-generation path proof locally.

Reviewed 2026-10-09 against [MITRE CWE-415](https://cwe.mitre.org/data/definitions/415.html), C [`free`](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [delete expressions](https://eel.is/c++draft/expr.delete), and the [Itanium C++ ABI destructor variants](https://itanium-cxx-abi.github.io/cxx-abi/abi.html). The example is constructed.
