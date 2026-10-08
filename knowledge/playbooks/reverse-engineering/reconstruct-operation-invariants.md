---
id: playbook-re-reconstruct-operation-invariants
title: Reconstruct operation invariants and validate logic defects
kind: playbook
topics: [reverse-engineering, logic-bugs, authorization, state-machines, evidence, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Reconstruct operation invariants and validate logic defects

## Purpose and target record
Reviewed 2026-10-02. Use when a binary may perform the wrong operation, for the
wrong subject/object, in the wrong state or after a failed prerequisite; memory
safety is a separate question, not a precondition. Record target hash/version,
configuration, entry mechanism, caller capabilities, object/session identity and
relevant helper boundaries.
Choose one sensitive effect and express the proposed invariant in falsifiable
terms. Example: only the owner of this live operation may publish its validated
payload, at most once, under the required policy version.

Distinguish documented policy from inferred intention. If the policy is unknown,
report observed behavior and the missing requirement rather than declaring a
security bypass from surprise alone.

## Recover entry-to-effect authority and data
Starting at the effect, trace backward to dispatch, input parsing, identity
establishment, authorization, object lookup and state guards. Track subject,
operation, object generation, operands, tenant/session and decision time.
Forward-trace each checked value to the consumed representation; mark decoding,
normalization, reload, alias, implicit default and asynchronous handoff.

Compare the authority used by a helper with the authority granted to its caller.
Identify checks in server/privileged code; UI restrictions or client-generated
fields alone are not evidence of service enforcement. Also identify upstream
trusted enforcement before claiming a missing local check is exploitable.

## Reconstruct a transition table
For each recovered state, list accepted events, actual guards, mutations, external
effects, result codes and next state. Include initial, error, closing, recovered
and compatibility states; include flags/pointers that encode state implicitly.
Record where the input version becomes validated and what invalidates that fact.

Trace omitted, repeated, reordered and interrupted phases, not just the normal
sequence. Check whether a new operation inherits old
validation or authorization. A table entry requires branch/write evidence;
do not assign meaning to an enum value solely from an invented decompiler name.

## Map failure and commit boundaries
Separate private preparation, visible effect, durable commit and response.
For timeout, parse error, denied authorization, allocation failure, short I/O,
failed dependency and cancellation, record state retained/reset, effects already
visible and ownership of cleanup. Include next-request behavior after failure.

For retries, identify logical request identity, duplicate policy, in-progress
state and crash/reconnect persistence. For quotas, identify accounting principal,
reservation, charge and release. For updates, trace trusted metadata through
verification to the exact installed bytes and activation/recovery state.

## Construct discriminating comparisons
Compare recovered branches and state writes with one relevant dimension changed:
owner A versus B; same numeric ID in another namespace; VALIDATE omitted; payload
changed after validation; same request repeated after lost acknowledgement;
malformed config versus absent config; failure followed by a second client.
Preserve the initial state and path predicates that make the sequence feasible.

Track effects, not only status codes. A denied response can follow an already
performed effect, and a success response can hide a partial commit. Injected
faults must correspond to feasible API failures; forced impossible internal
states support a hypothesis but do not reproduce the original program behavior.
If runtime evidence is separately authorized, use isolated bounded execution and
record exact inputs and prior state. Do not require specimen execution merely to
use this reference or treat a static inference as an observed run.

## Malware behavior need not be a software defect

When investigating suspected malware, recover the operation deliberately implemented:
which configuration or command activates it, what input selects its targets,
which authority it uses and what it changes or discloses. A program can implement
harmful behavior correctly, without violating its own internal state machine.

Distinguish declared capability, feasible dispatch and observed effect. A file-write
or network-send helper is not enough to classify purpose; trace content, destination,
trigger and surrounding behavior. Conversely, correct bounds and authorization
within a command channel do not make the controlled actions benign. Protocol
state recovery is covered by playbook-re-protocol-security-state.

## Counterevidence and handoff
Test alternate explanations: intentional capability transfer, authorization in
a trusted wrapper, immutable captured state, a valid recovery policy, idempotent
effects, rejected second commit or a transaction that actually covers all effects.
Do not equate a missing familiar comparison with missing enforcement.

Return the policy/invariant, entry and caller control, minimal request/event
sequence, branch/value/object evidence, actual forbidden effect, alternative
explanations checked and unresolved reachability/impact. Keep target observations
separate from constructed examples and classification labels.

## Supporting references
Reviewed 2026-10-02. Use reference-logic-authorization-object-binding,
reference-logic-state-transitions-failure-policy,
reference-logic-retries-transactions-replay,
reference-logic-configuration-quotas-fallbacks and
reference-logic-update-verification-installation for scoped facts and examples.
Primary classification anchors:
[CWE-863 authorization](https://cwe.mitre.org/data/definitions/863.html),
[CWE-841 workflow](https://cwe.mitre.org/data/definitions/841.html),
[CWE-636 fail-open](https://cwe.mitre.org/data/definitions/636.html).
Classification names do not establish the target's intended policy.
