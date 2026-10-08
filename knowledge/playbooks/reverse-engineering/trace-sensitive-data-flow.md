---
id: playbook-re-sensitive-data-flow
title: Trace binary input and malware configuration to sensitive operations
kind: playbook
topics: [reverse-engineering, data-flow, taint, aliases, reachability, guards, invariants, malware-analysis, vulnerability-analysis]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Sensitive data-flow investigation

A source introduces the value being followed; a sink consumes it in an operation
of interest. Data flow follows those values through transformations and storage.
For vulnerabilities, establish attacker influence and a violated contract. For
malware analysis, recover behavior and its enabling conditions; the behavior need
not involve a software bug or input controlled by a victim.

## Bound the source and sink

State the actor/input source and the precise sensitive operation: allocation,
copy, index, file access, authorization, dispatch, process creation or response.
Record module identity and coordinates at both ends. An external input exists
only to the extent that the actor can influence the observed field and path;
an API import is not evidence that the actor reaches its call site.

Forward tracing answers what the input influences. Backward tracing answers
which definitions can reach the sink. Use both until they meet on the same
value, object and feasible execution context. Keep unproven edges explicit.

## Malware data flow: configuration, command dispatch and transferred data

Choose a concrete question: which decoded field selects an operation, which
destination receives collected data, or which path is written or executed?
Follow embedded configuration, user input or received messages as appropriate;
do not assume every source is attacker-controlled merely because the specimen
is suspicious. Preserve decoding steps and the exact bytes consumed afterward.

For command dispatch, connect selector, accepted branch, handler and effect.
For suspected exfiltration, connect collected data, transformations and the
outbound buffer rather than reporting unrelated collection and network APIs.
Distinguish static capability from observed execution and explain unresolved
environmental or server-response conditions. This is a behavior-recovery method,
not an automatic verdict about intent or attribution.

## Track widths, units and versions of values

For each transform record input/output widths, signedness, unit, arithmetic,
range restrictions and storage location. Give modified values distinct names
in the evidence ledger. Preserve the exact version validated by a guard and
the exact version consumed at the sink.

A memory reload is a new observation if another thread, callback or peer can
change storage between check and use. A local copy can stabilize bytes but
does not authenticate their contents or extend the lifetime of referenced
objects. Follow aliases to their shared storage and ownership.

## Evaluate guards and path feasibility

A guard dominates a sink in a control-flow graph when every graph path to that
sink passes the guard. Dominance alone is insufficient: verify the accepted
branch, compared value/version, width/unit and any mutations afterward. Include
error, exception, cancellation and reentrant paths omitted by a simple graph.

For each candidate path collect predicates. Conditions such as state==OPEN
and state==CLOSED cannot both describe one unchanged state; show an intervening
transition if the path requires both. A syntactic data-flow connection is not
proof of a feasible execution. A solver result depends on faithful models of
calls, widths, memory and environmental constraints.

## Cross calls and component boundaries

Recover argument/return locations using the actual ABI and track caller-owned
buffers, hidden result storage and side effects through output parameters.
For an unresolved call, preserve the uncertainty about writes, escapes and
returned values; do not silently assume it sanitizes data or has no effects.

Across IPC/FFI, compare both contracts: identities, framing, field units,
serialization, normalization, ownership and lifetime. Input to the next
component must be tied to the previous component's actual output. The existing
`playbook-vr-evidence-and-chaining` defines the evidence classes for that claim.

## Constructed size-flow example

Hypothetical path: a 32-bit count n is checked, converted to 16-bit m, then
allocation uses m while copying uses n. Preserve the two values separately.
Ask whether the original guard permits n above the 16-bit maximum, whether
the allocation can succeed, and whether the copy consumes the original count
with the same unit. If any required edge is absent, report a candidate.

A bound on n below the narrowing threshold can refute this mismatch; a check
on m afterward may not constrain the original n. See
`reference-native-integer-size-buffer-arithmetic` for the conversion contract.

## Verification and reference use

When a call effect, alias, value or identity remains uncertain, first inspect
available call-site, implementation and API-contract evidence. If separately
authorized runtime evidence is needed, use bounded isolated observation and report
that build/input separately from the claimed path set. Preserve the first invalid
operation and earliest missing edge, not only a final crash. Unknown calls remain
unknown when no faithful evidence is available; do not execute a specimen merely
to complete a worksheet.

For multi-platform questions, retrieve each platform's contract independently
and compare scoped claims. Missing material in a bounded search packet is not
negative evidence; narrow the query, use exact metadata filters or read the
identified source. Contradictory claims require checking scope/version before
combining them.

## Build a bidirectional slice that meets on one execution context

Start forward at the controllable input field and backward at the exact sink
operand. Record each edge as instruction/call site, value version, width/unit,
memory range or argument binding, path predicate and evidence status. Stop at
unknown definitions explicitly instead of bridging them with a guessed name.

At loads, trace both the address and reaching contents. At stores, preserve
partial-byte writes and possible aliases. At calls, include return registers,
output parameters, globals/heap effects, ownership, escapes and exceptional
outputs. Match ordinary returns to the invocation that supplied the arguments.
Forward and backward results that meet only at the same function name are not
yet a connected path. Facts and counterexamples:
reference-native-data-flow-alias-call-context.

## Record the obligation that each guard actually establishes

For every credited check, record the accepted edge, compared value version,
signedness, unit, checked object/capacity and how these reach the sink unchanged
or through a justified transform. Include aliases, callbacks and state changes
that might invalidate the relation. Distinguish a range restriction from
authorization or lifetime validity; do not treat one as a substitute for another.

Retain correlations across joins and iterations. Reject contradictory conditions
only for the same unchanged value/context. Add exceptional edges from the actual
unwind mechanism and keep success-only outputs off failure paths. If an indirect
edge is unresolved, qualify the path and dominance result. Counterexamples:
reference-native-path-feasibility-guards.

## Validate a constraint model before promoting its conclusion

Specify whether the question is sink reachability or violation of a particular
bound/state/ownership contract. Include machine widths, memory identity, input
domain and the same value/object used by the operation. Record solver/tool
version, constraints, call summaries, concretization, search limits and excluded
states. Keep SAT, UNSAT, unknown, timeout and runtime observation distinct.

For a candidate model, evaluate its values against each recovered instruction
and external contract before execution. Use only authorized isolated execution
for reproduction. A mismatch should refine the model or reject the path, not
be hidden by adding assumptions that force the desired result. Deliver the
earliest uncertain edge and the smallest supported conclusion. A correct
arithmetic example alone does not validate a target path.

## Sources and scope

Reviewed 2026-10-02. This is a general local investigation method, not a claim
that any automatic taint engine proves reachability. The example is constructed.

- [Ghidra p-code operations](https://ghidra.re/ghidra_docs/languages/html/pcodedescription.html): typed-width operations, memory and control transfers used to inspect value flow.
- [LLVM language reference](https://llvm.org/docs/LangRef.html): SSA/phi, calls and memory semantics; relevant only when LLVM IR is the analyzed representation.
- Local evidence contracts: `playbook-vr-evidence-and-chaining`,
  `reference-native-integer-size-buffer-arithmetic`, `abi-windows-x64`,
  `abi-sysv-amd64` and `abi-aarch64-platform-conventions`.
