---
id: reference-validation-fuzz-target-execution-contracts
title: Fuzz-input representation, result channels and repeated-execution contracts
kind: reference
topics: [fuzzing, harness, persistent-mode, initialization, input-length, input-representation]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64]
---
# Fuzz-engine contracts are distinct from the target API contract

## Supplied bytes are not automatically a valid target object

A byte-range input contract supplies an address and byte extent, not decoded
objects or implicit termination. For example, libFuzzer's documented callback
receives a const byte pointer and size_t length, including empty/malformed inputs
and repeated calls within a process. [1]

Investigative consequence: the supplied size is a byte extent, not a decoded length,
element count or promise of a trailing NUL. Any conversion to a target API's
representation belongs to the harness and needs its own bounds and lifetime
reasoning. Bytes representing an object on disk are not automatically a valid
in-memory object with usable pointers or initialized runtime state.

## Callback return values and startup initialization have limited meanings

An adapter result used for corpus selection can differ from the target's parse or
operation result. As a scoped example, libFuzzer callback -1 excludes an input
from corpus admission while 0 permits consideration; other values are reserved.
Its optional initialization hook runs at startup. [1]

Investigative consequence: callback 0 is not the parser's success status or a
safety verdict. Preserve target results separately. Startup initialization is
not automatically per-input reset. A filter rejecting malformed inputs can
exclude precisely the error paths under investigation; document its purpose.

## Reusing a process requires an explicit state-reset boundary

Process reuse preserves more than the next call's arguments. For independent
cases, identify state that must be restored, released or recreated. AFL++'s
persistent-mode guidance explicitly covers retained state, resource leaks and
descriptor state. [2] Stability is not proof of semantic independence.

Investigative consequence: if a failure requires earlier inputs, the reproduction
unit includes that history until evidence shows otherwise. Distinguish an intended
stateful sequence from accidental cross-case contamination. Recreating a parser
object does not necessarily reset globals, thread-local state or external objects.

## A starting snapshot must preserve the intended initialization boundary

The point captured for repeated execution determines which input and environment
state is inherited. A specific forkserver contract illustrates the issue: AFL++
warns against deferred initialization after important thread/child creation,
timers, relevant shared resources or access to fuzzed input, including its size. [2]

Investigative consequence: snapshotting after input consumption can freeze the
wrong state; inherited resource state can differ from a fresh invocation. Record
the actual execution model and checkpoint, not just the word persistent. Do not
transfer forkserver assumptions to Windows process creation or an unrelated
emulator snapshot. Workflow: playbook-validation-faithful-harness.

## Sources and scope

Reviewed 2026-10-02. Conceptual input and execution boundaries, with named engine
contracts as scoped supporting examples, not required tools or proof of a target's
preconditions. Do not generalize an example's return values or initialization
restrictions to a different engine.

1. [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html): Fuzz Target, Startup initialization and Rejecting unwanted inputs.
2. [AFL++ persistent mode](https://github.com/AFLplusplus/AFLplusplus/blob/stable/instrumentation/README.persistent_mode.md): state reset and deferred initialization; rolling stable-branch documentation.
