---
id: reference-logic-state-transitions-failure-policy
title: State transitions, premature commit, fail-open paths and session contamination
kind: reference
topics: [logic-bugs, state-machines, fail-open, sessions, validation]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# State transitions, premature commit, fail-open paths and session contamination

## Scope and reconstructed state
Reviewed 2026-10-02. State-machine examples below are constructed proof models,
not facts about a particular target. State includes flags, object existence,
validated values, ownership, pending work and persistent records, not only an
enum called state. A branch on state=READY establishes little until the writes
that can produce READY and the data it is meant to summarize are recovered.
Distinguish intended transition rules from merely common UI/request ordering.

## Missing or reordered phases
CWE-841 classifies failure to enforce a required actor workflow, including
omitted or reordered steps. [1] Constructed protocol:

| Request | Required precondition | Result |
| --- | --- | --- |
| BEGIN | No active operation | New operation identity |
| VALIDATE | Complete stable input for that operation | Validated version recorded |
| COMMIT | That same operation/version is validated and authorized | Effect published |

COMMIT guarded only by operation_exists accepts BEGIN→COMMIT. A single valid
sequence BEGIN→VALIDATE→COMMIT does not rule out that omission. If VALIDATE sets a
session-wide flag, later mutation or a new operation can reuse stale validation.
Evidence must link the consumed operation/version to the completed prerequisite.

## Premature side effects and partial commits
A check performed after an irreversible effect cannot prevent that effect.
Constructed example: handler installs a file, then checks permission and returns
denied. The response says failure, but the unauthorized file replacement already
occurred. Conversely a temporary private write may be harmless if it cannot be
observed/used and is reliably discarded before publication.

Recover the first externally visible or security-relevant effect, not merely
the function named commit. Publication can occur through a global pointer,
callback, rename, message, device command or database operation. Distinguish
preparation, publication and acknowledgement; one return status does not prove
all three succeeded or failed together. Transaction boundaries are covered in
reference-logic-retries-transactions-replay.

## Fail-open is a policy outcome, not every fallback
CWE-636 describes error handling that enters a less secure state. [2] Constructed
decision API returns ALLOW, DENY or ERROR, but caller proceeds whenever result
is not DENY. Timeout, parse failure or dependency outage can then authorize an
operation that should require ALLOW. Confirm enum values and emitted comparisons;
decompiler Boolean types can hide a third outcome.

A fallback is not inherently fail-open: it may preserve equivalent authorization
or intentionally provide a safe restricted service. State the required policy,
trigger condition, actual fallback authority and forbidden effect. Error logging
does not establish rejection; follow control flow to the sensitive operation.

## Failure paths retain or corrupt state
Constructed example: authentication attempt for B overwrites current_user but
failure leaves authenticated=true from A. A later operation uses B's identity
with A's success state. Another variant changes an object pointer before a
validation error and leaves the old validated flag set.

For each failure edge, distinguish values reset, retained intentionally, partially
updated and rolled back. Cleanup success must not overwrite the original result
and produce false success. Returning an error without restoring an invariant
can affect the next request even when the failing request performs no sensitive
operation. Analysis limited to freshly initialized sessions can miss this history
dependency. Concrete protocol distinctions, including LDAP rebind and SSH partial
authentication, are in reference-parser-protocol-authentication-state; their reset
rules are not interchangeable across protocols.

Use playbook-validation-error-path-investigation to follow partial progress,
cleanup failures and the next operation. A forced failure condition must preserve
the relevant API's status, output validity and side effects before it can support
a claim about an ordinary reachable error path.

## Cross-request and cross-client contamination
CWE-488 concerns insufficient session-state separation, including shared or
pooled objects. [3] Reuse can expose valid old data or authority without any
uninitialized-memory read. Constructed case: response cache key is operation
name only, omitting principal/object; B receives A's cached privileged result.

Relevant state homes include process globals, thread-local storage, pooled
request objects, callback contexts, per-connection caches and singleton helpers.
Thread-local does not mean session-local when one worker handles many clients.
Record reset on success, error, cancellation and reconnect, plus cache key and
ownership. Shared state is not itself a defect if its data and policy are
intentionally shared and the access contract is satisfied.

## Observable violation versus unusual sequence
A logic finding needs a reachable sequence, the required invariant, actual state
at the violating effect and the missing enforcement. A malformed transition
that returns an error and preserves state is negative evidence. An undocumented
state value may be a legitimate compatibility/recovery state, not corruption.

Useful contrasts: same operation with phase omitted; same user with another
object; another user with the same object key; failure then next request;
reconnect then delayed callback. Hold unrelated fields constant where possible
to isolate the cause. These are comparison dimensions, not observations of target
behavior until supported by recovered branch/state evidence or separately authorized
runtime observations. For network-layer transitions and stream versus session
recovery, use playbook-re-protocol-security-state.

## Malware dispatch depends on state as well as decoded command bytes

Analytical distinction: a decoded command identifies candidate input to dispatch,
not proof of execution. Recover prerequisite negotiation, selected session/key,
command validation, handler selection, arguments and completion or external effect.
An acknowledgement can describe receipt rather than completed work.

Constructed case: a handler is present but reachable only after a session flag is
set. A forced flag can reveal capability while leaving natural activation unknown.
Likewise, missing activity after a failed handshake does not establish benignness.
Sequence evidence requirements are in playbook-validation-stateful-sequences;
legitimate protocol machinery alone establishes neither intent nor a vulnerability.

## Primary sources
Reviewed 2026-10-02; MITRE CWE 4.20 classifications. Examples above are independently
constructed binary-investigation models, not reproductions of listed CVEs.

1. [CWE-841, workflow enforcement](https://cwe.mitre.org/data/definitions/841.html).
2. [CWE-636, failing open](https://cwe.mitre.org/data/definitions/636.html).
3. [CWE-488, wrong-session data](https://cwe.mitre.org/data/definitions/488.html).
