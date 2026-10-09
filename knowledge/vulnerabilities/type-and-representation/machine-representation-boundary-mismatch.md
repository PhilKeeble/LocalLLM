---
id: vulnerability-type-machine-representation-boundary-mismatch
title: Machine-representation mismatch across a boundary
kind: vulnerability
topics: [endianness, bitfields, padding, scalar-width, serialization, abi]
platforms: [cross-platform]
architectures: [any]
---

# Machine-representation mismatch across a boundary

## Definition and violated invariant

A machine-representation mismatch occurs when a producer and consumer assign different values or field boundaries to the same bytes because they disagree about byte order, bit numbering, bitfield allocation, padding, alignment, scalar width, signedness, floating representation, or native-versus-wire encoding. Each boundary must define an explicit byte representation or use a demonstrably identical ABI contract at both ends.

This differs from ordinary parsing of a deliberately different wire format: conversion is expected there. The vulnerability is the reachable omission, duplication, or inconsistent application of the required conversion or layout rule.

## Conditions that establish the issue

Preserve the raw bytes and recover the producer's encoding, consumer's decoding, target ABI, load width, extensions, swaps, masks, shifts, packing, and final use. Prove the two interpretations differ for a feasible attacker-influenced value and that the mismatched value reaches a security-relevant bound, allocation, pointer, state, operation, or output.

For bitfields, do not derive allocation order from processor endianness. For copied native structures, include padding, compiler layout, language ABI, architecture width, and whether every transferred byte was initialized.

## Evidence that is not sufficient

A byte-swap instruction, packed structure, unaligned load, cross-platform protocol, or different decompiler types is not sufficient. Conversion may occur in another layer, both peers may use the same defined encoding, or the loaded bytes may never affect a sensitive consumer.

An incorrect decoded value is not automatically a memory-safety issue when later validation rejects it or treats it only as inert data.

## Investigation sequence

Write the raw boundary bytes once, then derive the producer value and consumer value separately with explicit widths and byte order. Follow every transformation without silently replacing a wire value with a native one. Record where sign or zero extension and truncation occur.

Compare the final decoded value with the independent buffer extent, object layout, allowed semantic domain, and consumer operation. For mixed-format containers, repeat this per field rather than assigning one byte order to the entire object.

## Constructed little-endian Windows x64 example

```c
uint16_t length;
memcpy(&length, message, sizeof(length)); /* message stores a big-endian length */
consume(message + 2, length);
```

```asm
movzx eax, word ptr [rcx]     ; native little-endian load, with no byte-order conversion
add   rcx, 2
mov   edx, eax
call  consume
```

With `message` initially in `RCX` under Windows x64, input bytes `00 20` encode the wire value 32 while the shown little-endian load produces `0x2000`, or 8192; the adjusted pointer remains in `RCX` and the length is passed in `EDX`. This establishes a decoding mismatch under the stated format and architecture; an overread additionally requires `consume` to trust that length beyond the actual payload rather than validate it.

## Primitive and impact limits

The direct result is a wrong decoded value or layout. Consequences can include incorrect allocation, out-of-bounds access, state or permission confusion, disclosure of padding, or protocol desynchronization. Impact depends on the final consumer and its independent checks.

## Related knowledge and primary sources

`architecture-machine-representation`, `reference-native-structure-layout-access`, and parser-format references define the relevant representation and boundary evidence. This profile repeats the producer-to-consumer proof locally.

Reviewed 2026-10-09 against the C++ [endian definitions](https://eel.is/c++draft/bit.endian), [bitfield allocation rules](https://eel.is/c++draft/class.bit), and [object representation rules](https://eel.is/c++draft/basic.types). The source, assembly, and byte sequence are constructed.
