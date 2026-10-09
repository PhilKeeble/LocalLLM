---
id: vulnerability-memory-overlapping-copy-operation
title: Overlapping ranges passed to a non-overlap copy operation
kind: vulnerability
topics: [memory-safety, overlap, memcpy, copying, undefined-behavior]
platforms: [cross-platform]
architectures: [any]
---

# Overlapping ranges passed to a non-overlap copy operation

## Definition and violated invariant

An overlap vulnerability occurs when source and destination byte ranges intersect but the selected operation requires them not to overlap. C `memcpy` has that restriction; `memmove` defines copying as if through a temporary array and supports overlap. Both still require the complete source and destination ranges to be valid.

Forbidden overlap can corrupt data or invoke source-language undefined behavior without crossing an allocation boundary. It becomes a security vulnerability when the resulting state influences a security decision, parser structure, pointer, length, or other sensitive operation.

## Conditions that establish the issue

Recover the exact source range `[S,S+N)`, destination range `[D,D+N)`, byte count, and resolved copy implementation. For representable addresses, the ranges overlap when `S < D+N` and `D < S+N`. Prove the non-overlap contract applies and a feasible path reaches the call with intersecting nonempty ranges.

Then trace the altered bytes to a security-relevant effect. If the binary contains an inlined direction-aware copy with defined intended behavior, a misleading imported name elsewhere does not establish the issue.

## Evidence that is not sufficient

Pointers into one allocation, matching bases, or a copy used for compaction is not sufficient. Subranges within one allocation can be disjoint, a zero-length copy has no copied range, and the selected routine may explicitly support overlap.

One observed output is not a portable contract for `memcpy`; implementation direction and optimization can change. Bounds safety also does not prove overlap safety, and switching overlap semantics would not repair an oversized range.

## Investigation sequence

Calculate the two half-open ranges using the actual count after conversions. Identify aliases and base adjustments across wrappers. Resolve whether the call is `memcpy`, `memmove`, a platform equivalent, or custom code, and inspect inlining or compiler transformations where relevant.

Follow the destination into the next parse or use and identify which required byte relation can be violated. Separate a language-level undefined operation from a demonstrated binary result, especially when analyzing one compiled artifact.

## Constructed source example

This hypothetical function shifts `used` bytes one position to the right within a buffer that has at least `used + 1` bytes of capacity:

```c
void insert_prefix_bad(char *buffer, size_t used)
{
    memcpy(buffer + 1, buffer, used);
    buffer[0] = ':';
}
```

For `used > 0`, source `[buffer,buffer+used)` and destination `[buffer+1,buffer+1+used)` overlap, violating `memcpy`'s contract despite both ranges fitting the allocation. Whether corrupted output creates a vulnerability depends on how the shifted record is consumed.

## Constructed System V AMD64 representation

For the constructed two-argument function, System V AMD64 receives `buffer` in `RDI` and `used` in `RSI`. This tail-call-shaped fragment rearranges them for `memcpy(destination, source, count)`:

```asm
mov  rdx, rsi             ; count = used
mov  rsi, rdi             ; source = buffer
lea  rdi, [rdi+1]         ; destination = buffer + 1
call memcpy
```

The call ranges overlap whenever `used` is nonzero. Confirm that the resolved call retains `memcpy` semantics; an optimizer may inline a different sequence whose concrete binary effects require separate analysis.

## Primitive and impact limits

The direct effect is unreliable destination content under the source contract, not automatically an out-of-bounds access or arbitrary write. Record the actual compiled copy direction and corrupted fields if assessing a particular binary.

Security impact requires a demonstrated consumer of the damaged state. A malformed display string is different from corruption of a parsed length, authenticated message, object pointer, or dispatch value.

## Related knowledge and primary sources

`reference-native-strings-copy-format` owns the shared `memcpy` and `memmove` contracts. This profile repeats the interval test and security-effect requirement needed when retrieved alone.

Reviewed 2026-10-09 against C [`memcpy` and `memmove`](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), POSIX [`memcpy`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/memcpy.html) and [`memmove`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/memmove.html), and the [System V AMD64 ABI](https://gitlab.com/x86-psABIs/x86-64-ABI). The source and assembly are constructed.
