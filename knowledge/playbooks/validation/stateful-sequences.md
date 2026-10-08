---
id: playbook-validation-stateful-sequences
title: Investigate stateful request sequences, authentication changes and reconnect failures
kind: playbook
topics: [reverse-engineering, stateful-fuzzing, sessions, authentication, reconnect, reset, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Investigate a sequence rather than only its final input

## Define the state-dependent claim and its required invariant

Identify the sensitive operation and the condition that must hold when it takes
effect: correct principal/object, completed validation, live owner, single commit
or required protocol phase. An invariant is a condition the implementation must
preserve across the relevant events. Establish its policy or API basis; common
client behavior alone is not a mandatory sequence.

Recover static transitions and use existing captures first. The following are
reasoning and evidence requirements, not instructions to start a service, execute
a specimen or install a fuzzer. Use whichever exposed capabilities supply the
needed state, code and trace evidence.

## Represent each event with the state it can consume and change

For each relevant message, API call, timer, cancellation or completion, retain:
input and origin; principal/session/object generation; required preconditions;
state read/written; result; externally visible effect; and pending work.
Separate received bytes, parsing, acceptance, dispatch, commit and acknowledgement.

Find field writers and downstream consumers instead of relying on a decompiler's
state enum. A response-derived label can merge distinct internal states; retain
substatus and identity. Use reference-validation-state-observations-reset and
reference-logic-state-transitions-failure-policy.

## Preserve the prerequisite prefix and dynamic value relationships

A sequence includes the steps establishing its starting conditions, not just the
last malformed message. Retain authentication, negotiated modes, created objects,
earlier failures and the initial state of relevant shared resources. For values
returned by the target, record which later field refers to which earlier result.

Constructed example: CREATE returns an object identifier consumed by WRITE and
COMMIT. Reusing a numeric identifier from another run can select no object—or a
different object. Distinguish concrete recorded bytes from the logical dependency
on the newly returned identifier. Do not repair stale IDs silently and then claim
byte-for-byte replay. Keep malformed values when they are the property being studied.

## Compare transition boundaries with a specific hypothesis

Use these conceptual contrasts where the target contract makes them relevant.
They are candidate analysis dimensions, not observed vulnerabilities.

| Contrast | Question at the sensitive effect |
| --- | --- |
| Omit/reorder a prerequisite | Is the required fact actually enforced? |
| Repeat a completed operation | Can effects duplicate or resources release twice? |
| Mutate after validation | Does approval bind the consumed object/version? |
| Change identity mid-exchange | Does old progress or authority reach the new subject? |
| Fail, then send a valid request | Which partial state survives the failure? |
| Disconnect/reconnect | Which transport, parser and session generations changed? |
| Complete old work after reuse | Does the result reach the correct live owner? |

Hold unrelated dimensions constant when the evidence permits. Attribute a changed
outcome to the changed precondition only after accounting for timing, randomness,
external state and execution-model differences.

## Treat authentication changes as several linked state transitions

Trace attempted identity, verified credentials/factors, effective authorization,
cached grants and active operations. Determine when the actual contract invalidates
each. Do not assume every protocol resets on failed authentication in the same way.
The LDAP and SSH examples in reference-parser-protocol-authentication-state have
different rules; neither substitutes for a proprietary protocol's recovered policy.

Follow the operation after the failure or identity switch. A stale flag is a lead;
evidence must connect it to the identity/object selected for the effect. Consider
legitimate anonymous access, delegation and resumption as possible counterevidence.
Use reference-logic-authorization-object-binding for the complete decision tuple.

## Distinguish reconnect, parser reset and session resumption

Recover what closes, what returns to a pool and what remains reachable. Include
buffered input, cursors, callbacks and shared compression/negotiation state. A new
transport handle does not prove a new logical session, and retained state is not
necessarily wrong when the protocol explicitly supports resumption.

Determine the identity and generation captured by outstanding work and the one
used when its result is applied. A valid address can now belong to a new client.
Use reference-parser-stream-recovery-limits and
reference-concurrency-cancellation-completion-shutdown. Treat timers and completion
events as sequence elements, not unexplained noise between messages.

## Separate intended sequence state from accidental cross-case state

Define the analysis unit: one request, one session, a multi-session history or a
restart/recovery history. Identify reset domains and completion conditions. A
return from cancellation is not necessarily drained work; restarting a process
does not undo a remote commit. Preserve relevant initial state in each domain.

If an outcome depends on earlier cases, retain that history until it is explained.
It may reveal a real pooled-object or persistent-state defect. If the adapter alone
creates impossible state, qualify the finding accordingly. Do not reset shared
services or external data merely to make evidence easier to interpret.

## Establish effects beyond responses and crashes

For vulnerabilities, connect the sequence to the first violated invariant and its
effect: wrong-session data, unauthorized operation, stale-object use, duplicate
commit or sustained resource loss. A rejection response can follow an already
published effect; a crash can be downstream of earlier corruption.

For malware, connect prerequisite exchange, decoded selector, handler, arguments
and result. Distinguish a command received from work completed. Missing behavior
after a failed negotiation is a visibility limitation, not proof of absent
capability. Forced state or fabricated peer responses must remain explicit.

## Preserve a sequence-level evidence record

Report initial state, ordered inputs/events, dynamic-value relationships, relevant
cross-thread ordering, object generations, state writes and the violating effect.
Mark which elements are observed, statically established, constructed or unknown.
A total log order alone may not establish causality between independent threads.

Retain a comparison sequence or counterevidence that explains why the state change
matters. Shortening a sequence must preserve its violated invariant, not merely
any crash or response. Report missing earlier history as a reproducibility limit;
do not silently replace it with a fresh-session assumption.
Use playbook-validation-failure-minimization for reducing prerequisite history
while preserving the causal claim and distinguishing unresolved candidates.

## Basis and scope

Reviewed 2026-10-02. Conceptual workflow based on the linked state, authorization,
parser and cancellation references. Fresh primary review: RFC 4252 authentication
completion/identity changes, RFC 4513 authorization state, Windows CancelIoEx
completion and CWE-841 workflow enforcement. No target observations are claimed.
For initial protocol recovery, use playbook-re-protocol-security-state; for adapter
entry fidelity, use playbook-validation-faithful-harness.
