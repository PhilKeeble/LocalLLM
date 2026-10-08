---
id: playbook-validation-coverage-evidence
title: Determine what coverage proves about a sensitive path or missing behavior
kind: playbook
topics: [reverse-engineering, coverage, reachability, negative-evidence, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Interpret coverage as evidence, not a verdict

## State the exact reachability question

Name the instruction, handler, state transition or effect under investigation.
Distinguish module loaded, function entered, relevant branch taken, access
attempted and operation completed. A report answering one of these does not
automatically answer the others.

For vulnerability identification, identify the input/state needed for the
violating operation. For malware analysis, identify activation prerequisites and
the code/data/effect chain. Use existing coverage, traces and static evidence;
this workflow does not require a new execution or a particular collection tool.

## Bind the measurement to code identity and collection scope

Record build/artifact identity, module/range, architecture and code generation.
Recover collection unit, filters, included processes/threads, start/stop interval
and known missing data. Distinguish original instructions from translated code
and compiler-generated instrumentation. Use reference-validation-coverage-reachability
and reference-validation-binary-instrumentation-evidence.

If only a percentage or opaque bitmap is available, preserve that limitation.
Do not infer exact path coverage from an unnamed metric. A different build,
module filter or starting point can change both the denominator and the meaning
of the measured points; compare like-scoped evidence or explain the mismatch.

## Trace the prerequisite chain to the sensitive operation

Identify where the path stops progressing: input acquisition, framing, decoding,
integrity validation, initialization, authentication, variant selection or actual
consumption. Recover the guarding value and rejection destination. A deep target
with no recorded hits can result from input rejection before its entry.

Distinguish a proven rejecting prerequisite from missing collection. An indirect
target omitted by a decompiler is not thereby unreachable. Preserve unknown edges
and exceptional continuations. Use reference-native-computed-dispatch-tables and
reference-native-path-feasibility-guards rather than inferring the whole graph
from observed destinations.

## Inspect the first relevant event, not only an aggregate total

For a recorded hit, recover the same invocation's inputs, object generation,
operands and authority. Determine whether the event occurs before, during or after
the operation whose outcome matters. A call entry does not establish return;
return can precede asynchronous completion.

For an access, compare its full byte range with the correct live/initialized
object. For authorization, compare subject, object, action and decision at use.
For a malware command, connect dispatch to the destination and observed result.
Additional hits without these facts do not resolve the security question.

## Explain negative evidence with a bounded claim

Classify an unobserved path as unresolved, outside collection, blocked by an
established prerequisite, or proven infeasible under stated constraints. Keep
those categories separate. A small corpus, disabled feature, unsupported CPU
operation or missing peer state can all limit exploration.

Specify the next discriminating evidence: an omitted module's collection scope,
the branch's actual operand, initialization failure, or a state transition enabling
dispatch. This is an evidence request, not authorization to change configuration,
force execution, disable checks or connect a specimen to external services.

## Interpret saturation and new feedback conservatively

No new coverage means no new measured feature under the chosen inputs, model and
budget. It does not imply all values, schedules, error cases or logic policies
have been explored. A new comparison feature or count is not necessarily a new
control-flow path; inspect the metric's meaning.

Relate gaps to concrete hypotheses: larger representable lengths, a different
operation mode, failure cleanup or a prerequisite sequence. Use
playbook-validation-input-selection-mutation and playbook-validation-stateful-sequences.
Do not replace a missing hypothesis with arbitrary execution volume.

## Report reached behavior, missing scope and supported conclusions separately

Retain the measurement identity and scope, exact relevant hits or absences,
state/input provenance, and the data/effect evidence supporting the conclusion.
Keep corpus-aggregate coverage separate from one input's execution record.
Preserve analyst-forced conditions and instrumentation effects.

A useful result can be a supported candidate, a refuted path under explicit
constraints, or a confirmed invariant violation. A clean detector result and high
coverage still do not establish absence of all vulnerabilities. Likewise, absent
activity in one environment does not clear a suspected malware capability.

## Basis and limits

Reviewed 2026-10-02. Conceptual workflow grounded in
reference-validation-coverage-reachability and the linked data-flow, path and
instrumentation references. The primary coverage sources define metrics, not
security assurance thresholds or a required debugger/fuzzer combination.
