---
id: playbook-re-rust-boundary
title: Recover Rust behavior, unsafe contracts and native boundaries in binaries
kind: playbook
topics: [reverse-engineering, rust, vulnerability-analysis, malware-analysis, ownership, ffi]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Investigating a Rust-containing binary

## Establish Rust attribution without assigning behavior from the language
Preserve specimen identity, architecture, file/runtime coordinates and available
symbols. Use symbol names and matched library/compiler patterns as attribution
evidence, not proof of a specific compiler version or malicious intent. A binary
can mix Rust, C/C++ and other code; map transitions explicitly.

State the question before following helpers: an attacker-controlled length reaching
an unsafe operation, a stale callback context, a missing authorization check, or
a suspected command handler reaching an external effect. Retained panic, allocator
or formatting code alone answers none of those questions. Factual starting point:
`reference-rust-layout-dispatch`.

## Recover enum decisions, trait dispatch and concrete generic types
For an enum-like value, connect constructors, variant tests, payload uses and
cleanup. Do not invent a separate tag when a niche representation explains the
branch. For indirect trait calls, recover the data pointer, selected method and
candidate concrete implementation; keep unproved targets explicit.

For specialized generic code, identify the type-dependent widths and ownership
operations actually present. Repair the decompiler's prototype before propagating
a guessed Vec field order or C calling convention through callers. Consult
`reference-rust-layout-dispatch`; machine evidence takes precedence over a name
match or a source-like decompiler rendering.

## Vulnerability path: input, conversion, violated contract and consequence
Trace external input through parsing, integer/count conversion, allocation and
the final consuming operation. Record units and actual initialized extent. Audit
raw slice construction, unchecked text conversion, typed initialization and native
output counts against `reference-rust-unsafe-memory`.

A plausible unsafe call is only a lead. Establish feasible branch conditions,
attacker influence and the violated requirement. Also inspect logical bugs that
need no memory corruption: incorrect object authorization, state transitions,
resource limits or error recovery. State separately what the defect establishes
and which consequences remain unproved.

## Ownership path: construction, transfer, callback and cleanup
Build a compact path record for the resource: allocator/origin, owner, borrowers,
move or raw transfer, pending users and final release. Distinguish Box/CString
ownership reconstruction from a borrow. Follow partial initialization and failure
paths rather than counting textual destructor calls.

For retained callbacks, identify when the final invocation becomes impossible;
a cancellation request alone does not prove that point. Include panic strategy,
catch boundaries and native unwind conventions. Use `reference-rust-ffi-boundaries`
and `reference-rust-ownership-drop-panic`; cleanup of memory is not rollback of
already committed external effects.

## Malware analysis: configuration and dispatch to observable effects
Separate runtime/library code from the path that consumes configuration or
commands. Follow decoded bytes, selected enum/trait branch, concrete arguments,
native/API calls and affected resource. Record gating conditions and unresolved
indirect calls. Strings and imports can guide this trace but do not replace it.

Distinguish three conclusions: code for a capability is present; a feasible path
can invoke it with specified inputs; execution was actually observed. Persistence,
collection or outbound-transfer claims need the corresponding path and arguments,
not Rust attribution or generic networking code. Shared dependencies do not prove
common operators. Workflow: `playbook-re-sensitive-data-flow`.

## Report facts, inference and missing evidence separately
Retain relevant addresses, bytes, recovered types with confidence, entry conditions,
ownership transitions and the precise contract used. Label constructed examples
and static path hypotheses; do not report unperformed execution as confirmation.
Record missing context such as callback quiescence, allocator identity or unknown
compiler layout instead of importing another build's assumptions.

Reviewed 2026-10-02. This is investigation guidance grounded in the four Rust
reference IDs cited above, not a requirement to execute an unknown specimen.
Controlled execution, when authorized, supplements rather than replaces the
contract and data/control-flow evidence.
