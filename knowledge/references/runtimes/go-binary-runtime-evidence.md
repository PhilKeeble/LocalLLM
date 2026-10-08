---
id: reference-go-binary-runtime-evidence
title: Go binary metadata, internal ABI and scheduler evidence
kind: reference
topics: [go, metadata, abi, symbols, runtime, goroutines]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm, arm64, riscv64]
---

# Go binary metadata and runtime evidence

## Scope and interpretation

Reviewed 2026-10-02 against official Go package documentation and compiler/runtime
design sources. Language contracts apply independently of executable format;
gc implementation layouts do not automatically describe gccgo, TinyGo or a
modified toolchain. Platform tags are not a promise that every implementation
supports every listed OS/architecture combination.

Here gc names the standard Go compiler toolchain; GC in memory discussions means
garbage collection. An ABI specifies machine-level value layout and call rules.

Recover artifact identity and implementation before applying private layouts.
An embedded version string is evidence to reconcile with machine code, not proof
that every object follows an assumed structure. Workflow: playbook-re-go-boundary.

## Embedded build information is attribution, not reachable-code proof

debug/buildinfo.Read and ReadFile inspect embedded build information in a binary
without executing it; most fields require a module-enabled build. In contrast,
runtime/debug.ReadBuildInfo describes the running binary, not an arbitrary file.
[Build-information reader](https://pkg.go.dev/debug/buildinfo).

BuildInfo describes the toolchain, main package/module, contributing dependency
modules and build settings. Settings can identify GOOS, GOARCH, compiler,
build mode, cgo configuration and VCS state; availability must be checked.
Record Module.Replace when present rather than attributing replacement code
solely to the original module's version.
[BuildInfo and BuildSetting](https://pkg.go.dev/runtime/debug).

Investigative inference: preserve the artifact hash alongside recovered fields.
A module entry does not prove a vulnerable function is present, reachable or
configured unsafely. Missing metadata is not proof the binary is not Go. Do not
execute an unknown program merely to ask it for information obtainable statically.
Compiler or dependency attribution alone also does not establish malicious intent.

## Function and line tables have their own coordinates

debug/gosym reads gc symbol/line tables. NewLineTable takes the table bytes and
the text-section start; Table exposes PC-to-function and PC-to-file/line mappings.
[gosym API](https://pkg.go.dev/debug/gosym).

Investigative consequence: keep file offsets, link-time addresses and loaded
addresses separate when locating tables and interpreting PCs. A plausible name
does not validate table boundaries. Check mapped extents, pointer width and
cross-references before using recovered names to assign a prototype or input
path. A source-line association does not prove an optimized instruction retains
the source variable's original lifetime or representation.

## Internal calls and value layouts are implementation evidence

The gc ABIInternal is explicitly unstable; ABI0 assembly calls can be connected
through wrappers. Do not substitute the OS C ABI. Arguments/results are assigned
wholly to registers or wholly to the stack; composite components consume
registers recursively. Reserved register-argument spill slots need not contain
copies of arguments. [Internal ABI: calls and memory layout](https://go.dev/src/cmd/compile/abi-internal).

The reviewed gc layout uses pointer/length/capacity for slices and pointer/length
for strings, with int-sized counts. Empty interfaces have type/data fields;
nonempty interfaces have itab/data fields. The itab supplies type/method evidence.
The data field may contain a direct pointer-word value or point to indirect
storage; do not assume every value is separately boxed. These are implementation
layouts, not a stable serialization format.

Investigative consequence: reconstruct the receiver, every component and returned
value at both sides of a call. A decompiler's apparent three scalar arguments may
be one slice. Resolve wrappers and metadata before labeling an indirect call as
an arbitrary function-pointer dispatch. Fixed internal offsets need toolchain
evidence, not merely an architecture match.

## Goroutines, threads and runtime stacks are distinct

The gc scheduler distinguishes G (goroutine), M (OS thread) and P (resources for
executing user Go code). G objects can be reused. User stacks can grow/shrink;
runtime code can switch to a thread's system stack. The current low-level G can
therefore be a system/signal G rather than the user goroutine.
[Runtime developer guide: scheduler and stacks](https://go.dev/src/runtime/HACKING).

Investigative consequence: a thread ID is not an enduring request/goroutine
identity. Separate stack-switching helpers from application recursion or unusual
control-flow transfers. Correlate request identity and observation time before
joining two traces; a recycled runtime-object address is not proof of the same
logical operation. Avoid fixed initial-stack sizes or private g/m/p offsets as
cross-version assumptions.

## Related factual homes

- reference-go-values-and-aliasing: logical values, lengths, aliasing and text.
- reference-go-concurrency-and-unwind: communication, cancellation and cleanup.
- reference-go-cgo-and-unsafe: native transitions, retention and unsafe storage.
