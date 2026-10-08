---
id: playbook-re-algorithmic-resource-boundary
title: Recover parser work, resource budgets and availability consequences
kind: playbook
topics: [reverse-engineering, vulnerability-identification, malware-analysis, parsers, algorithmic-complexity, resource-exhaustion]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover an algorithmic resource boundary

## Establish who controls the expensive operation

Start from the accepted input and dispatch path, not a visually complicated loop.
Record who can control bytes, counts, patterns, key values, graph edges, fragment
timing or repeated operations. Follow decoding and prior rejection to the relevant
consumer. Include parser callbacks, rendering, normalization, sorting, error
formatting and cleanup; successful parsing is not the end of the work chain.

Keep distinct: an ordinary costly feature, an attacker-triggerable resource-policy
violation and deliberate resource abuse by malware. A library identifier, regex
string or allocation size alone establishes none of those conclusions.

## Build a cost model from instructions and call relationships

Name the counted work: bytes scanned/copied, hash probes, comparison lengths,
backtracking states, graph visits, recursive frames or queued tasks. Recover loop
starts/ends, progress variables, nested-call multiplicity and caches. State which
inputs make the costly branch feasible, not just its theoretical upper bound.

Use reference-parser-algorithmic-work-graph-bounds for constructed sums and graph
models, reference-parser-regex-work-limits for engine-specific controls, and
reference-parser-xml-expansion-reparse-cost for expansion versus rescanning.
Separate a static cost argument from an observed duration. Existing authorized
traces can strengthen the argument; do not invent measurements or run an unknown
sample merely to complete a documentation-based investigation.

## Map every limit to its unit, owner and reset point

For each effective limit, record value/source, units, check location, charged work,
scope and reset/release behavior. Relevant scopes include operation, parsed object,
session, authenticated principal, worker pool and process. Recover sentinel meanings
and setter failure handling. A constant found in a binary need not be the active
setting on the selected path.

Compare separately: input bytes, expanded output, live allocations, node/field
count, recursion depth, repeated visits, CPU work, elapsed time and concurrent
retention. A cap on one quantity is not evidence of caps on the others. Route quota
reservation/identity arithmetic to reference-logic-configuration-quotas-fallbacks,
and compressed-data accounting to reference-parser-decompression-size-memory-limits.

## Determine whether deadlines actually interrupt and release work

Trace where expiry is noticed and what stops: waiting caller, parser loop, worker,
connection or whole task. A queued timer on a blocked event loop may not execute
until the expensive call returns. A caller returning timeout does not itself prove
the worker stopped, freed allocations or released shared locks.

These are investigative alternatives, not universal timer semantics. Identify
the actual scheduler/cancellation contract and observation points. Inspect retry,
pool return and late completion before claiming bounded outstanding work.
See reference-parser-stream-recovery-limits for idle-I/O versus total deadlines,
and reference-concurrency-cancellation-completion-shutdown for lifetime boundaries.

## Follow resource-limit failure to the security decision

Keep match, no-match, incomplete, invalid, exhausted and cancelled results distinct
where the API distinguishes them. Trace fallback parsing, retries with raised
limits, cached partial objects and actions already performed by callbacks.
A bounded failure can still become a logic flaw if the application treats skipped
validation as success; that requires evidence of the caller's decision path.

For malware analysis, mark any content not examined because a budget was reached.
Do not translate incomplete scanning into a clean verdict. If a specimen drives
expensive decoding, separate that observed behavior from an inference that its
purpose is analysis evasion; legitimate formats can also require substantial work.

## State availability impact without inflating the evidence

Report input authority, reached operation, cost model, effective bound, affected
resource and scheduling scope. Explain whether the consequence is one rejected
document, loss of a worker, shared event-loop blockage, retained memory or process
termination. A single expensive task does not automatically deny the whole service.
Include isolation, admission limits or preconditions that narrow the conclusion.

If reachability, collision feasibility, cancellation or deployed configuration is
unknown, name that gap. Keep the mechanism finding useful without calling it a
reproduced remote denial of service. Resource-exhaustion evidence does not by itself
establish code execution or malicious intent.

## Basis and review

Reviewed 2026-10-02. Analytical workflow grounded in the linked library references
and their primary sources; no specimen observations or performed experiments are
claimed. Use alongside playbook-re-incremental-parser-state when input arrives in
fragments and playbook-re-object-reconstruction-boundary when parsing invokes code.
