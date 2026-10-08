---
id: playbook-re-validate-decompilation
title: Validate disassembly, function boundaries and decompiler hypotheses
kind: playbook
topics: [reverse-engineering, disassembly, decompilers, function-discovery, prototypes, evidence]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Validate a reconstructed program

## Scope and required evidence

Use when a finding depends on decompiled types, missing parameters, apparent
uninitialized values, duplicated cleanup or suspicious control flow. Preserve
specimen hash, module/section coordinates, tool version, processor mode,
compiler specification and analysis overrides. Decompiler output is a model;
the question is whether the relevant machine operations support the finding.

Select the matching format and ABI references before interpreting a call.
`abi-windows-x64`, `abi-sysv-amd64` and `abi-aarch64-platform-conventions`
describe different contracts. OS syscalls and custom internal calls may differ.

## Check code and function boundaries

At each disputed range, record bytes, decoded instructions, incoming edges and
entry/unwind/symbol evidence. Check instruction mode, alignment, jump-table
targets and embedded data. Follow fallthrough only where it is valid; an
incorrect returning/non-returning classification can create fictitious code
and paths. Ghidra's analysis documentation demonstrates this failure mode. [1]

Treat inferred starts as candidates: corroborate with callers, exports,
callbacks or applicable unwind information. No single prologue signature is
required for all functions. For a jump into another region, test tail-call,
shared-epilogue and function-chunk explanations before splitting ownership.

## Resolve a disputed region without forcing a complete function inventory

Start from the finding's instruction and work outward through validated edges.
Retain separate classifications for entry candidate, instruction interval, data
interval and unresolved bytes. For each indirect transfer, record target formula,
selector domain and whether the recovered target set is exhaustive or partial.
Correlate exceptional continuations separately from ordinary returns. Do not
repair an unexplained edge by silently changing the entire region's code/data type.

Use `reference-native-function-boundaries-control-flow` for symbols, cold ranges,
callbacks, tail transfers and noreturn; `reference-native-code-data-padding` for
decoder/pool/alignment evidence; `reference-native-computed-dispatch-tables` for
table coordinates and guards. For transformed loops and shared bodies use
`reference-native-compiler-transformations`. These supply facts; preserve the
target-specific bytes and reasoning that connect them to this finding.

## Repair prototypes without circular reasoning

For the suspect call, tabulate each caller-defined register/stack value, width,
callee use, return use and preserved/clobbered location. Include hidden result
storage and this pointers. Compare several call sites when available. For
indirect calls, establish plausible targets instead of imposing one prototype
on unrelated callees.

Change an analysis signature only when evidence supports it; retain the old
hypothesis and the reason. Avoid broad type propagation until local errors are
resolved: Ghidra warns that early parameter analysis can spread bad signatures.
An attractive pseudocode result does not validate the type you supplied. [1]

## Keep a call-site evidence packet before propagating a signature

For each disputed call, retain target expression/target set, applicable ABI,
instruction coordinates, pre-call definitions and caller-visible results. Map
each candidate argument as location, consumed width, provenance, callee use and
remaining uncertainty. Separate receiver, hidden result, by-value copy, explicit
output pointer and ordinary input hypotheses. Record stack offsets relative to
the observed stack state, not a prologue-independent guessed frame.

Challenge the candidate against another caller and each feasible target. If only
one site supports a variadic or indirect signature, prefer a scoped override;
Ghidra documents those uses. [1] Keep unresolved locations rather than inserting
dummy source arguments to make pseudocode tidy. Accept a minimum supported machine
interface without claiming to recover unused original parameters. Use
`reference-native-prototype-argument-evidence` for promotion, hidden-copy and
result-consumption distinctions, then consult the matching ABI for placement.

## Validate data-flow and branch semantics

At the relevant sink, inspect original instruction operands and widths. Trace
definitions through casts, extensions, arithmetic, memory aliases and calls.
Check which instruction last set each consumed flag. Confirm signed/unsigned
conditions and exceptional exits. Do not use a pseudocode variable name as
object identity or evidence of initialization.

If using an intermediate representation, retain address spaces and operation
widths. Ghidra p-code distinguishes loads/stores, integer comparisons,
extensions and indirect branches; the IR operation and its correspondence to
machine instructions matter more than a rendered C expression. [2]

## Validate cleanup and apparent uninitialized reads

For repeated frees/destructors, enumerate predecessor conditions and unwind
edges and determine whether both releases can occur on the same object's
lifetime. For an apparent uninitialized value, locate the actual consuming
instruction and all feasible definitions. A debugger's optimized-out variable
is not an observed read of uninitialized storage. [3]

Constructed example: two decompiled cleanup blocks call the same destructor.
If branch predicates make the blocks mutually exclusive, that observation
refutes this two-release path; it does not establish safety of other paths.
Retain the rejected hypothesis and exact conditions to prevent rediscovery.

## Handoff and stopping conditions

Record the smallest corrected statement with coordinates: instruction fact,
supported high-level interpretation, reachable path and remaining uncertainty.
If bytes cannot be decoded reliably, a target is unresolved or an ABI is
unknown, state the missing edge rather than inventing source code. A bounded
runtime observation can test one uncertainty but does not prove every path.
Use playbook-validation-coverage-evidence to distinguish a missing recorded hit
from an established path constraint or incomplete collection; an observed subset
of indirect targets is not a complete recovered target set.

Sources reviewed 2026-10-02; procedure is a local evidence workflow informed by:

1. [Ghidra advanced analysis](https://ghidra.re/ghidra_docs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf): non-returning functions, signatures, data types and troubleshooting.
2. [Ghidra p-code operations](https://ghidra.re/ghidra_docs/languages/html/pcodedescription.html): loads/stores, branches, signed comparisons and extensions.
3. [GDB optimized code](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Optimized-Code.html): limits of source-level debugging.
