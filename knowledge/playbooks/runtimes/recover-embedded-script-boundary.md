---
id: playbook-re-embedded-script-boundary
title: Trace embedded scripts through native bindings, capabilities and callback lifetime
kind: playbook
topics: [reverse-engineering, embedded-scripting, native-bindings, vulnerability-analysis, malware-analysis]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# Investigate an embedded script/native boundary

## Locate script input and the first execution edge

Identify the engine using converging evidence: imports, registration APIs,
initialization patterns and value handling. Distinguish source compilation,
bytecode deserialization and execution. Trace bytes from resources, files,
configuration, updates or network input, through transformations to the engine.

Record who can control those bytes and whether integrity is checked before use.
A string containing script syntax is not execution evidence; a linked engine is
not proof the sample uses it. For malware analysis, connect the loader to a
reachable trigger and recover which payload actually reaches it.

## Recover script names, native callbacks and captured authority

Build a compact mapping for relevant bindings: script-visible name, native
wrapper, captured state, argument conversion, downstream operation and result.
Follow returned objects and module loaders as well as global registrations.
For Lua, distinguish a native result count from pushed script values. For
JavaScript, separate each engine's handle/reference model.

Use `reference-lua-host-boundaries`, `reference-javascript-native-lifetimes` and
`reference-script-host-isolation`. A suspicious API name is a lead; its actual
native destination and available authority determine the capability.

## Audit conversion before auditing the sensitive operation

For each script-controlled argument, record accepted types, coercion, failure
indicator, numeric range, text encoding and byte extent. Follow the exact value
used by the sink, not just a pre-conversion check. Identify callbacks or property
accesses that can run script during conversion and invalidate earlier state.

Distinguish type validation from authorization. A valid path string does not
authorize opening that path; a valid object wrapper does not authorize another
request to use its native handle. State the expected policy and the feasible
path that violates it before labeling a binding vulnerable.

## Reconstruct ownership across callbacks, errors and teardown

Track script value, native wrapper, native allocation and execution context as
separate lifetimes. Locate strong roots or reference acquisitions rather than
assuming a copied native pointer keeps a value alive. Inspect cancellation,
registration failure, duplicate close, shutdown and exceptional cleanup edges.

For asynchronous work, identify the owning queue and the last possible callback.
For re-entry, ask which invariants are temporarily broken when script regains
control. Report the actual invalidation/use ordering; a runtime finalizer or
reference-count helper alone is not evidence of a lifetime defect.

## Evaluate confinement and resource limits against reachable host work

Determine which native resources a script can reach and which controls apply at
the effect, including any real process or OS restrictions. Separate language
contexts, interpreter heaps and native execution threads. Inspect bytecode trust
and module-loading authority independently of source-language checks.

For availability, trace allocations, recursion, queued jobs and blocking native
operations to the corresponding limit or cancellation mechanism. A timeout is
not proof that all work has stopped. A memory quota is not proof that external
native allocations are included. Preserve unknown scope rather than assuming it.

## Report vulnerability evidence and malware behavior separately

For a vulnerability, name the controlled input, violated invariant, reachable
native path and resulting effect. For malware, distinguish capability presence,
feasible invocation and observed execution, including the data source and
destination. Obfuscated scripts, runtime embedding and dynamic evaluation also
appear in legitimate applications.

Use `playbook-re-sensitive-data-flow` for source-to-effect tracing and
`playbook-re-validate-library-attribution` to separate engine/library code from
sample-specific logic. Keep unresolved bindings and missing payload conditions
visible in the conclusion rather than treating them as negative evidence.

## Evidence basis and scope

Reviewed 2026-10-02. Procedure grounded in the engine contracts cited in the three
runtime references above. CPython extension specifics belong in
`playbook-re-python-native-boundary`; this workflow does not replace their API
ownership and interpreter-lifecycle rules.
