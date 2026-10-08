---
id: playbook-re-validate-concurrent-interleaving
title: Validate a concurrent interleaving and preserve its evidence
kind: playbook
topics: [reverse-engineering, concurrency, evidence, races, lifetime]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Validate a concurrent interleaving and preserve its evidence

## Purpose and evidence inputs
Reviewed 2026-10-02. Use for a suspected data race, TOCTOU, deadlock, reentrant
state error or async lifetime violation in an authorized target. Preserve binary
hash/build identity, OS/ISA/runtime, inputs, object generations, participant
threads/callbacks, relevant instruction addresses and synchronization contracts.
State one invariant first: e.g. every copy length is bounded by the retained
destination, or no callback uses an owner after its last lifetime guarantee ends.

Keep machine evidence separate from inferred source variables and intent. Shared
addresses alone do not prove the same live object; multiple decompiler reads
alone do not prove multiple actual fetches.

## Recover participants and protection
Enumerate normal, error, cancellation, timeout, reconnect, shutdown and nested
callback paths touching the state. Identify which actor controls input/mutation,
which object each pointer/handle denotes and what retains its lifetime. Recover
lock identities/modes, acquire/release edges, queue handoff and API drain promises.
For language data-race claims, establish conflicting operations and missing
happens-before; for logic races, establish the multi-step operation invariant.

Do not treat absence of a visible fence as absent synchronization, or the
presence of atomic helpers as complete protection. Check helper implementations,
call boundaries and actual ISA semantics before asserting permitted reordering.

## Write the minimal schedule
Record ordered events with participant, object generation, instruction/API,
observed value and held protection. Constructed TOCTOU schedule:

1. A reads length=16 and accepts capacity=64.
2. B can mutate the same live request length to 4096.
3. A reloads length=4096 and passes it to the copy without another sufficient check.

For every gap, explain why the other participant can run and why no lock,
snapshot, lifetime reference or version check excludes the schedule. Mark
unresolved edges. A hypothesized schedule is not a reproduced trace. In a
deadlock schedule, show simultaneous outstanding waits, not just opposite
acquisition orders from incompatible states.

## Separate feasible schedules from observed executions
Instruction paths, object lifetimes and synchronization contracts can support a
feasible schedule without an observed run. State which edges are established and
which remain assumptions. Identify the first invariant violation, not only a later
crash: changed values, recycled allocation, last reference, conflicting commit or
blocked wait dependency. Static reasoning is not an execution observation.

If separately authorized runtime observations are available, preserve controlled
inputs, initial state, isolation and observation conditions. Pausing threads or
instrumenting accesses can alter scheduling; changed synchronization, impossible
register values or manually freed objects do not reproduce the original behavior.
A race report or a clean stress run applies only within its observation model and
exercised paths. Neither proves the presence or absence of every logical race.

## Test counterexplanations and neighboring paths
Check whether aliases denote different objects; whether cleanup paths are
exclusive; whether weak CAS failure is spurious; whether a callback is actually
drained; whether the consumer revalidates the changed snapshot; and whether an
error path avoids the sensitive effect. Check lock coverage after waits and
callouts, not only on entry. Preserve the counterevidence explicitly.

Once an invariant violation is established, assess independently input control,
entry reachability, privilege boundary, realistic scheduling and impact. Do not
equate a theoretical data race with exploitable corruption or a lab deadlock
with remotely reachable denial of service.

## Handoff and supporting references
Return: invariant; scoped target identity; minimal event schedule; exact evidence
for each event; synchronization/lifetime analysis; observed effect; excluded
alternatives; reproduction conditions; remaining unknowns. Keep candidate,
confirmed defect and impact assessment separate.

Supporting facts: reference-concurrency-memory-order-atomic-invariants,
reference-concurrency-mutable-validation-double-fetch,
reference-concurrency-refcounts-reuse,
reference-concurrency-cancellation-completion-shutdown and
reference-concurrency-locks-waits-reentrancy. Primary anchors reviewed 2026-10-02:
[C++ race definition](https://eel.is/c++draft/intro.races),
[Linux kref acquisition](https://docs.kernel.org/core-api/kref.html),
[Windows cancellation](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex).
This workflow does not replace the target API/ISA specification.
