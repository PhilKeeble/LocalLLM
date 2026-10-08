---
id: reference-validation-coverage-reachability
title: Execution coverage units, reachability, missing events and security-evidence limits
kind: reference
topics: [coverage, reachability, control-flow, branches, fuzzing, negative-evidence, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Coverage is a scoped observation of execution

## Function, block, edge and source coverage answer different questions

Record the collection unit rather than using coverage as an unqualified number.
LLVM documents function-entry, basic-block and edge instrumentation [1], while
source-based reporting separately defines function, instantiation, line, region
and branch statistics [2]. These are supporting examples, not required tools.

| Unit | What a hit establishes within the collection model |
| --- | --- |
| Function entry | Execution reached an instrumented entry point |
| Basic block | Execution reached a recorded straight-line code block |
| Edge | Execution traversed a recorded control-flow transition |
| Source line/region | A mapped source unit was attributed execution |
| Branch outcome | A mapped condition took a recorded outcome |

A function hit does not imply its sensitive operation completed. A line can
contain several conditions or regions. A named function may have multiple
template/inline instantiations; aggregate function coverage need not distinguish
them. Bind the report to its actual code and mapping before naming a reached
operation. An event at block entry does not guarantee all later instructions
finish without fault or interruption.

## Covering blocks does not necessarily cover every edge between them

Constructed graph: entry P either executes optional Q or skips it; both routes
reach R. Observing P,Q,R on one execution covers those three blocks but does not
show the P-to-R skip edge. LLVM's edge-coverage discussion demonstrates this
general distinction using a conditional block. [1]

Investigative consequence: a recorded handler and cleanup block do not establish
every path between them. Likewise, separate executions covering all edges need
not establish every multi-edge sequence, loop count or interleaving. Retain the
actual predecessor and state when the finding depends on a particular ordering.
Static path feasibility remains a separate question in
reference-native-path-feasibility-guards.

## Instrumentation and report denominators limit percentages

Compiler coverage can deliberately omit redundant points; LLVM's block/edge
instrumentation documents such pruning and exclusion controls. [1] A report also
depends on selected binaries/modules, generated code, threads, execution window
and available mapping. A percentage needs its numerator, denominator and scope.

Investigative consequence: 100% of recorded entries is not 100% of deployed code,
states or input values. A rebuilt binary, altered filters or different entry
boundary can change the measured set. Do not compare raw totals across such
changes as though they counted the same events. Absence from the denominator is
different from a present point with zero observed hits.

## A feedback feature is not necessarily a unique executed path

Fuzzing feedback may combine edge presence, hit-count information, comparison
values or indirect-call relationships. LLVM's fuzzing documentation explicitly
distinguishes its combined feature count from reported block/edge coverage. [3]

Investigative consequence: a new feature can reflect a new value or count at
already reached code. An unchanged feature set can conceal new identities,
objects or policy outcomes. If a collector hashes several events into a finite
map, establish its collision behavior before interpreting a map entry as one
unique location; do not assume every collector uses hashing. No feature count is
a count of confirmed vulnerabilities or proof of exhaustive semantic exploration.

## Identical paths can process security-relevant different values

Constructed case: a copy exercises the same recorded control-flow edges with lengths 4
and 64, but the destination has capacity 8. Path presence alone does not identify
the violated bound. A separate access/extent analysis or suitable detector is
needed. Conversely, taking a new error branch can be correct rejection.

For logic bugs, the same handler can use a different principal, object generation
or authorization decision. For malware, reaching an API-call site does not alone
show its arguments, successful return or asynchronous completion. Join control
flow to data, authority and effects; use playbook-re-sensitive-data-flow and
playbook-validation-interpret-diagnostics.

## No recorded hit is not proof of unreachable code

Possible explanations include an unsatisfied input/initialization prerequisite,
an excluded module/thread, a late collection start, unsupported generated code,
lost/unavailable data or a genuinely infeasible path. Determine which explanations
the evidence can exclude. A static graph edge is also not proof of feasibility.

An observed hit supports reachability under that execution's conditions; a forced
call or modified state narrows what it proves about natural reachability. A missing
malware action after failed negotiation is an observation limit, not benignness.
An impossibility claim needs constraints or exhaustive reasoning for a stated
domain, not merely prolonged absence from a trace.

## Sources and scope

Reviewed 2026-10-02. Definitions and implementation examples are scoped; diagrams
expressed in text and copy examples are constructed reasoning aids. No target
coverage was collected. Workflow: playbook-validation-coverage-evidence.

1. [LLVM SanitizerCoverage](https://clang.llvm.org/docs/SanitizerCoverage.html): instrumentation points, edge coverage, pruning and exclusion mechanisms.
2. [Clang source-based coverage](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html#interpreting-reports): function/instantiation, line/region and branch report meanings.
3. [LLVM fuzzing output](https://llvm.org/docs/LibFuzzer.html#output): coverage versus combined features.
