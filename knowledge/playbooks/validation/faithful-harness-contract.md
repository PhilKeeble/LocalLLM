---
id: playbook-validation-faithful-harness
title: Establish a faithful fuzzing harness boundary for a reversed binary
kind: playbook
topics: [fuzzing, harness, reverse-engineering, calling-conventions, initialization, dependencies, reachability]
platforms: [windows, linux, macos, android, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Relate harness behavior to the target's real contract

## Choose the boundary and state the claim it can support

A harness is an adapter that supplies input and state to selected target code
and observes its result. Recover the natural caller, trust boundary and downstream
operation before choosing an internal function, exported API or full-process entry.
Use existing static/captured evidence first; this workflow does not itself authorize
execution of a specimen or changes to a shared service.

Record what is preserved, replaced and bypassed. An internal decoder can usefully
expose a bug under stated preconditions without proving that a public request
reaches it. Conversely, a caller's check only refutes a proposed input path when
that check actually dominates the relevant call with the same validated values.
Keep harness-local, API-contract and deployed-boundary conclusions distinct.

## Establish the machine interface before interpreting a call failure

Recover argument positions, widths, calling convention, stack requirements,
receiver/context, hidden result storage, return channels and callback signatures.
Use reference-native-prototype-argument-evidence and the selected ABI reference.
A decompiler prototype or function-pointer cast is not sufficient evidence.

For Windows x64, account for argument positions and caller-reserved home space;
do not import System V AMD64's independent integer/vector argument sequences.
Other architectures and private optimized interfaces need their own rules.
An immediate crash from a wrong receiver, hidden argument or stack contract is
not evidence of a target vulnerability. Inspect the first actual violated contract
using playbook-validation-first-fault-cause.

## Preserve the production input representation and its ownership

Record the transformation from supplied bytes to the target's parameters: framing,
decoding, length units, termination, alignment, copies and selected variant.
Keep supplied byte count, decoded count, allocation capacity and logical payload
length separate. Bounds-check the adapter itself without silently imposing an
unrelated validity rule that removes target error paths.

If the API mutates input or retains it after return, identify the required mutable
storage and lifetime. A temporary adapter buffer cannot stand in for a retained
owner. Constructed contrast: adding a trailing NUL can satisfy a C-string API's
precondition, but it changes the question if the real caller accepts unterminated
byte spans. Document which contract is being investigated rather than treating
both entry conditions as equivalent.

## Establish initialization, thread context and reachable state

Recover constructors, loader/runtime initialization, required configuration,
allocator ownership, thread-local context and prerequisites to the selected call.
Do not substitute a zero-filled block for a live language/runtime object unless
the target contract permits it. A fake vtable or copied process pointer does not
establish a valid receiver.

For Windows COM, apartment/thread requirements are part of the interface;
see reference-windows-com-apartments-reference-lifetime. For other runtimes, use
their local thread-attachment and object-lifetime references. A correctly arranged
register call can still violate those runtime preconditions. Preserve the evidence
that normal callers can produce the chosen state, or label it synthetic.

## Model dependencies with results, output data and side effects together

For replaced I/O, allocation, clock, random, authentication or callback services,
record the modeled result, output validity, transferred length, ownership change,
completion timing and external effect. Returning success without initializing
required outputs can manufacture a defect. Always succeeding can hide error
cleanup; synchronous completion can hide lifetime problems in deferred work.

Constructed example: a replacement read returns a full byte count but initializes
only a prefix. A later uninitialized-value warning may originate in that replacement,
not the real reader. Conversely, returning a documented short result with its
actual prefix can exercise legitimate incremental handling. Use the real API's
contract, including failure outputs, rather than a generic success/failure model.

## Separate per-input reset from deliberate stateful sequences

Identify state lifetime explicitly: one call, one sequence, one worker process,
shared external object or whole campaign. Inventory globals, caches, callbacks,
threads, handles, file offsets, allocator arenas and pending work. The engine does
not know which of these the target requires resetting. Engine-specific facts are
in reference-validation-fuzz-target-execution-contracts.

If sequence state is intentional, encode and preserve the sequence and starting
state. If independent cases are intended, unexplained dependence on a previous
case limits attribution. A process restart does not undo remote commits or reset
shared files. Use reference-validation-isolation-reset-boundaries. Do not label
every history-dependent crash a false positive: real applications may preserve
the same history, but that reachability needs evidence.

## Preserve cleanup and classify the observed outcome

Follow result handling and cleanup on success, rejection, partial initialization,
exception, timeout and cancellation. Record outstanding callbacks and buffers;
cleanup by the adapter must not double-release a resource already transferred to
the target. Catching every exception or forcing every error to success can conceal
the result that matters. Use playbook-validation-allocation-lifetime-trace.

Distinguish target defect, adapter defect, violated API precondition, unsupported
execution model and unresolved failure. A timeout is an observation, not proof
of an infinite loop. For diagnostic reporting and recovery modes, use
playbook-validation-interpret-diagnostics rather than assuming every warning crashes.

## Relate findings to vulnerability or malware evidence

For a vulnerability, retain the target identity, natural input path, preserved
preconditions, exact failed operation and any missing link to deployed reachability.
For malware analysis, a decoder harness may recover configuration fields without
showing that the original program selected them or performed their actions.
Feeding already-decoded content likewise does not prove the original decoding
or key-acquisition path succeeded.

Assess whether the available evidence distinguishes target behavior from adapter
behavior. A syntactically valid input rejected before the intended function is
weak coverage evidence; a wrapper-induced crash is not a substitute for that path.
Further authorized observation should resolve a specific gap, not silently expand
the claim beyond the chosen boundary. Report deviations alongside results.

## Source basis and scope

Reviewed 2026-10-02. Investigative synthesis, with platform/API contracts in the
linked local references. Constructed examples illustrate attribution, not findings.

- [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html): byte-range callback, repeated process execution and initialization.
- [AFL++ persistent mode](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.persistent_mode.md): reset and checkpoint constraints.
- [Microsoft x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170): argument, home-space and result contracts.
- [C++ function-call compatibility](https://eel.is/c++draft/expr.call): a cast does not make incompatible function types call-compatible.
