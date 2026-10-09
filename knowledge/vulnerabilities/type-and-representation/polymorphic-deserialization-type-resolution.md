---
id: vulnerability-type-polymorphic-deserialization-resolution
title: Polymorphic deserialization and runtime type-resolution confusion
kind: vulnerability
topics: [deserialization, polymorphism, type-resolution, object-construction, callbacks]
platforms: [cross-platform]
architectures: [any]
---

# Polymorphic deserialization and runtime type-resolution confusion

## Definition and violated invariant

A polymorphic-deserialization vulnerability occurs when attacker-influenced data selects a runtime type outside the consumer's intended closed set, or when a permitted type is bound under the wrong assembly, loader, schema, generic, or base-interface identity. Type selection, object construction, lifecycle callbacks, member population, and final dispatch must remain bound to an explicit trusted contract.

This profile covers the type-resolution root. A gadget chain or dangerous callback is a later execution path and requires its own reachable side effect; a type-name string alone does not prove activation.

## Conditions that establish the issue

Identify serializer and active implementation, metadata or tag enabling type selection, resolver/binder/converter, accepted type identities, assembly or module loading context, constructors or callbacks, populated state, and final consumer. Prove untrusted input can select or construct a type not authorized for that position and reach a security-relevant operation or incompatible dispatch.

Validation by simple name, assignability, or interface alone may be too broad when multiple implementations carry different authority. Conversely, an exact closed mapping can constrain type choice while member values and callbacks still require review.

## Evidence that is not sufficient

Polymorphism, `$type`, class names in serialized bytes, a binder, reflection imports, or serializer metadata is not sufficient. Type metadata may be disabled, records may be decoded without activation, the implementation may reject use, or the resolver may enforce a closed set.

Do not infer remote reachability, gadget availability, or code execution from API presence.

## Investigation sequence

Trace raw type metadata through parsing, normalization, resolver lookup, loader identity, allowlist decision, allocation, member assignment, callbacks, and final virtual/interface use. Enumerate nested objects and collection element types, not only the root.

At IL or native boundaries, identify actual resolved type handles and constructor/callback targets. Bind validation to the same loaded type object used for construction and account for handled errors or partially populated state.

## Constructed resolver example

```csharp
Type Resolve(string requestedName)
{
    return loadedTypes.First(t => t.Name == requestedName);
}

ICommand command = (ICommand)Deserialize(payload, Resolve(typeName));
command.Execute();
```

Simple-name matching can select an unintended loaded type when more than one assembly defines that name, and interface compatibility alone does not authorize its `Execute` behavior. The finding requires attacker control of `typeName`, effective use of this resolver, an unintended matching type, and a reachable effect. A closed mapping from protocol tags to exact trusted type identities would change the result.

## Primitive and impact limits

The direct primitive is unauthorized object type selection or construction. Consequences can include callback side effects, wrong object state, gadget dispatch, resource exhaustion, or type confusion. Code execution requires the selected path to reach an execution-capable operation.

## Related knowledge and primary sources

`reference-dotnet-serializer-type-and-state-boundaries`, JVM/Python serializer references, and `vulnerability-dotnet-deserialization-gadget-chain` provide concrete mechanisms. This profile repeats the type-identity binding requirement locally.

Reviewed 2026-10-09 against Microsoft [BinaryFormatter security guidance](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide), Microsoft [NRBF record decoding](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/read-nrbf-payloads), Json.NET [serialization settings](https://www.newtonsoft.com/json/help/html/SerializationSettings.htm), and [MITRE CWE-502](https://cwe.mitre.org/data/definitions/502.html). The resolver example is constructed.
