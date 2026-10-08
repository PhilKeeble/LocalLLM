---
id: playbook-re-windows-exception-cleanup
title: Recover Windows exception selection, cleanup and continuation paths
kind: playbook
topics: [reverse-engineering, windows, seh, cpp, exceptions, unwind, cleanup, validation]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Recover Windows exception selection, cleanup and continuation paths

## Identify exception mechanism before repairing the control-flow graph

Scope: authorized Windows binary analysis; reviewed 2026-10-02. Record image,
architecture, toolchain/runtime evidence, debugger state and observed exception.
Classify SEH filter, termination block, vectored callback, top-level filter,
C++ personality/funclet, translator or fail-fast path. Resolve the actual caller
before assigning meanings to a handler's integer return value.

Map machine unwind metadata separately from language cleanup. Match format
version and address bases; bind outlined code to its parent frame and protected
range. A generic handler name or ordinary-call prototype is not sufficient.
Use `reference-windows-seh-vectored-handlers`,
`reference-windows-msvc-exception-cleanup-evidence` and `abi-windows-x64`.
[Microsoft x64 unwind format](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170).

## Preserve exception record and debugger decisions without conflating addresses

For an observed Windows exception, retain code, flags, instruction address,
valid parameters, target CONTEXT, thread and first/last-chance status. For AV or
in-page error, separate the instruction from the inaccessible address and any
underlying NTSTATUS. Bound parameter reads and preserve copied data while its
storage is valid. Unknown fields stay unknown.

Record whether the debugger handled, passed through or altered the exception.
One first-chance stop does not prove the process would crash without a debugger.
Conversely, a recovered handler does not prove safe continuation. Identify the
specific state repair or error path rather than calling all caught faults benign.
Do not retain a borrowed filter-context pointer as a durable crash snapshot.

## Reconstruct search, unwind and continuation as separate paths

Follow SEH filters outward, preserving continue-search, continue-execution and
execute-handler branches. Filters can inspect state before inner cleanup.
When a handler is selected, add applicable unwind actions before its body;
resumption at the fault point is not the same path. Finally blocks do not select
a catch, and AbnormalTermination true need not mean an exception was raised.

For C++ EH, resolve IP-to-state, state-to-cleanup and try-to-catch associations
using the actual encoding. Follow transition targets rather than scanning all
destructors in numeric/address order. Track each cleanup's continuation: handler,
propagation, normal return or termination. Keep FH4 encoded fields distinct
from their expanded in-memory representation and from FH3 maps.

## Compare resource and invariant state at every feasible exceptional exit

For each potentially throwing/faulting operation in the Windows target, record
which acquisitions completed, ownership transfers and externally visible writes
already happened. Map cleanup to the same object generation. A completed member,
failed constructor, borrowed pointer and raw allocation have different obligations.
Use `reference-native-cpp-lifecycle-unwind` for language lifetime rules.

Check for skipped cleanup, repeated release on one feasible path, cleanup using
partially initialized state, false success after an exception, stale authorization
and incomplete rollback. Normal and exceptional release sites can be exclusive.
A catch-all that returns success does not reverse earlier effects. A finally
block or RAII object is not proof of cleanup on termination or asynchronous faults
under a compiler mode that does not supply that guarantee.

## Audit callback/module lifetime and fatal-path limits

Trace VEH and top-level filter registration/replacement/removal, translator
installation on the actual thread, and module/context retention. A DLL unload
does not implicitly remove its VEH. A registration token is not a proof that
callbacks are drained. Look for allocation/locking/callout dependencies in handlers
that run with faulting-thread state.

Keep noexcept escape, failed exception handling and Windows fail-fast separate
from ordinary caught propagation. Determine what actually terminates and which
effects survive; do not invent destructor execution before termination. A
fatal-check import alone is neither a memory-corruption finding nor proof that
the input reaches it. Preserve the triggering condition and counterevidence.

## Recover exception-driven malware paths without inventing malicious intent

If a Windows binary deliberately raises an exception, locate the relevant handler
registration or frame metadata, trigger, handler decisions, context changes and
resumption target. Follow the resulting operations and observable effects; a VEH,
software exception or unusual return constant alone is not proof of malware.
Debugger handling can bypass application handlers, so differing paths under a
debugger need not establish a deliberate anti-debug check.

Separate a detected fault from an earlier corrupting write using
playbook-validation-first-fault-cause. For a recovered handler that returns success,
ask what state remains corrupted or partially committed. For a fatal path, preserve
completed effects rather than assuming termination erased them. Label intent and
capability inferences separately from evidenced execution.

## Validate the disputed path with bounded, mechanism-matched evidence

Use static metadata/instruction evidence and, when authorized, debugger traces
matching the target ABI/options. A trace of a continuable software exception
does not establish access-violation recovery or another architecture's behavior.
Do not inject faults into a working service or change its global crash policy.

A sufficient result names the trigger, selected/rejected handler, protected
state, cleanup order, final continuation and violated invariant. Explicitly
separate source intent, documented contract, compiled observation and unresolved
target reachability. Test claims of duplicate release against mutually exclusive
paths and claims of safe recovery against retained corruption or partial effects.
