---
id: vulnerability-kernel-native-compat-ioctl-layout-confusion
title: Native and compatibility ioctl layout confusion
kind: vulnerability
topics: [kernel, drivers, ioctl, compat, abi, structure-layout]
platforms: [linux, android, windows]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# Native and compatibility ioctl layout confusion

## Definition and violated invariant

This vulnerability occurs when a kernel or driver interprets a request using a layout, pointer width, alignment, command size or transfer direction different from the caller ABI that produced it. The invariant is that dispatch and field decoding must use the exact command, caller ABI and buffer contract, and conversions must yield one validated native representation.

Compatibility handling is not simply truncating every pointer. Fixed-width fields, handles, padding, embedded pointers and alignment can differ independently. On Windows, WOW64 does not automatically translate driver-defined IOCTL payloads; on Linux, compat handlers must preserve the user ABI.

## Conditions that establish the issue

Bind device, complete command value, caller bitness and ABI, selected native or compat handler, transfer method, supplied lengths and actual request layout. Show a field is read from the wrong offset or width, a pointer or size is converted incorrectly, or command metadata causes an incompatible buffer interpretation that reaches a security-relevant consumer.

Prove the caller can reach the affected ABI path. A 32-bit layout bug on a target without compatibility execution is not reachable.

## Evidence that is not sufficient

A compat function, `long`, pointer field, structure cast, encoded command size or size mismatch is not sufficient. The handler may translate explicitly, use fixed-width wire fields or reject incompatible callers. Encoded ioctl size and direction are metadata, not independent proof that the handler validates or follows them.

A decompiler's structure type is not authoritative. Reconstruct offsets from machine accesses and caller construction.

## Investigation sequence

Decode the full command and map it to dispatch. Recover each caller layout and native target layout with offsets, widths, alignment and padding. Trace conversion, reserved-field checks and embedded object capture. Compare input and output lengths with every accessed range under both ABIs.

At binary level, annotate 32- versus 64-bit loads, sign/zero extension and pointer canonicalization. Identify whether a compat pointer becomes a user address under the platform helper rather than through an unsafe cast. Follow converted values into allocation, copy and authority checks.

## Constructed layout

Assume a hypothetical 32-bit request encodes `{ uint32_t ptr; uint32_t len; }` as eight bytes, while the native 64-bit structure is `{ void *ptr; uint32_t len; }` with `len` at offset eight. Casting the eight-byte compat buffer to the native type can read the 32-bit `len` as the upper half of a pointer and read a native `len` beyond the supplied object.

This is an explanatory layout, not a universal ABI. Packing and alignment must be recovered for the actual compiler, architecture and interface.

## Primitive and impact limits

The direct result can be wrong pointer, length, command, direction or response interpretation. Consequences range from clean rejection to out-of-bounds access or privileged operation on the wrong object. RCE or elevation requires the downstream primitive and boundary to be established.

## Related knowledge and primary sources

`reference-linux-kernel-interface-representations`, `reference-windows-wow64-layouts-views` and driver IOCTL references provide the platform contracts. This profile retains the cross-ABI comparison locally.

Reviewed 2026-10-09 against Linux kernel [ioctl interface guidance](https://docs.kernel.org/driver-api/ioctl.html), Microsoft [IOCTL definitions](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes) and Microsoft [WOW64 implementation details](https://learn.microsoft.com/en-us/windows/win32/winprog64/implementation-details). The layout is hypothetical.
