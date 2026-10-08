---
id: reference-go-values-and-aliasing
title: Go interface values, slice aliasing, strings and integer boundaries
kind: reference
topics: [go, interfaces, slices, strings, aliasing, integer-overflow]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm, arm64, riscv64]
---

# Go values and investigation boundaries

## Scope

Reviewed 2026-10-02 against the Go specification, official explanations and
standard-library contracts. These are logical value rules; private machine
layouts belong to reference-go-binary-runtime-evidence. Memory safety does not
establish application authorization, semantic length correctness or safe native
interop. Unsafe constructions require reference-go-cgo-and-unsafe.

## A nonnil interface can contain a nil pointer

An interface holds a dynamic type and value. A typed nil pointer stored in an
interface leaves that interface nonnil; this includes error values. Comparing
the interface with nil does not establish a nonnil underlying pointer.
[Go FAQ: nil error values](https://go.dev/doc/faq#nil_error).

Type assertion x.(T) panics on failure; the two-result form yields a success
Boolean instead. A successful assertion to a pointer type does not establish
a nonnil pointee. [Specification: type assertions](https://go.dev/ref/spec#Type_assertions).

Investigative consequence: distinguish the dynamic-type check, nil check and
receiver dereference. Trace which check controls the sink. Do not classify an
interface check as missing merely because the data word alone is zero, or assume
an error interface accurately reflects the programmer's intended success state.

## Slice copies do not copy the backing elements

A slice describes part of an array; reslicing shares storage. Its length counts
visible elements, while capacity describes how far that view can extend into
the backing array. Reslicing can expose elements beyond the current length up
to capacity. copy copies only the smaller source/destination length and supports
overlap. [Go slices: usage and internals](https://go.dev/blog/slices-intro).

Investigative consequence: identify the backing allocation and all views, not
just the current slice variable. Passing a slice or saving it in a request does
not create a snapshot. A later producer overwrite can change a consumer's input
without freeing memory. A short copy can be valid Go yet leave application data
incomplete; check the returned count and the destination's subsequent use.

## Append can preserve or split aliases

append reuses existing capacity when sufficient and allocates new backing storage
otherwise; the returned slice must be retained. Growth is not an unconditional
allocation or a fixed doubling contract. [Built-in append](https://pkg.go.dev/builtin#append).

The full slice form a[low:high:max] sets capacity to max-low while still sharing
elements. [Specification: full slice expressions](https://go.dev/ref/spec#Full_slice_expressions).

Investigative consequence: analyze both append branches. A capacity-limited view
can prevent an append from overwriting a neighbor through that view, but it does
not isolate writes to existing elements. A narrow view can also retain a much
larger backing allocation; logical payload size alone is insufficient evidence
for memory-retention accounting.

## String length, byte positions and decoded characters differ

Go strings contain immutable bytes, not necessarily valid UTF-8. Indexing reads
bytes; range decodes UTF-8 and reports byte positions. A rune is a code point,
not necessarily a complete user-perceived character. Go does not automatically
normalize text. [Strings, bytes, runes and characters](https://go.dev/blog/strings).

utf8.DecodeRuneInString returns RuneError with width 1 for invalid nonempty
encoding and width 0 for empty input. A valid encoded replacement character
must not be confused with malformed input merely because the rune value matches.
[UTF-8 decoding](https://pkg.go.dev/unicode/utf8#DecodeRuneInString).

Investigative consequence: annotate each limit and offset with its unit. Preserve
original bytes when comparing validator and consumer behavior. An embedded NUL
is data in a Go string but may terminate a native C-string consumer. UTF-8
decoding is not path canonicalization, authorization or application grammar
validation. Check malformed-input handling rather than assuming string typing
performed validation on construction.

## Integer safety is not automatic overflow rejection

Go runtime integer overflow does not generally panic: unsigned arithmetic wraps,
and signed overflow has defined results rather than C-style undefined behavior.
[Specification: integer overflow](https://go.dev/ref/spec#Integer_overflow).

Investigative consequence: reconstruct widths, sign and conversions before
evaluating allocation/count relationships. A later bounds panic may prevent a
particular memory access without repairing an earlier quota bypass, truncated
native count or incorrect accepted length. Check the invariant before arithmetic
loses information; distinguish panic-driven denial of service from an actual
out-of-bounds native access.
