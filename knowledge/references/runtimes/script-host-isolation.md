---
id: reference-script-host-isolation
title: Embedded script contexts, native capabilities, bytecode trust and execution limits
kind: reference
topics: [embedded-scripting, javascript, sandboxing, bytecode, resource-limits, host-capabilities]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64]
---
# Script-host isolation and capability evidence

## Separate globals are not an operating-system security boundary

Node's node:vm runs code in V8 contexts but explicitly is not a security mechanism
for untrusted code. [1] QuickJS contexts within one runtime can share objects;
separate runtimes cannot exchange their JavaScript objects. [2]

Neither fact establishes which native authority the host exposes. Recover
reachable host functions, objects and loaders before describing confinement.
An empty-looking global object is weak evidence when a supplied callback returns
a privileged object. Conversely, the mere presence of an interpreter does not
prove that untrusted input can supply executable scripts.

## Native bindings define reachable capabilities beyond the language core

V8 function/object templates can expose C++ functions and property callbacks to
scripts. [3] Duktape's sandboxing discussion explicitly treats C code as trusted. [4]

For a boundary investigation, treat each binding as a capability: name the
operation, native target, accepted values and authority used. A generic file,
command, module or memory wrapper can undermine a script policy without any
interpreter memory-corruption bug. Establish the mismatch between the intended
policy and the reachable operation; powerful functionality intentionally exposed
to a trusted script is not itself a vulnerability.

## Precompiled bytecode is not necessarily an untrusted input format

QuickJS documents version-coupled bytecode without execution security checks.
Duktape requires valid, intact bytecode compatible with the engine configuration;
malformed bytecode can cause memory-unsafe behavior. [2,4]

Trace binary-chunk input separately from source-text input, including decrypted,
decompressed or resource-embedded payloads. A successfully parsed header is not
proof of safe instructions. For malware identification, recover the loading and
execution path before assigning behavior to bytes that merely resemble a chunk.
Lua-specific loader rules are in `reference-lua-host-boundaries`.

## QuickJS memory limits and interrupt callbacks have distinct scope

QuickJS offers per-runtime memory limits, maximum stack-size configuration and
an interrupt callback periodically consulted during engine execution. [2]

Do not turn those APIs into a claim that all host work is bounded. Identify native
allocations, blocking I/O, recursively entered bindings and pending jobs outside
the metered operation. Determine what actually stops on budget exhaustion and
whether partially completed effects remain. A configured limit is evidence of
one control, not proof of total process containment or transaction rollback.

## Node vm timeouts do not automatically cover every asynchronous callback

Node documents microtaskMode 'afterEvaluate' for running a context's microtasks
within evaluation timeout handling. Callbacks scheduled on shared/global queues,
including exposed scheduling functions and some outer-context callbacks, are not
thereby controlled by that timeout. [1]

Trace which context creates a callback, which queue receives it and when that
queue runs. Returning from evaluation does not prove all induced work has ended.
For a resource-exhaustion or stale-context finding, establish the queued operation
and cleanup ordering; do not infer either from a timeout option alone.

## Interpreter threads, contexts and native threads are different identities

Duktape permits only one active native thread per heap at a time; different heaps
can execute concurrently. Its language threads do not change that requirement. [4]
QuickJS does not support multithreaded execution inside a runtime. [2]

In a host using worker threads, identify which heap/runtime owns each object and
how callbacks are serialized. Independent engine heaps do not prevent host
callbacks from sharing a process-global native resource. Analyze that resource's
synchronization separately; runtime isolation is not a lock for application data.

## Primary sources and scope

Reviewed 2026-10-02. Node docs identify v26.10.0; Duktape guide identifies 2.6.0.
QuickJS/V8 sources are living project documentation. These examples establish
specific embedding contracts, not a claim that all script engines have identical
security or scheduling models. Workflow: `playbook-re-embedded-script-boundary`.

1. [Node.js vm documentation](https://nodejs.org/api/vm.html): security warning, timeout and microtask/context interactions.
2. [QuickJS manual](https://bellard.org/quickjs/quickjs.html): runtime/context identity, bytecode and resource controls.
3. [V8 embedding guide](https://v8.dev/docs/embed): function templates, accessors and interceptors.
4. [Duktape Programmer's Guide](https://duktape.org/guide.html): bytecode dump/load, threading and sandboxing (2.6.0).
