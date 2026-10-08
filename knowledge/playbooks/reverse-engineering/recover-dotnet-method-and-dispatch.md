---
id: playbook-re-dotnet-method-dispatch
title: Recover a .NET method, runtime identity and dispatch path
kind: playbook
topics: [reverse-engineering, dotnet, il, metadata, reflection, dispatch, code-identity]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Recover a .NET method and dispatch path

## Establish the artifact before selecting a runtime model

Record hashes, packaging, architecture, CLR/native headers, dependency/runtime
configuration and available matching symbols. Distinguish .NET Framework,
modern .NET, ReadyToRun and Native AOT using corroborating evidence. Static
metadata/version strings alone do not establish the runtime actually used.
Keep unknown build/deployment choices explicit.

Use metadata readers or a deliberately configured metadata-only context for
unknown assemblies. Do not invoke entry points, property getters or attribute
constructors for discovery. A parser must still bound malformed metadata. If
runtime observation is needed, use an authorized isolated environment and
record what code is executed; reflection is not automatically passive.

## Resolve one method and its actual signature

Preserve module/hash, MVID, token and IL offset as one coordinate tuple. Resolve
the call-site token in the caller's module, keeping generic type and method
arguments separate. Record the defining assembly and load context when available.
Do not bind unrelated methods through equal tokens or printed type names.

Decode method header, code extent, local signature and EH sections separately.
Read instruction operand kinds rather than treating every integer as an RVA or
metadata token. Check signed branch bases and switch table bounds. Reconstruct
evaluation-stack types/values at joins and retain unresolved signatures instead
of guessing a pointer width from the host analysis tool.

## Recover reflective selection before treating it as a call edge

For GetMethod/Invoke or reflective property access, retain input-controlled name,
actual Type identity, lookup flags, signature, generic arguments and binder.
Separate discovery from invocation. An ambiguous lookup, missing trimmed member,
bad target or rejected argument can stop the path before target code runs.

Map the selected MethodInfo or accessor back to its defining module and body.
Identify application authorization separately from public/nonpublic lookup.
If invocation throws, distinguish the wrapper/inner exception and target-entry
trace from binding failure; do not assume earlier getter or binder effects were
rolled back. Facts: reference-dotnet-loading-code-identity.

## Trace receiver, guards and sink through the IL

For call/callvirt, distinguish static versus instance signature, declared method,
runtime receiver and resolved implementation. For constrained instance calls,
establish closed T and whether the operation uses the original managed address,
a dereferenced object or a boxed copy. Do not infer a native vtable slot solely
from callvirt, or assume every constrained call avoids allocation.

Follow attacker-influenced values through loads, aliases, checked/unchecked
conversions, comparisons and call arguments. Verify exact opcodes at the guard
and use. Include EH/filter/cleanup edges; a reconstructed source-language
checked block or using statement is a hypothesis until supported by IL and
handler ranges. State a violated bound or operation invariant, not just a
suspicious method name or reflection import.

## Join IL evidence with a native observation

At the relevant runtime stop, bind the method to the active native code range,
runtime build and generic instantiation. R2R on disk and JIT code in memory may
both exist; preserve observation time and code version. Validate a native
instruction consequence without treating JIT offsets as IL offsets.

For P/Invoke or unsafe/native callbacks, continue with
playbook-re-dotnet-native-boundaries and retain both managed and native
coordinates. For loader-related findings, prove which assembly/module was
selected and what lower-trust actor controlled it. A separate load context is
not evidence of sandboxing; an Unload request is not proof of completed unload.

## Trace one delegate or asynchronous operation to terminal use

Recover the delegate signature, selected invocation list and captured storage.
Follow copies and event removal: a removed subscriber can remain in a snapshot.
For task-returning multicast invocation, identify whether all returned operations
are joined or only the final return is observed. Locate native registration,
delegate roots, unregister and in-flight callback drain before accepting lifetime.

Map async stubs to state machines; trace actual suspension/resume paths rather
than assuming await always schedules elsewhere. Record reloaded state and any
identity/authorization check on each side. Track exceptions through the actual
Task, async-void boundary or custom awaiter. Cancellation request is not terminal
completion; identify the event that releases each resource and prove late users
are excluded. Facts: reference-dotnet-delegates-async-lifetimes.

## Evidence sufficient to accept or reject a hypothesis

A useful result contains the exact entry and resolved method, affected value
and invariant, feasible guard-to-use path, runtime/deployment scope and observed
consequence or explicit missing edge. Include counterevidence: checked overflow,
unreachable dispatch, mismatched token scope, absent input control, or a load
failure before the sink. Do not convert a failing inspection API into target
behavior or a successful load into trusted identity.

This workflow establishes metadata/dispatch and operation-lifetime evidence.
Marshaller layout and serializer-specific validation require their separate
contracts; recovering one method does not accept those other surfaces.
Continue with playbook-re-dotnet-deserialization-boundary for object decoding,
type selection and the actual constructor/setter/callback validation path.

## Sources and factual homes

Reviewed 2026-10-02. reference-dotnet-metadata-il-evidence holds instruction,
token and method-body rules; reference-dotnet-loading-code-identity holds
runtime, load-context, inspection and trust distinctions.

- [CLI specification](https://ecma-international.org/publications-and-standards/standards/ecma-335/): scoped normative format/instruction reference.
- [Module.ResolveMethod](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.module.resolvemethod?view=net-10.0): token and generic context.
- [MetadataLoadContext](https://learn.microsoft.com/en-us/dotnet/standard/assembly/inspect-contents-using-metadataloadcontext): metadata-only inspection.
