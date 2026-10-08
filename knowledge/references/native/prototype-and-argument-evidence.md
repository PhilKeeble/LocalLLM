---
id: reference-native-prototype-argument-evidence
title: Recovered prototypes, hidden arguments, variadic promotions and indirect-call evidence
kind: reference
topics: [prototypes, calling-conventions, hidden-arguments, varargs, indirect-calls, decompilers]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# A recovered signature is an interface hypothesis

## Declared parameters, passed values and consumed values are different sets
Reviewed 2026-10-02. Recover the machine interface from definitions and uses;
an assigned prototype is a hypothesis that can also influence later analysis.
For example, Ghidra documents that locally inferred call signatures can
differ from stored signatures and from each other; committing a signature changes
subsequent analysis. [1] Rendered parameter names are not independent evidence.

Investigation inference: a live register at a call can contain an argument,
linkage context, scratch state or unrelated remaining bits. A declared parameter
can also be unused by the optimized callee. Record caller definitions and callee
uses separately; absence of a use does not recover the original declaration's
argument count. Conversely, do not count a callee read after it overwrites the
register as an incoming argument. Use several call sites and feasible entries,
including tail transfers, before generalizing the machine interface.

## Pointer roles require provenance and use, not only a register position
For hidden-result and receiver placement, use the selected homes:
`abi-windows-x64`, `abi-sysv-amd64`, `abi-aarch64-platform-conventions`,
`abi-aapcs32-base-vfp-platforms` and the scoped MIPS/RISC-V/PowerPC references.
Ordinary ABI rules need not describe private optimized calls or raw syscalls.

Constructed investigation: the caller allocates an object, passes its address,
the callee initializes it and the caller consumes it afterward. This supports a
hidden-result hypothesis, but the same pattern can be an explicit output API.
Distinguish them using the target ABI/type metadata and other arguments. A pointer
used to select dispatch and access persistent fields supports a receiver/context
role, not necessarily the exact C++ source type. Do not turn internally supplied
result storage into an alleged attacker-input buffer without tracing provenance.

## LLVM sret and byval annotate roles that plain pointer syntax hides
In inspected LLVM IR, sret marks a pointer to source-level return storage; the
IR function returns void. byval implies a hidden pointee copy, whereas byref does
not imply a copy. [2] These are IR attributes, not labels inferred merely from
a machine pointer parameter or a decompiler's C-like spelling.

Constructed IR investigation: stores through a byval parameter can update the
copy without updating the caller's original object. Reporting caller corruption
requires identifying which storage is actually modified. An sret void IR return
does not mean the source operation produced no object. Conversely, a bare pointer
without those attributes supplies no such proof. Record IR revision, attributes,
calling convention and lowering stage; do not require an ABI's hidden-result
pointer to be returned in a register solely because another ABI does so.

## Variadic promotions precede architecture-specific argument placement
The current C++ draft applies default argument promotions to eligible arguments
without corresponding parameters: float promotes to double, and smaller ordinary
integer types promote to int when it represents their full range, otherwise
unsigned int. [3][4][5] This is not a rule for every named parameter.

Constructed target with eight-bit unsigned char and 32-bit int: passing value
255 and float 1.5 through ellipsis supplies int 255 and double 1.5. Inferring a
one-byte slot and a four-byte float from their original variable types loses the
call boundary representation. Recover named-versus-unnamed status, then use the
ABI's register/stack rules. A format string constrains expected consumption; it
does not prove the actual caller supplied matching arguments or that the string
was trusted. Do not count duplicated floating representations as extra arguments.

## Indirect signatures must follow the feasible target set
The current C++ draft makes calls through a non-call-compatible function type
undefined. [3] A cast in source-like output does not prove compatibility, and
source undefined behavior does not specify an automatic hardware fault.

Constructed dispatch: one path selects a two-argument handler, another selects
a thunk that adapts inputs before reaching a different body. Inspect the thunk
and target-specific argument uses rather than merging both bodies into one
guessed signature. An unresolved target remains an unknown interface; a single
observed target does not prove all others agree. Distinguish a local analysis
override from changing the inferred type of a shared table for every caller.
Use `reference-native-computed-dispatch-tables` for target-set completeness.

## Return-register residue is not automatically a return contract
Investigation inference: recover which result bits the caller actually consumes,
the callee definitions reaching each exit and applicable ABI result channels.
An untouched return register on one path can be irrelevant for a void function,
or a real missing definition if the caller consumes a required result. Ignoring
a returned value likewise does not prove the declaration was void.

Constructed case: a caller tests only the low byte after a call. That observation
supports an eight-bit consumption fact, not proof that the whole register is a
Boolean, signed status or pointer. Another caller may consume a wider value.
Keep output-buffer contents, status/flags and scalar results separate; success
semantics require the actual API contract. See `playbook-recover-service-boundary`
for raw service errors rather than applying an ordinary C return model to traps.

## A harness or debugger call must satisfy the recovered interface

Calling a recovered function with guessed arguments changes the evidence problem:
the adapter may violate the ABI or object preconditions before the target reaches
its ordinary input handling. Hidden return storage, receiver adjustment, stack
alignment, variadic promotion and callback signatures need evidence from the
actual interface. C++ function-pointer casts do not establish call compatibility. [3]

Constructed investigation: a direct-call adapter omits a hidden output buffer and
the callee writes through what the adapter thought was the first input argument.
That failure does not by itself show an input-validation bug in the real caller.
Recover the real argument roles, initialized state and feasible natural call path.
For vulnerability and malware investigations, use playbook-validation-faithful-harness
to distinguish a target operation from an effect manufactured by the adapter.

## Sources and limits
Reviewed 2026-10-02. Examples are constructed; no target compiler or executable
was run. C++ draft and LLVM pages are living references, not legacy-edition
guarantees. Tool training supplies analysis behavior, not normative ABI maps.

1. [Ghidra advanced analysis](https://ghidra.re/ghidra_docs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf): PDF pp. 33-37, saved/local signatures, Parameter ID and per-call overrides.
2. [LLVM parameter attributes](https://llvm.org/docs/LangRef.html#parameter-attributes): sret, byval and byref.
3. [C++ function calls](https://eel.is/c++draft/expr.call): call compatibility and ellipsis arguments.
4. [C++ integral promotions](https://eel.is/c++draft/conv.prom): ordinary narrow integer promotion conditions.
5. [C++ floating promotion](https://eel.is/c++draft/conv.fpprom): float-to-double.
