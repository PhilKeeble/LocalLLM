---
id: vulnerability-parser-deserialization-callback-gadget-side-effect
title: Deserialization callback, constructor, gadget, or reconstruction side effect
kind: vulnerability
topics: [parsers, deserialization, callbacks, constructors, gadget-chains, object-reconstruction]
platforms: [cross-platform]
architectures: [any]
---

# Deserialization callback, constructor, gadget, or reconstruction side effect

## Definition and violated invariant

A deserialization side-effect vulnerability occurs when attacker-influenced data causes object construction, type resolution, setters, converters, callbacks, hooks, proxy behavior or later graph use to perform an operation outside the intended data-decoding contract. The selected implementation, permitted types, reconstruction lifecycle and every reachable side effect must be appropriate for the input's trust boundary.

This profile covers execution during or because of reconstruction. Polymorphic type-selection confusion is a related root, while a gadget chain requires a concrete sequence of available operations and attacker-controlled state reaching a security-relevant sink.

## Conditions that establish the issue

Identify exact serializer and active mode, entry point and untrusted bytes, schema or type metadata, resolver/filter/allowlist, allocated types, constructors bypassed or invoked, field assignment order, setters and conversions, lifecycle callbacks, nested graph, gadget methods, final consumer and process authority. Prove the input selects and configures a reachable side effect that violates policy.

For a chain, record every edge from deserialized state to the next callable operation and the preconditions each gadget supplies. API presence, a known gadget type or a type name in bytes is not enough.

## Evidence that is not sufficient

A serializer import, reflection, callbacks, serializable type, class name, rejected payload, historical gadget name or deserialization crash is not sufficient. Type metadata may be disabled, a closed schema may apply, decoding may avoid activation, or the chain may lack a reachable sink in this build.

Do not infer remote reachability, code execution or privileges from unsafe capability alone. Trace the actual boundary and resulting operation.

## Investigation sequence

Follow bytes through format parsing, type selection, allocation, population, conversions, callbacks and final graph consumption. Preserve callback order and partially initialized state. Enumerate nested collection and extension-data types, not only the root.

For binary analysis, identify actual constructor/callback targets and values supplied at each call. Separate a parser accepting data from a later application method that activates it, while retaining their common object identity.

## Constructed callback example

```csharp
sealed class Job
{
    public string Command { get; set; }
    [OnDeserialized]
    void Ready(StreamingContext context) => Scheduler.Enqueue(Command);
}
```

If an untrusted serializer constructs `Job`, populates attacker-controlled `Command`, and invokes `Ready`, reconstruction schedules an operation before ordinary application validation. The finding requires that this serializer honors the callback, permits the type and property, and that `Scheduler.Enqueue` reaches a forbidden effect. The attribute alone does not establish any of those facts.

## Primitive and impact limits

The direct primitive can be unauthorized file/network access, command or process dispatch, callback execution, resource exhaustion, state mutation or type-confused final use. Code execution requires an execution-capable reachable sink and suitable attacker control.

## Related knowledge and primary sources

`vulnerability-dotnet-deserialization-gadget-chain`, `vulnerability-type-polymorphic-deserialization-resolution`, and runtime serialization references provide concrete ecosystems. This profile repeats complete reconstruction-to-effect proof locally.

Reviewed 2026-10-09 against Microsoft [.NET serialization callbacks](https://learn.microsoft.com/en-us/dotnet/standard/serialization/serialization-events), Microsoft [BinaryFormatter security guidance](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide), Serde [custom conversion attributes](https://serde.rs/container-attrs.html), and [MITRE CWE-502](https://cwe.mitre.org/data/definitions/502.html). The source is constructed.
