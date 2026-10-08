---
id: reference-native-bounds-objects-terminators
title: Native out-of-bounds access, subobjects, one-past pointers and off-by-one errors
kind: reference
topics: [memory-safety, bounds, subobjects, off-by-one, terminators, sentinels]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Bounds, objects and terminators

## Extents that must not be conflated

Record separately: mapped region, allocator block, requested allocation,
constructed object/subobject, logical payload and initialized byte range.
An access can remain within a mapped page while crossing an object or exposing
uninitialized bytes. Allocator rounding is not a portable extension of requested
storage: Linux malloc_usable_size documentation explicitly rejects writing excess
reported space without reallocating it. [1]

Constructed investigation: a record allocation contains an eight-byte name and
an authorization field. Writing twelve name bytes may stay in the allocation
but corrupt the neighboring field. Establish actual field boundaries and the
write's intended contract; a heap-level boundary check alone cannot refute it.
Conversely, a supported whole-record byte copy is not a field overrun merely
because it spans several members. Identify the operation's object and purpose.

## Full access ranges, not just starting addresses

For nonnegative byte coordinates in one representable domain, a read/write of
width w at offset o in extent n requires first `o <= n`, then `w <= n-o`.
Apply independently to source and destination of a copy. For a sequence, include
all iterations and the actual scalar/vector width, not its decompiled type.
See `reference-native-integer-size-buffer-arithmetic` for arithmetic prerequisites.

Constructed example: an eight-byte load at offset 12 in a 16-byte payload touches
bytes 12..19. Its first byte is valid but the range exceeds the payload by four.
If independent evidence proves a larger readable object and intentional
lookahead, record that contract instead of inferring a fault from payload size
alone. A readable overrun may still violate confidentiality or parsing semantics;
prove which bytes are consumed and what crosses a trust boundary.

## One-past pointers and subobjects

C++ permits forming the one-past endpoint of an array for relevant arithmetic
and comparisons. That endpoint is not an element to read or write, nor does it
become a pointer to an unrelated adjacent object just because addresses match.
Pointer arithmetic has object-based restrictions, not only integer-address
bounds. [2,3]

Investigation: distinguish comparing an end pointer from dereferencing it. A
loop using `p != end` may be valid; a consuming path at `p == end` needs its own
range proof. Source-language UB and observed binary effects are separate claims.
For an apparent subobject crossing, recover layout and byte-operation contract
before assuming the decompiler's array declaration is the original type.
Compression-history matches are a distinct contract: legal overlap and valid
backward distance still require output capacity. See
`reference-parser-compression-framing-history`.

## Off-by-one and terminator capacity

An N-element array has valid element indices 0..N-1. A payload of k character
code units plus one terminator needs at least k+1 units with checked arithmetic.
An allocation sized for exactly k nonterminated units is not necessarily wrong;
the consuming API determines whether a terminator is required.

Constructed example: after copying eight payload bytes into `char out[8]`, a
write to `out[8]` for NUL is outside the array. If only seven payload bytes were
accepted, `out[7]` could be the terminator. Trace the accepted count, written
count and capacity separately; do not confuse a returned required length with
the count actually stored. Include the zero-capacity case before a `cap-1`
calculation. See `reference-native-strings-copy-format` for API-specific results.

## Inclusive ends and sentinel searches

Document whether an end is inclusive or exclusive. Converting an inclusive
maximum index into a count requires adding one with overflow checked. A zero
count does not provide a last element. Sentinel-based loops need evidence that
the sentinel is reachable within valid initialized storage, or an independent
bound before every consuming load.

Constructed investigation: a delimiter scanner increments before testing its
bound. Follow the initial position, final load and branch order for empty and
delimiter-free inputs. A source-level condition in a decompiler is insufficient
if the machine has already loaded past the accepted range. A guard page fault
can expose the load, but failure to fault on a neighboring readable page does
not establish correctness.

## Sources and verification scope

Reviewed 2026-10-02. Extent ledgers and examples are constructed investigative
methods, not reproduced vulnerabilities. API/ABI details still need target scope.

1. [Linux malloc_usable_size](https://man7.org/linux/man-pages/man3/malloc_usable_size.3.html): diagnostic extent and excess-space caveat.
2. [C++ compound types](https://eel.is/c++draft/basic.compound): one-past and object identity.
3. [C++ pointer arithmetic](https://eel.is/c++draft/expr.add): array-bound restrictions.
