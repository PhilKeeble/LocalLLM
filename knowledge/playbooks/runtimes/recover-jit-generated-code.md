---
id: playbook-re-jit-generated-code
title: Investigate JIT guards, generated-code failures and runtime-versus-payload identity
kind: playbook
topics: [reverse-engineering, jit, generated-code, vulnerability-analysis, malware-analysis, deoptimization]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# Investigate JIT-generated code

## Establish runtime, code version and logical method together

Identify the engine/runtime from converging artifact and process evidence.
Separate application bytecode, interpreter/helper code, baseline native code and
optimized native code. Record native bytes/range, method or script identity,
compilation generation and observation time where available.

Use reference-jit-code-identity. A symbol name or executable allocation alone
cannot distinguish a legitimate runtime stub from payload code. Do not attach,
enable agents or execute an unknown sample solely to fill metadata gaps without
authorization and an appropriate analysis environment; existing captures may
leave identity unresolved.

## Recover the fast path's assumption and every failure destination

For the relevant access/call, identify shape/type, range, representation, target
or instance assumptions. Trace earlier dominating guards, runtime dependencies,
inline-cache cases and the slow/deoptimization path. Keep a source-language type
separate from the engine's storage representation.

Use reference-jit-guards-specialization. A guard need not be adjacent to the use,
and a miss need not raise an application error. Record the actual failure edge
rather than describing all runtime calls as deoptimization or all deopts as crashes.

## Follow side effects that can invalidate a checked fact

Trace stores, accessors, coercions, callbacks, allocation/GC and relevant shared
state between proof and use. Determine which facts the compiler preserves and
which it invalidates or rechecks. For a suspected omission, state the precise
sequence: established fact, reachable invalidating effect, stale optimized use.

Distinguish a guest/application policy error from compiler miscompilation. Valid
language behavior on unusual input may take a generic path without violating
memory safety. Missing a second check in disassembly is a lead, not a conclusion.

## Reconstruct deoptimization and GC state at the actual transition point

Identify the native PC's deoptimization/stack-map entry, logical continuation,
inlined frames and live value representations. Follow relocated references rather
than equating preserved machine registers with stable object addresses. Check
whether already completed effects are preserved without unintended duplication.

Use reference-jit-deoptimization-gc-state. A metadata-assisted reconstruction is
not a literal copy of the optimized native frame. Keep absent metadata and
compiler-version uncertainty explicit instead of assigning source variables to
every stack word.

## Separate compiler-error evidence from runtime and application effects

A useful compiler-bug hypothesis identifies the language/runtime rule, the
optimization assumption, a feasible input/state violating it, and the emitted
operation that then produces the wrong effect. Tier-specific behavior alone is
not proof: code identity, timing, GC and application nondeterminism can also differ.

For malware, trace the generating input and actual generated behavior into host
effects. Warming a method, changing shapes or allocating executable memory can be
normal runtime behavior. Preserve the distinction between capability, reachable
behavior and observed execution; runtime attribution does not establish benign intent.

## Account for binary instrumentation around generated code

When a trace uses translated copies, recover the analysis tool's code mapping as
well as the application's method/compilation map. Preserve the original bytes,
translation generation and capture time. A code-cache address is not directly a
module RVA or managed bytecode offset.

Check collection gaps around code replacement and late hook installation before
calling a missing event anti-analysis behavior. Tool-generated regions also need
to be distinguished from runtime stubs and application payloads. Use
playbook-validation-binary-only-evidence for instrumentation, model and stop-reason
limits; this does not require additional execution.

## Evidence basis and scope

Reviewed 2026-10-02. Procedure applies the three JIT references above and their
primary sources. It does not prescribe universal tier thresholds, private object
offsets, debugger flags or an engine-specific exploit recipe. WebAssembly host
authority belongs in playbook-re-webassembly-boundary; embedded JavaScript/native
lifetimes belong in playbook-re-embedded-script-boundary.
