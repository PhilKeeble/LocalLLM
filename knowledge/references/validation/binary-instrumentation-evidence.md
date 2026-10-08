---
id: reference-validation-binary-instrumentation-evidence
title: Instrumentation hooks, trace scope, translated code and observation limits
kind: reference
topics: [binary-instrumentation, hooks, code-cache, traces, malware-analysis, observation-scope]
platforms: [windows, linux, macos, android, ios]
architectures: [x86, x64, arm, arm64]
---
# Binary instrumentation evidence

## Function hooks can observe or change the call

Instrumentation can both observe and alter a call; these roles must be separated.
For example, Frida Interceptor callbacks can read/write arguments and register
context. Its
per-invocation object supports associating entry data with the matching return.
Argument interpretation at an arbitrary instruction is not necessarily the
function-entry argument layout. [1]

Investigative consequence: record hook location, ABI, thread and invocation.
Preserve original arguments separately from replacements. A buffer address saved
at entry is not a saved copy of its bytes. Recover outputs only within their
valid lifetime and actual returned extent. A call observed after modifying an
argument is evidence about the modified call, not the original caller's behavior.

## Thread, interval and event selection define what a trace contains

An execution trace covers selected events, not necessarily the whole process.
For example, Frida Stalker follows a specified thread, or the current thread when
the thread identifier is omitted.
Excluded ranges suppress tracing within calls into those ranges. Event choices
distinguish calls, returns, instructions, executed blocks and compiled blocks;
call summaries aggregate targets/counts rather than retaining call order. [1]

Investigative consequence: no event is not proof of no execution outside the
collection scope. A compile event is not a per-execution counter. An aggregate
call count cannot reconstruct ordering, arguments or cross-thread causality.
Preserve covered threads, intervals, exclusions and event type with conclusions.

## Instrumented code addresses are not automatically original module addresses

Dynamic translation can execute generated copies rather than original addresses.
Frida Stalker executes relocated, instrumented copies of original blocks and
reuses these copies. Its design distinguishes original-code ranges from generated-code
ranges. [2]

Investigative consequence: identify whether a PC belongs to target code, a
translated copy or instrumentation. Do not subtract the original module base
from a code-cache PC to invent an RVA. Retain the tool's address mapping and
original bytes. A generated executable region can belong to the analysis tool,
not the application's JIT or an unpacked payload. Conversely, that possibility
does not explain every unidentified region; establish its creator and use.

## Self-modifying code needs code-generation and cache identity

Translated code and original bytes may have different update histories. In the
documented Stalker implementation, a trust policy controls when it stops checking
whether previously translated original bytes have changed. Its design also explains why a hook
installed after translation may not affect an already cached copy. [2]

Investigative consequence: correlate bytes, translation generation and hook
installation time. A missed hook may be a collection artifact, not evasion.
Likewise, a trace attributed using a later memory dump may name the wrong code
version. Keep application JIT identity separate from tool translation identity;
see reference-jit-code-identity.

## Added instrumentation can disturb exclusive-store sequences

Frida documents that inserted work can disturb ARM/AArch64 exclusive load/store
sequences and that Stalker needs special handling around them. [1,2]

Investigative consequence: an instrumentation-only retry loop or timeout is not
sufficient evidence of a target deadlock. Recover the original instructions and
store-status path, then separate collector effects from application contention.
Do not assume tracing preserves every concurrency interleaving. Architectural
status semantics remain in architecture-aarch64-instruction-evidence.

## Coverage and a security violation require different evidence

A block/call trace answers a control-flow question within its collection scope.
It does not, by itself, state object bounds, initializedness, ownership or caller
authority. For vulnerability identification, join the instruction to its violated
contract. For malware analysis, join the dispatch to arguments and actual effects.
Hooks that fabricate results cannot establish the real OS operation succeeded.
These are analytical limits, not claims that every tracer detects the same events.

## Primary sources and scope

Reviewed 2026-10-02. Mechanism-first reference grounded in Frida's rolling API
and Stalker design as implementation examples. It does not prescribe Frida or
claim that every collector has these event types, cache rules or limitations.
Workflow: playbook-validation-binary-only-evidence.

1. [Frida JavaScript API](https://frida.re/docs/javascript-api/): Interceptor and Stalker callbacks, event selection and transformer warnings.
2. [Frida Stalker design](https://frida.re/docs/stalker/): block relocation/reuse, call probes, trust threshold and exclusive-store considerations.
