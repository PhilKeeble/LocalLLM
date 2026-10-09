---
id: vulnerability-lifetime-cleanup-bypass-nonlocal-control-flow
title: Cleanup failure across exceptions, cancellation, unwind, panic, or signal paths
kind: vulnerability
topics: [lifetime, cleanup, exceptions, unwind, cancellation, longjmp, panic]
platforms: [cross-platform]
architectures: [any]
---

# Cleanup failure across exceptions, cancellation, unwind, panic, or signal paths

## Definition and violated invariant

A cleanup-control-flow vulnerability occurs when a nonlocal exit or exceptional path bypasses a required release, rolls cleanup in the wrong order, releases a partially initialized resource incorrectly, or reports success while leaving sensitive partial effects. Relevant mechanisms include language exceptions, cancellation, unwind, `longjmp`, panic/recover, signals, thread exit, and process termination, each with distinct cleanup behavior.

Cleanup must correspond to resources actually acquired and effects already committed on that path. Running too little can leak or retain authority; running too much can double release or act on uninitialized state.

## Conditions that establish the issue

Recover the selected language/runtime mechanism, protected instruction range, acquisition milestones, cleanup handlers or deferred calls, partial effects, continuation, and final status. Prove a feasible exit skips or misorders an obligation and causes a security-relevant retained resource, stale state, duplicate release, unsafe continuation, or fail-open result.

For partially constructed objects, destroy only completed subobjects under the applicable language rules. A complete-object destructor may be wrong on one failure path and required on another.

## Evidence that is not sufficient

An exception-capable call, landing pad, `defer`, catch block, signal handler, or missing linear release call is not sufficient. Metadata or structured cleanup can cover the edge, the call may be nonthrowing under its actual contract, or process termination may make ordinary resource release irrelevant while leaving external effects intact.

Two cleanup sites can be mutually exclusive. Reconstruct path conditions before counting releases.

## Investigation sequence

Build an acquisition-state table for every point that can exit nonlocally. Map unwind metadata, handlers, cleanup funclets, deferred calls, cancellation points, and terminal exits to the resources and effects present at that point. Follow cleanup failures and exceptions raised during cleanup.

At binary level, distinguish normal continuation from exceptional edges and identify parent-frame access in cleanup helpers. Do not interpret unwind metadata as proof a cleanup executed in an observed run.

## Constructed C++ example

```cpp
void process()
{
    native_resource resource = acquire_resource();
    operation_that_can_throw(resource);
    release_resource(resource);
}
```

If acquisition succeeds and the operation throws, ordinary control never reaches the release. The finding requires no RAII owner, catch cleanup, outer ownership transfer, or process-lifetime contract to cover `resource`, plus a consequential retained resource or partial effect. A binary call to `release_resource` only on the normal successor and no applicable cleanup edge supports that path after exception behavior is established.

## Primitive and impact limits

The direct result may be a leak, retained lock or authority, partial transaction, duplicate release, inconsistent object, or misleading success. Memory corruption, denial of service, or privilege impact depends on the retained resource and later behavior.

## Related knowledge and primary sources

`reference-native-cpp-lifecycle-unwind`, `reference-windows-msvc-exception-cleanup-evidence`, and runtime-specific unwind references define concrete mechanisms. This profile repeats acquisition-state and path requirements locally.

Reviewed 2026-10-09 against C++ [constructor/destructor exception cleanup](https://eel.is/c++draft/except.ctor), the [Itanium exception-handling ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html), Go [defer, panic, and recover](https://go.dev/blog/defer-panic-and-recover), and [MITRE CWE-459](https://cwe.mitre.org/data/definitions/459.html). The example is constructed.
