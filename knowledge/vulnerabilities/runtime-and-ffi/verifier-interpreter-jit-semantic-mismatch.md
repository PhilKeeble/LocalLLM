---
id: vulnerability-runtime-verifier-interpreter-jit-semantic-mismatch
title: Verifier, interpreter and JIT semantic mismatch
kind: vulnerability
topics: [verifier, interpreter, jit, ebpf, jvm, webassembly, type-confusion]
platforms: [cross-platform, kernel]
architectures: [any]
---

# Verifier, interpreter and JIT semantic mismatch

## Definition and violated invariant

This vulnerability occurs when a constrained-code verifier accepts a program using one model of types, ranges, control flow, helper effects, memory, numeric operations, or state merging, but the interpreter or generated native code executes the accepted program with a materially different meaning that violates the verifier's safety conclusion. The invariant is semantic agreement for every accepted instruction and reachable state across verification and all execution tiers.

Verifier rejection, an interpreter/JIT output difference, or generated native code alone is not a vulnerability. The mismatch must invalidate a security property such as memory isolation, control-flow validity, helper authority, or type safety.

## Conditions that establish the issue

Capture exact input program bytes, feature set, verifier and execution implementation/build, initial state, accepted abstract states, optimization or lowering path, and concrete execution. Identify the first instruction where abstract and concrete meaning diverge, then show how the divergence permits a state the verifier intended to exclude.

Account for signedness, width, wrap, shifts, pointer provenance, nullable/reference refinement, state joins, loops, exceptions/traps, helper side effects, memory growth, and tier transitions as applicable. Prove the affected tier actually executes.

## Evidence that is not sufficient

A verifier log, accepted unusual program, JIT compilation, helper call, range widening, trap, or crash is not sufficient. Conservative analysis can reject safe programs; accepted programs can trap safely; interpreters and JITs may use different internal representations while preserving language semantics.

Do not transfer one implementation's private verifier state or instruction encoding to another. A runtime version string without the loaded engine and feature configuration does not bind the observed semantics.

## Investigation sequence

Decode the program using the selected format and feature rules. Reproduce the verifier's control-flow graph and abstract state at each relevant edge, retaining how states merge. Separately recover interpreter behavior or generated instructions for the same operation and concrete state. Compare at the earliest disagreement rather than reasoning backward from a crash.

Trace the invalid state to its first protected consumer: memory access, indirect call, privileged helper, object field, return value, or host import. For tiered execution, include entry guards, on-stack replacement, deoptimization, code identity, and whether fallback repairs or preserves the state.

## Constructed range mismatch

```text
program:   r2 = attacker_value; r2 <<= 32; r2 >>= 32; load8 [safe_base + r2]
verifier:  models the second shift as preserving a nonnegative bounded 32-bit value
executor:  performs an arithmetic right shift of a signed 64-bit value, producing a negative offset
```

This hypothetical trace establishes a useful mismatch only if the instruction definitions and operand widths actually differ as stated, the verifier accepts the program with the claimed bound, and execution reaches the load with an out-of-range address. Real eBPF, JVM, and WebAssembly operations have distinct shift, typing, and memory rules; do not apply this invented sequence to them by analogy.

## Native-code representation

At a JIT boundary, compare the verifier's abstract operation with the selected machine instruction and extensions. For example, `shr r64, n` and `sar r64, n` implement logical and arithmetic right shifts; choosing one can matter only when the source semantics distinguish them and the operand can have its high bit set. One mnemonic discrepancy is not proof until register width, incoming range, masking of shift counts, and resulting protected access are established.

## Primitive and impact limits

The primitive is execution of a verifier-forbidden concrete state after acceptance. Impact depends on its first consumer and the runtime boundary: guest linear-memory corruption, host or kernel memory access, invalid reference use, or unauthorized helper invocation require separate proof. An engine crash supports availability impact only on the exercised path.

## Primary sources and scope

Reviewed 2026-10-09 against Linux kernel [eBPF verifier documentation](https://docs.kernel.org/bpf/verifier.html), the JVM Specification's [class-file verification rules](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-4.html#jvms-4.10), and WebAssembly's [validation](https://webassembly.github.io/spec/core/valid/index.html) and [execution](https://webassembly.github.io/spec/core/exec/index.html) semantics. The example is intentionally runtime-neutral and does not assert a defect in those implementations.
