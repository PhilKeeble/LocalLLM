---
id: playbook-re-recover-cpp-lifecycle
title: Recover C++ object dispatch, lifecycle phases and cleanup paths
kind: playbook
topics: [cpp, vtables, rtti, inheritance, constructors, destructors, exceptions]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Investigate C++ machinery without assuming a source hierarchy

## Establish the ABI and retain competing layout hypotheses
Reviewed 2026-10-02. This local evidence workflow uses the ABI and language
sources below; it does not treat a compiler fingerprint as conclusive.

Record binary identity, target ABI, compiler clues, pointer width, loaded image
bases, RTTI configuration and relevant optimization limits. Select
abi-itanium-cpp-dispatch-layout or abi-microsoft-cpp-dispatch-rtti only when its
layout is supported. For an unknown variant, retain raw bytes and candidate
component roles rather than forcing a familiar class layout.

Separate candidate object address, subobject address, vptr/vbptr field address,
table address point and target function address. Save the exact loads and
relocations connecting them. A C callback table can resemble C++ dispatch;
table shape alone is insufficient to label the language or source class.

## Build a receiver-normalized dispatch packet
For each observed virtual call, retain receiver provenance, table slot byte
offset, entry width, candidate target set, incoming this adjustment and any
outgoing result adjustment. Identify whether a thunk changes the call interface.
Normalize each field access to a supported owner/subobject origin before
merging types; preserve unknown gaps and allocation capacity separately.

Use RTTI as corroboration: record the actual descriptor graph and offset
encodings rather than only a recovered name. Verify mapped ranges and reject
cycles or impossible offsets in a proposed parser interpretation. Missing RTTI
does not justify inventing a hierarchy; matching metadata does not prove the
receiver is live. Follow unknown indirect targets explicitly in the call graph.

## Reconstruct phases before classifying dispatch-pointer writes
Create a path-specific event sequence: storage acquired, bases/members completed,
current constructor phase, table stores, publication/callbacks, ordinary calls,
destructor phases and storage release. Pair each event with instruction or
runtime evidence and distinguish observed events from inferred ones.

Check whether a repeated table store matches a phase transition or originates
from an unrelated data write. For virtual inheritance, recover construction
tables/VTT or vbtable/vtordisp use under the chosen ABI. Do not combine a
base-phase field map and completed-object map without explaining the receiver
change. Publication during construction is an investigation lead, not by itself
proof of a race or reachable invalid call; retain synchronization and caller
conditions. Facts: reference-native-cpp-lifecycle-unwind.

## Add exceptional edges and partial-construction states
For each potentially throwing operation in scope, map the applicable EH range,
personality, handler/cleanup target, completed subobjects and still-owned
resources. Connect funclets or landing pads to the owning frame instead of
silently treating them as unrelated routines. Keep normal return, handled
exception, resumed propagation and termination paths distinct.

Distinguish base, complete and deleting destructor roles from actual allocator
release. Classify non-delegating versus delegating constructor failure before
assigning cleanup obligations. Follow a resource generation across aliases:
two calls on two different objects are not a same-object double destruction.
Do not add an edge between cleanup blocks merely because the decompiler prints
them sequentially. Missing EH decoding is a stated coverage gap, not proof of
no exceptional path.

## Sufficient output and bounded verification
Deliver an evidence packet with ABI confidence, partial hierarchy, normalized
offset map, dispatch targets, phase sequence and per-exit resource obligations.
For each proposed issue, provide a feasible path connecting attacker-influenced
input to the invalid access/state transition and identify the violated contract.
For a rejected issue, preserve the branch condition, phase or coordinate
correction that invalidated it without claiming whole-program safety.

Where authorized, a minimal compiler experiment or bounded debugger trace can
test one layout/phase hypothesis; record exact toolchain/options and specimen
differences. A constructed arithmetic check does not reproduce a target ABI.
Leave unresolved member-pointer encodings, indirect targets and unwind tables
explicit rather than supplying plausible-looking source declarations.

## Source basis
Reviewed 2026-10-02. Workflow is local synthesis, not an external prescribed procedure.

- [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html): object machinery; facts in abi-itanium-cpp-dispatch-layout.
- [Clang 21.1.0 Microsoft ABI implementation](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-21.1.0/clang/lib/CodeGen/MicrosoftCXXABI.cpp): scoped implementation evidence in abi-microsoft-cpp-dispatch-rtti.
- [C++ construction/destruction](https://eel.is/c++draft/class.cdtor) and [constructor unwinding](https://eel.is/c++draft/except.ctor): lifecycle facts in reference-native-cpp-lifecycle-unwind.
- [LLVM exception handling](https://llvm.org/docs/ExceptionHandling.html): distinct exceptional-flow models; use the target's actual personality and encoding.
