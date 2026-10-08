---
id: playbook-validation-error-path-investigation
title: Investigate allocation, I/O, timeout, cancellation and cleanup failure paths
kind: playbook
topics: [reverse-engineering, fault-injection, error-handling, partial-io, cleanup, failure-policy, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover what remains true when an operation fails

## Define the operation and its failure obligations

Identify the entry boundary, required policy and operation stages: acquisition,
preparation, validation, publication, completion and acknowledgement. They need
not be distinct functions. State what must remain true on failure: no unauthorized
effect, valid retained state, correct ownership, accurate status or bounded recovery.

Recover code and existing captures first. Fault injection is one possible source
of conditional evidence, not a prerequisite. This workflow does not authorize
changing a shared service, exhausting host resources or executing a specimen.
Use reference-validation-failure-models-partial-effects for result-contract limits.

## Recover all result channels before interpreting an error edge

Identify primary return value, exception behavior, error field, valid output
parameters, transferred extent and asynchronous completion. Trace the exact
comparison and subsequent use. A guessed Boolean return can conceal pending,
partial-success or tri-state policy outcomes.

Follow error preservation across logging and cleanup; another call can replace
thread-local error state. Do not infer success from a final cleanup return or
failure from an unrelated stale error. Use reference-native-resource-lifetimes-results
and the actual API contract. Record outputs whose validity on failure is unknown
rather than assuming either zero initialization or preserved old contents.

## Describe a proposed failure at the correct stage and scope

Record operation identity, call site, input/state, failure point, affected dependency,
duration and the full permitted result. Distinguish these analysis dimensions:

| Condition | Evidence question |
| --- | --- |
| Acquisition fails before ownership exists | Does cleanup release an unacquired resource? |
| A later acquisition fails | Are earlier resources released or intentionally transferred? |
| Transfer makes partial progress | Are remaining offset/count and initialized extent correct? |
| Wait expires while work remains pending | Which references and completion paths remain live? |
| Effect completes but acknowledgement is lost | Can retry duplicate or misattribute the effect? |
| Recovery also encounters failure | Are state, accounting and original error still coherent? |

A forced condition outside the API contract can study robustness to corruption,
but must not be described as ordinary API failure. Changing only the visible status
after successful work may leave inconsistent hidden state.

## Follow ownership and publication along each relevant exit

Record resource generation, initialized members, borrowed aliases, transfer of
ownership and last use. Include exception cleanup and callbacks, not only explicit
return blocks. A shared cleanup label is not evidence that all incoming paths own
the same resources. Determine which state distinguishes partial initialization.

Follow capacity, count, pointer and ready/validated flags together. Constructed
case: reallocation fails while the original block survives, but capacity was already
increased. A later write can exceed the real allocation even if the failing call
returns an error. Establish the later path and actual stored values. Use
playbook-validation-allocation-lifetime-trace.

## Preserve partial progress and late completion in the reasoning

For short I/O, distinguish transferred bytes, buffer capacity and remaining work.
Identify whether retry advances from the right position, reparses accumulated
input, or repeats a logical operation. Do not substitute generic EOF for every
zero result or treat a would-block result as permanent rejection.

For timeout/cancellation, preserve pending work and the lifetime of each referenced
object until its own completion condition. Compare timeout, success and cancellation
paths for one-time effects, duplicate cleanup and stale-generation access. Use
reference-concurrency-cancellation-completion-shutdown and
reference-windows-overlapped-io-lifetime-cancellation for scoped distinctions.

## Examine recovery, retries and the next operation

Determine whether failure leaves a live transaction, reserved quota, published
object, pooled state or queued callback. Distinguish intentional recoverable state
from a violated invariant. Include failure of the compensating action and continued
dependency outage where the model permits them. A compensation can restore a count
without undoing an already disclosed value or delivered command.

Trace the next request or reconnect when retained state matters. A clean result
from a fresh process does not resolve a history-dependent defect. Use
reference-logic-retries-transactions-replay and
reference-logic-state-transitions-failure-policy. For process-loss claims, record
durability and recovery assumptions; normal function-return cleanup is not proof
of crash consistency.

## Connect the error path to the security or behavior claim

Report the modeled condition, feasible branch, first evidenced invariant violation
and consequence. Keep natural triggerability separate from behavior under a
forced condition. Resource exhaustion needs a reachable workload and relevant
limit; one retained cache object alone is not unbounded leakage.

For malware, recover fallback selection, retry/defer behavior and completed effects
under the observed conditions. A failure-only handler can be relevant without
proving it ran; forcing it does not establish original intent or activation.
For vulnerability findings, a returned error or absent crash does not refute
earlier unauthorized effects, stale state or invalid accesses.

## Preserve a bounded failure-path explanation

Keep the original evidence and any intervention distinct. Retain the dependency
contract, chosen failure model, partial effects, ownership transitions, remaining
work, reported result and subsequent state. Name competing explanations and the
earliest missing causal link.

If the available evidence supports a valid failure model and a violated invariant,
state that conditional finding precisely. If the model itself is unverified, do
not promote its outcome to an ordinary target defect. For simplification and
comparison criteria, use playbook-validation-failure-minimization and
playbook-validation-differential-metamorphic-analysis.

## Basis and scope

Reviewed 2026-10-02. Conceptual investigation workflow grounded in
reference-validation-failure-models-partial-effects and linked local references.
The constructed reallocation example is explanatory, not a target observation.
