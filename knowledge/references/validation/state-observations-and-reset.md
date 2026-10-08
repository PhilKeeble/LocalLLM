---
id: reference-validation-state-observations-reset
title: Observable responses, hidden session state and reset-domain evidence
kind: reference
topics: [stateful-fuzzing, state-machines, sessions, authentication, reset, callbacks, evidence]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# State observations and reset boundaries

## A response code is an observation, not a complete state identifier

An identical response can accompany different identities, pending work or retained
data. Conversely, different response bytes need not imply different security state.
This is an analytical distinction between visible output and the internal facts
that govern later operations, not a claim about a particular parser layout.

Concrete protocol evidence: SSH authentication failure messages can carry partial
success while authentication is incomplete; final success has a distinct message.
[1] Thus grouping only by the outer failure code loses relevant progress. Retain
substatus, operation identity and the conditions that enable the next sensitive
action. Trace fields and consumers before treating a response-derived state graph
as the implementation's actual state machine.

## Authentication progress is bound to an identity and service

For SSH, changing the user or service during authentication requires clearing
accumulated authentication state, or disconnecting if it cannot be cleared. [1]
For LDAP, receipt of Bind moves authorization to anonymous; failed binding leaves
it anonymous. [2] These are separate protocol contracts, not one universal reset.

Investigative consequence: record attempted identity, verified identity, effective
authorization and unfinished authentication separately. A previous success flag
cannot be interpreted without the identity/attempt to which it belongs. Anonymous
access may be intentionally permitted. Establish the actual forbidden operation
and policy before treating acceptance after a failed attempt as a bypass.
Detailed facts: reference-parser-protocol-authentication-state.

## Reset has an object, scope and completion condition

Use the following analytical inventory; it is not a universal memory layout.

| State owner | Examples of evidence needed |
| --- | --- |
| Message/parser | Cursor, partial fields, buffered suffix, encoding mode |
| Operation | Object/version, validated operands, commit/result state |
| Session | Principal, grants, negotiated mode, resumption identity |
| Worker/process | Thread-local data, pools, globals, allocator history |
| Pending work | Timers, callbacks, queued requests, retained owners |
| External system | Files, remote commits, durable records, shared counters |

Resetting one row does not establish that another was reset. A reconnect can
replace a transport while retaining application state; a process restart cannot
retract an already delivered external effect. Trace each relevant owner and its
contract. Permitted session resumption is not inherently contamination. See
reference-validation-isolation-reset-boundaries and reference-parser-stream-recovery-limits.

## A reset request does not establish quiescence

Quiescence means the work relevant to a lifetime or reset claim can no longer
access or change that state. It must be established for the particular subsystem,
not inferred from a timeout, an empty queue or a function name.

Concrete Windows contract: CancelIoEx requests cancellation without waiting for
completion; an operation can still complete normally, be canceled or fail another
way. Its OVERLAPPED storage cannot be reused until I/O completion. [3]
Application callbacks can have additional lifetimes beyond that I/O event.
Investigative consequence: late work can contaminate a new session even when the
new request's bytes are independent. Bind submission, completion, release and
reuse to the same object generation. See
reference-concurrency-cancellation-completion-shutdown.

## Sequence reachability and outcome are separate proof obligations

CWE-841 covers failure to enforce required actor workflows, including omitted or
reordered steps. [4] A strange order alone is not a vulnerability: the applicable
contract may allow it, reject it safely or implement recovery.

Constructed example: validation records version 3, mutation creates version 4,
and commit consumes version 4 under version 3's approval. The finding requires
the reachable sequence, stale approval and forbidden effect—not just a missing
function call in a trace. For malware, the same sequence reasoning distinguishes
a command merely received from one accepted, dispatched and completed. A reset
that skips activation prerequisites limits observed behavior; it does not prove
the binary benign.

## Sources and scope

Reviewed 2026-10-02. Protocol/API facts are explicitly scoped; the inventory and
examples are analytical models for binary investigations. No toolstack, target
execution or universal session implementation is assumed. Workflow:
playbook-validation-stateful-sequences.

1. [RFC 4252 §§5-5.1](https://www.rfc-editor.org/rfc/rfc4252.html#section-5): identity changes and partial versus complete authentication.
2. [RFC 4513 §4](https://www.rfc-editor.org/rfc/rfc4513.html#section-4): LDAP authorization transitions.
3. [CancelIoEx contract](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex): cancellation request versus terminal I/O and storage lifetime.
4. [CWE-841](https://cwe.mitre.org/data/definitions/841.html): required actor workflow enforcement, not proof of a specific target flaw.
