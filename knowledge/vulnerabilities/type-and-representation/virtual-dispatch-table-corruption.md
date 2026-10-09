---
id: vulnerability-type-virtual-dispatch-table-corruption
title: Virtual-table, interface-table, or dispatch-slot corruption and misbinding
kind: vulnerability
topics: [control-flow, vtable, dispatch, function-pointers, type-confusion]
platforms: [cross-platform]
architectures: [any]
---

# Virtual-table, interface-table, or dispatch-slot corruption and misbinding

## Definition and violated invariant

A dispatch-table vulnerability occurs when an object or dispatcher selects a function table or slot that does not belong to its live type, interface, state, or operation. Causes include memory corruption, stale or wrong-type objects, incorrect interface adjustment, mutable registration tables, unchecked indexes, and copying an incomplete member-pointer representation.

Indirect dispatch is normal compiler and application behavior. The finding requires corrupted or misbound control data and a reachable call, not merely a load from a read-only table.

## Conditions that establish the issue

Identify the dispatch object's construction and lifetime, table-field writer, expected table identity, slot calculation, receiver/context adjustment, feasible target set, and indirect call. Prove attacker influence or an invariant violation changes the selected table, slot, or receiver and reaches an unintended callable target.

Apply the target ABI: C++ vfptrs, virtual-base tables, COM interface tables, Rust trait-object vtables, and custom callback arrays have different shapes and ownership rules.

## Evidence that is not sufficient

A pointer at object offset zero, table in read-only memory, indirect call, repeated constructor table stores, or missing RTTI is not sufficient. Construction/destruction phases, thunks, and custom dispatch can explain these patterns.

Control of object data does not automatically control the call target when CFI, pointer authentication, read-only tables, or validated slot sets constrain dispatch; inspect effective policy.

## Investigation sequence

Trace every write to the table or slot source and bind it to object generation and phase. Recover slot index, entry width, target, receiver adjustment, and arguments at the call. Enumerate feasible legitimate tables rather than naming one from symbols alone.

If another memory bug corrupts dispatch, preserve that root cause and describe table control as a resulting execution primitive. Verify mitigation coverage on the affected build.

## Constructed machine example

```asm
mov  rax, [rcx]           ; load object's dispatch-table pointer
mov  rax, [rax+18h]       ; select slot three on this constructed 64-bit table
call rax                  ; RCX remains the receiver
```

This is ordinary virtual-style dispatch until evidence shows `[RCX]` can contain a table not valid for the live receiver or that slot three is misindexed. If an adjacent overwrite controls `[RCX]`, the sequence can become a controlled indirect-call primitive, but target usability and CFI or pointer-authentication policy remain separate.

## Primitive and impact limits

The direct primitive is unintended indirect dispatch with some degree of target and argument control. Code execution requires a reachable usable target and satisfaction or bypass of active control-flow defenses; a bad table can instead fault immediately.

## Related knowledge and primary sources

`abi-microsoft-cpp-dispatch-rtti`, `abi-itanium-cpp-dispatch-layout`, and runtime dispatch references define concrete table forms. This profile repeats object/table/slot/receiver binding locally.

Reviewed 2026-10-09 against the [Itanium C++ ABI virtual-table layout](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#vtable), Clang's [Microsoft C++ ABI implementation](https://github.com/llvm/llvm-project/blob/main/clang/lib/CodeGen/MicrosoftCXXABI.cpp), Rust [trait objects](https://doc.rust-lang.org/reference/types/trait-object.html), and [MITRE CWE-843](https://cwe.mitre.org/data/definitions/843.html). The assembly is constructed.
