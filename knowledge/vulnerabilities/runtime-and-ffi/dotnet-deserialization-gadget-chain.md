---
id: vulnerability-dotnet-deserialization-gadget-chain
title: .NET deserialization with attacker-controlled type construction and gadget chains
kind: vulnerability
topics: [dotnet, deserialization, type-resolution, gadget-chain, callbacks]
platforms: [windows, linux, macos]
architectures: [any]
---

# .NET deserialization with attacker-controlled type construction and gadget chains

## Definition and violated invariant

A .NET deserialization vulnerability exists when less-trusted serialized data can make a consuming process construct or populate types outside an approved data contract, or invoke application behavior before adequate validation. A gadget chain is a reachable sequence of constructors, serialization callbacks, setters, converters or other methods whose combined side effects produce an unintended operation.

The required invariant is that input selects only an approved schema and values, and that reconstruction cannot perform unauthorized effects. The vulnerability is the reachable input-to-effect chain; a serializer name, type metadata string or gadget-capable class in loaded code is not the chain by itself.

## Conditions that establish the issue

Identify the bytes an attacker can influence, the exact serializer implementation and active configuration, the deserialization call reached, effective type-resolution policy, types available to the process, and callbacks or methods invoked during reconstruction. Then trace controlled members through a complete gadget sequence to a file, process, network, reflection, loading or other security-relevant effect under the process's authority.

Microsoft states that `BinaryFormatter.Deserialize` is unsafe for untrusted input and cannot be made safe by a `SerializationBinder` or configuration switch. For a target finding, still establish that a functioning implementation executes: an API reference can resolve to a throwing or replacement implementation depending on deployment.

## Evidence that is not sufficient

Serialized-looking bytes, `$type` metadata, a reference to `BinaryFormatter`, an `ISerializable` type, `[OnDeserialized]`, or a known gadget class is not sufficient. The path may be unreachable, the runtime may reject the operation, type metadata may be disabled, an allowlist may exclude the type, the required assembly may be absent, or the side-effecting member may never receive controlled state.

A post-deserialization validation call does not disprove earlier effects. Conversely, a callback before validation is not automatically dangerous; inspect its body and the values available at that point.

## Investigation sequence

Trace the trust boundary from file, IPC, network, database, clipboard, cache or synced storage to the stream or reader passed to the serializer. Recover the concrete library, overload, settings, binder or resolver, surrogate, converter, expected root type and runtime/package implementation. Determine whether input can select types directly or only populate a closed set.

For each admitted type, recover construction semantics, field/property assignment, `ISerializable` constructors, lifecycle callbacks, collection behavior and error continuation. Build the gadget chain in execution order and preserve the controlled value at every edge. Stop the conclusion at the strongest demonstrated effect and record the process token, sandbox and accessible resources separately.

## Constructed .NET source example

This hypothetical legacy path passes an externally influenced stream to a functioning `BinaryFormatter` implementation:

```csharp
object LoadState(Stream input)
{
    var formatter = new BinaryFormatter();
    return formatter.Deserialize(input);
}
```

The call is an unsafe trust boundary for untrusted input under Microsoft's documented contract, but source presence alone does not prove execution in a deployed runtime. Establish the stream's provenance, active implementation and reachable call. Other serializers require their own type-selection and callback analysis rather than inheriting `BinaryFormatter` conclusions by analogy.

## Constructed callback gadget

This hypothetical serializable type performs a file read during an `OnDeserialized` callback:

```csharp
[Serializable]
sealed class Report
{
    public string Path = "";
    [NonSerialized] public string? CachedText;

    [OnDeserialized]
    private void AfterDeserialization(StreamingContext context)
    {
        CachedText = File.ReadAllText(Path);
    }
}
```

This establishes a useful gadget only if the selected serializer can construct `Report`, attacker data controls `Path`, the callback runs before a rejecting boundary, and the read has an observable or chainable consequence. The snippet demonstrates one side effect, not remote code execution or a universal .NET callback order.

## Constructed IL evidence

The following symbolic IL omits assembly qualification and offsets. It shows the stack order for the deserialization call and a possible callback body; it is not a byte signature:

```il
newobj   instance void BinaryFormatter::.ctor()
ldarg.0
callvirt instance object BinaryFormatter::Deserialize(Stream)
ret

ldarg.0
ldarg.0
ldfld    string Report::Path
call     string File::ReadAllText(string)
stfld    string Report::CachedText
ret
```

Resolve the actual metadata tokens and method bodies. A `callvirt` instruction can be used for instance-call null checking even when no meaningful virtual dispatch occurs; it does not itself prove attacker-selected method resolution.

## Primitive and impact limits

The direct primitive is attacker-influenced object construction and execution of a demonstrated reconstruction-time side effect. Denial of service can arise from graph depth, allocation or expensive callbacks without a gadget chain for code execution. File access, network access, process launch and reflection are different primitives and must be reported separately.

Remote code execution requires a remotely influenceable payload, a complete available gadget chain reaching execution or an equivalent code-loading effect, and sufficient process authority. Do not infer it from the general danger of a formatter or from public knowledge that gadget chains exist.

## Related knowledge and primary sources

`reference-dotnet-serializer-type-and-state-boundaries` owns serializer-family differences, type selection, callbacks and deployment qualifications. `reference-dotnet-metadata-il-evidence` owns token and IL interpretation. The decisive trust-boundary and gadget-chain proof is repeated here for isolated use.

Reviewed 2026-10-09 against Microsoft's [BinaryFormatter security guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide), [BinaryFormatter migration guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/), [.NET serialization callbacks](https://learn.microsoft.com/en-us/dotnet/standard/serialization/serialization-callbacks), and [ECMA-335](https://ecma-international.org/publications-and-standards/standards/ecma-335/) for CLI metadata and IL. The source, callback and symbolic IL are constructed examples.
