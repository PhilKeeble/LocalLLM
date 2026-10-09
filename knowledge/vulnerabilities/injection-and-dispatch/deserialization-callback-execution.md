---
id: vulnerability-injection-deserialization-callback-execution
title: Unsafe deserialization through permitted callbacks or reconstruction behavior
kind: vulnerability
topics: [injection, deserialization, callbacks, gadget-chains, object-graphs, code-execution]
platforms: [cross-platform]
architectures: [any]
---

# Unsafe deserialization through permitted callbacks or reconstruction behavior

## Definition and violated invariant

Deserialization execution occurs when attacker-controlled serialized data selects types, functions, constructors, setters, callbacks, reducers, proxies, or object relationships whose permitted reconstruction behavior performs an unintended operation. The deserializer must treat untrusted input as data under a closed schema; it must not let the input choose behavior-capable objects or a graph whose normal callbacks compose into a security-relevant side effect.

The dangerous mechanism is serializer-specific. Java object streams can invoke class-defined reconstruction callbacks; Python pickle can resolve and call globals; .NET object-graph serializers have their own type resolution and callbacks. Generic type allowlisting is not a universal safety claim, and Microsoft states that `BinaryFormatter` cannot be made safe for untrusted input through a binder or configuration switch.

## Conditions that establish the issue

Recover the exact serializer and format, attacker control and integrity gate, concrete type/function resolution, filters or binders, graph depth and references, constructors, setters, reconstruction callbacks, validation callbacks, replacement/resolution hooks, property access, post-deserialization consumers, exception timing, and process authority. Prove that an input-controlled graph reaches an unintended callback or later behavior with attacker-controlled arguments and a security-relevant effect.

For a gadget chain, document every link's input values, invocation rule, returned object, ordering, and required environment. A known gadget class present in a dependency is not enough; it must be permitted, constructible, connected, and reached by the selected serializer.

## Evidence that is not sufficient

A serializer API, polymorphic type metadata, callback method, gadget-capable class, dependency, deserialization exception, or object construction is not sufficient. Input may be authenticated, the type may be unreachable or rejected, the callback may not run under this serializer, required properties may be unavailable, or the resulting action may remain within the intended data contract.

Final failure does not prove earlier callbacks were rolled back. Conversely, callback presence does not prove any submitted graph invokes it.

## Investigation sequence

Trace bytes into the exact deserializer and record resolver/filter state. Build a graph ledger containing serialized record, resolved runtime type or global, allocation path, field/property writes, callback phase, replacement object, exception boundary, and side effect. Follow both success and failure paths and preserve actions that occur before rejection.

At managed/native boundaries, recover virtual or reflective dispatch and host calls made by callbacks. Confirm the arguments, effective identity, working directory, environment, network or filesystem target, and observable result before assigning execution impact.

## Constructed Java object-stream example

```java
ObjectInputStream input = new ObjectInputStream(requestBody);
Object message = input.readObject();
dispatch((Message) message);
```

`readObject` reconstructs a transitive object graph and can invoke class-specific reconstruction and validation behavior under Java's serialization contract. This call becomes an execution vulnerability only if attacker-controlled bytes can select a permitted reachable class graph whose callbacks perform an unintended effect. The cast and later dispatch do not prevent effects that already occurred during reconstruction.

## Primitive and impact limits

The direct primitive is invocation of behavior selected through serialized data during or after object reconstruction. Consequences can include file or network access, process launch, data disclosure, resource exhaustion, state mutation, or code execution under the deserializing process. Impact depends on reachable types/functions, filters, libraries, environment and process authority; deserialization exposure alone is not proof of a working chain.

## Related knowledge and primary sources

`vulnerability-parser-deserialization-callback-gadget-side-effect`, serializer-specific references, and object-reconstruction playbooks contain deeper lifecycle detail. This profile repeats chain reachability and pre-failure side-effect requirements locally.

Reviewed 2026-10-09 against Java [`ObjectInputStream`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputStream.html), Python [`pickle`](https://docs.python.org/3/library/pickle.html), and Microsoft's [`BinaryFormatter` security guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide). The Java source is constructed; current runtime availability and serializer behavior must be established from the target.
