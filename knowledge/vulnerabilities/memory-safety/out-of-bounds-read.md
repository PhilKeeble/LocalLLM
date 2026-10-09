---
id: vulnerability-memory-out-of-bounds-read
title: Out-of-bounds read before or after an intended object
kind: vulnerability
topics: [memory-safety, out-of-bounds-read, information-disclosure, bounds]
platforms: [cross-platform]
architectures: [any]
---

# Out-of-bounds read before or after an intended object

## Definition and violated invariant

An out-of-bounds read occurs when code reads any byte outside the intended live object's extent. The first address can be valid while a wider scalar, vector or copy crosses the boundary. A readable neighboring page does not extend the object or make the access valid.

The defect is the invalid read. Information disclosure additionally requires the read bytes to influence an output, side channel or security decision observable across a trust boundary. A fault without disclosure supports availability impact on the exercised path.

## Conditions that establish the issue

Recover the source object's base, capacity, initialized range and allocation generation. Calculate the complete read range for every iteration or helper operation and prove a feasible path where it is not contained in the object. Establish less-trusted influence over the offset, count, sentinel or state that reaches that path.

For disclosure, trace the out-of-range bytes to their consumer: response, log, comparison, branch, checksum, compression output or copied destination. Distinguish reading uninitialized bytes inside an object from reading outside it; both can disclose data but violate different invariants.

## Evidence that is not sufficient

A load near an end pointer, a crash in a parser, a large declared length, or a buffer followed by sensitive memory is not sufficient. The load may be an intentional in-object lookahead, a vector operation whose extra lanes are masked before use, or a helper operating on a larger allocation than the decompiler inferred.

Do not infer disclosure merely because bytes were fetched by the CPU. Establish architectural consumption and an observable path; speculative or prefetched data needs a separate side-channel analysis.

## Investigation sequence

Trace available bytes, declared length, logical payload and consumed length separately. For a read of width `W` at offset `O` into an `N`-byte object, require representable arithmetic, `O <= N` and `W <= N - O`. For loops, include the final iteration and instruction width; for strings, establish a reachable terminator or independent bound.

At binary level, recover signedness of index checks, scale, base pointer, load width and whether later instructions mask or use every loaded lane. Follow error paths and partial-read results so stale or unwritten capacity is not mistaken for received input.

## Constructed source example

This hypothetical checksum trusts a claimed length rather than the available object extent:

```c
uint32_t checksum(const unsigned char *data, size_t available, size_t claimed)
{
    uint32_t sum = 0;
    for (size_t i = 0; i < claimed; ++i)
        sum += data[i];
    return sum;
}
```

The read becomes out of bounds when `claimed > available` and execution reaches `i == available`. Returning the checksum exposes a derived value, not necessarily the bytes themselves; the strength of any disclosure oracle requires separate analysis. A caller-proven relation `claimed <= available` refutes the shown candidate.

## Constructed Windows x64 representation

Under Windows x64, the constructed arguments are `data` in `RCX`, `available` in `RDX` and `claimed` in `R8`. This possible loop never consumes `available`:

```asm
xor  eax, eax             ; sum
xor  r9d, r9d             ; i
loop_bytes:
cmp  r9, r8
jae  done
movzx r10d, byte ptr [rcx+r9]
add  eax, r10d
inc  r9
jmp  loop_bytes
```

The byte load is invalid once `R9` reaches the actual object extent. The unused `RDX` is a strong lead in this constructed function, but real callers or wrappers can enforce the relation. Confirm object size and all predecessor constraints before classifying it.

## Primitive and impact limits

Record read direction, maximum range, repeatability and observable transformation. A direct copy into a response can disclose bytes; a comparison can expose a narrower oracle; a pointer or length consumed from adjacent memory may create a later control or memory primitive. Report only the demonstrated chain.

An out-of-bounds read does not write memory and does not independently establish code execution. Code execution requires another defect or a control decision driven by the invalid value.

## Related knowledge and primary sources

`reference-native-bounds-objects-terminators` owns full-range, one-past and sentinel reasoning. `reference-native-integer-size-buffer-arithmetic` owns the arithmetic prerequisites. The observable-use requirement is repeated here because an invalid read and information disclosure are different conclusions.

Reviewed 2026-10-09 against [MITRE CWE-125](https://cwe.mitre.org/data/definitions/125.html), C array and pointer rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The checksum and assembly are constructed.
