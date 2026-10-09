---
id: vulnerability-memory-stack-out-of-bounds-write
title: Stack-based out-of-bounds write
kind: vulnerability
topics: [memory-safety, out-of-bounds-write, stack, control-flow]
platforms: [cross-platform]
architectures: [x86, x64, arm, arm64]
---

# Stack-based out-of-bounds write

## Definition and invariant

A stack-based out-of-bounds write occurs when code writes outside the intended extent of an automatic object in a stack frame. For an object occupying `[base, base + capacity)`, every written byte must remain inside that half-open range. The defect begins at the first byte outside the object, even when the write remains inside reserved stack-frame space and does not immediately fault.

This issue is also called a stack buffer overflow, but it is distinct from stack exhaustion caused by excessive recursion or unusually large frames. It establishes a memory-corruption primitive; it does not by itself establish control of a return address or code execution.

## When it is a security problem

The issue is security-relevant when a less-trusted source can influence a write's offset, width, count, terminator, or source data and a reachable path permits the resulting write range to exceed a local object's capacity. Confirm the object's actual extent, the complete destination range, and any dominating validation before classifying the path.

Impact depends on what follows the object in the realized frame and whether the corrupted value is later used. Possible targets include padding, another local, a security cookie, a saved register, exception or unwind state, and saved control data. Their placement is compiler-, ABI-, optimization-, and build-dependent.

## What does not establish the issue

A call to a copy routine, a stack-local array, a crash near a return instruction, or an apparently absent check in one basic block is not sufficient evidence. A caller or earlier branch may prove the bound, an inlined operation may have a different effective extent, and a decompiler may infer the wrong array size or merge several stack slots.

The presence or absence of a visible stack cookie also does not prove or disprove the write. A cookie is a detection mechanism for certain corruptions; it neither defines the destination object's bounds nor covers every stack object and overwrite pattern.

## Investigation workflow

Start at the input boundary and preserve the exact width, signedness, units, and transformations of every value that contributes to the destination address or write length. Recover the local object's base and capacity from allocation, initialization, and use evidence rather than from a decompiler declaration alone.

For each write, calculate `[destination + offset, destination + offset + write_size)` and compare it with the local object's range. Account for multiplication, terminators, loop exit conditions, partial-copy behavior, and integer narrowing. Then verify that every path to the write is dominated by an adequate bound and that errors stop later use. Treat frame layout and impact as a separate analysis after the object-level violation is established.

## Constructed source example

This hypothetical function copies an externally supplied byte sequence into a 32-byte local object:

```c
void parse_name(const unsigned char *src, size_t len)
{
    unsigned char name[32];
    memcpy(name, src, len);
    consume(name, sizeof(name));
}
```

On the shown path, `len > 32` makes the copy exceed `name`. The snippet is vulnerable only if `len` can exceed 32 at runtime: a verified caller contract or a dominating check outside the excerpt can make this path safe. `consume` is included only to keep the local object's later use visible; it is not part of the bounds error.

## Constructed Windows x64 representation

The following unprotected assembly is one possible lowering of the example. Under the Windows x64 calling convention, `src` arrives in `RCX`, `len` in `RDX`, and the first four integer arguments use `RCX`, `RDX`, `R8`, and `R9`.

```asm
sub  rsp, 48h
mov  r8, rdx             ; memcpy count = len
mov  rdx, rcx            ; memcpy source = src
lea  rcx, [rsp+20h]      ; memcpy destination = name
call memcpy
lea  rcx, [rsp+20h]
mov  edx, 20h
call consume
add  rsp, 48h
ret
```

In this constructed frame, `name` occupies `[rsp+20h, rsp+40h)` after the subtraction. The saved return address is at `[rsp+48h]`, so the write becomes out of bounds after 32 bytes; a 41-byte copy first reaches the return address at byte offset 40 from `name`. A real build may use a different layout, inline the copy, add a security cookie, or retain values in different registers.

## Primitive and impact conditions

The direct primitive is a write past a stack object's end. Record separately how many bytes can be written, which byte values are controlled, whether the offset is fixed or variable, and whether execution continues to a use of corrupted state.

A crash supports denial-of-service impact on the exercised path. A control-flow claim additionally requires evidence that reachable controlled bytes affect saved control data or another control-bearing value. A code-execution assessment must also account for active protections and the available continuation, including stack-cookie checks, hardware shadow stacks where present, control-flow restrictions, executable-memory policy, and address randomization. Do not infer those conditions from the overflow alone.

## Related knowledge contracts

- `reference-native-bounds-objects-terminators` defines object extents, half-open ranges, and terminator accounting.
- `reference-native-integer-size-buffer-arithmetic` covers integer width, overflow, truncation, and allocation/use mismatches.
- `abi-windows-x64` owns Windows x64 argument, stack, and nonvolatile-register rules.
- `reference-windows-cet-shadow-stack` and `playbook-re-windows-mitigation-evidence` own mitigation-specific interpretation.
- `playbook-vr-evidence-and-chaining` separates observation, reachability, consequence, and final impact.

## Scope and primary sources

This profile describes the durable object-bounds reasoning used across native platforms. The assembly is a deliberately simple Windows x64 example, not a signature or a promise about compiler output.

Primary references reviewed for this draft:

- MITRE CWE-121, *Stack-based Buffer Overflow*: <https://cwe.mitre.org/data/definitions/121.html>
- Microsoft, *x64 calling convention*: <https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention>
- Microsoft, *x64 stack usage*: <https://learn.microsoft.com/en-us/cpp/build/stack-usage>
- Microsoft, */GS (Buffer Security Check)*: <https://learn.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check>
