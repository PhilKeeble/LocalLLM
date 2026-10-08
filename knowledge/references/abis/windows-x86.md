---
id: abi-windows-x86
title: Windows x86 cdecl stdcall fastcall thiscall and stack evidence
kind: reference
topics: [abi, calling-convention, stack-cleanup, hidden-arguments, varargs]
platforms: [windows]
architectures: [x86]
---
# Windows x86 calling conventions

## Scope: Microsoft 32-bit x86 interfaces

These rules describe documented Microsoft x86 conventions, not every compiler
that emits x86 instructions. Do not carry the keyword's x86 behavior over to
x64/ARM targets, where many such keywords are ignored. Private optimized
functions, vectorcall, assembly and other compilers require separate evidence.
Record compiler/convention hypotheses before correcting decompiler prototypes.

## cdecl and stdcall arguments and cleanup

Microsoft x86 cdecl places stack arguments right-to-left and assigns argument
cleanup to the caller. stdcall also uses right-to-left stack arguments but the
callee removes them. Variadic calls use cdecl rather than relying on a callee
knowing the variable byte count. [1,2]

At ordinary entry, before any prologue, `[ESP]` holds the return address and
the first stack argument begins at `[ESP+4]`. Subsequent offsets depend on the
actual argument widths and hidden parameters, not a universal four-byte stride.
Cleanup may be folded into other stack adjustments. Track the complete stack
delta across call and return; absence of an immediate caller `add esp` is not
proof of stdcall.

## Microsoft x86 fastcall uses ECX/EDX for eligible arguments

Microsoft x86 fastcall assigns the first two eligible DWORD-or-smaller arguments
found left-to-right to ECX and EDX. Other arguments go on the stack; the callee
cleans stack arguments. Structs/classes/unions are stack arguments regardless
of small size under this documented rule. [3]

Distinguish register arguments from scratch values by following caller setup and
callee use. A small aggregate appearing on the stack is not inconsistent with
fastcall, and a stack-only parameter count can miss the register inputs.

## Microsoft x86 thiscall receiver and variadic-member differences

Ordinary nonvariadic Microsoft x86 thiscall passes `this` in ECX, remaining
arguments on the stack right-to-left, with callee cleanup. Variadic members use
cdecl: `this` is pushed last, becoming the first stack argument. [4]

Constructed example: in a nonvariadic thiscall `obj->f(int n)`, follow ECX to
object accesses and `[entry ESP+4]` to n. Do not call ECX an attacker-supplied
buffer before tracing the object source. A thunk can adjust `this` before
entering another body; preserve both object coordinates.

## Result storage and preserved registers

Ordinary Microsoft x86 scalar integer results use EAX; documented eight-byte
structure results can use EDX:EAX, whereas non-POD/large structures require
hidden result storage. ESI, EDI, EBX and EBP are preserved when used. [5]
Do not generalize EAX to every result category: floating/vector returns and
compiler-specific class eligibility require their actual interface contract.

For a hidden return, locate caller storage, the passed address, callee writes
and returned pointer. Determine its placement from the actual call, especially
for member functions and compiler variants. A hidden parameter can change the
apparent argument count and cleanup size; an inferred output buffer is not
automatically an externally controlled input.

## Decoration and stack evidence are supporting clues

Microsoft C-linkage x86 decoration commonly uses `_name` for cdecl,
`_name@N` for stdcall and `@name@N` for fastcall. N represents parameter-list
bytes; for fastcall it is not simply the number of bytes actually stacked.
C++ mangling and linker export aliases can obscure these clues. [1,2,3]

Constructed investigation: a `ret 8` is evidence of an eight-byte stack
adjustment by that return, not proof of two user-declared arguments. Combine
all exits, caller stack preparation, register uses, hidden parameters and
indirect-call type metadata. Record a custom convention if evidence contradicts
the named baseline; do not force the disassembly to match its decorated name.

## Sources and verification scope

Reviewed 2026-10-02 against Microsoft Learn. Constructed examples, not compiler
experiments. Calling-convention recovery requires caller and callee evidence.

1. [cdecl](https://learn.microsoft.com/en-us/cpp/cpp/cdecl?view=msvc-170).
2. [stdcall](https://learn.microsoft.com/en-us/cpp/cpp/stdcall?view=msvc-170).
3. [fastcall](https://learn.microsoft.com/en-us/cpp/cpp/fastcall?view=msvc-170).
4. [thiscall](https://learn.microsoft.com/en-us/cpp/cpp/thiscall?view=msvc-170).
5. [Argument passing and naming](https://learn.microsoft.com/en-us/cpp/cpp/argument-passing-and-naming-conventions?view=msvc-170).
