---
id: vulnerability-runtime-untrusted-reflection-dynamic-member-selection
title: Untrusted reflection, dynamic member or runtime type selection
kind: vulnerability
topics: [reflection, dynamic-dispatch, type-resolution, member-lookup, capability]
platforms: [cross-platform]
architectures: [any]
---

# Untrusted reflection, dynamic member or runtime type selection

## Definition and violated invariant

This vulnerability occurs when less-trusted names or metadata select a runtime type, constructor, method, field, property, module, class loader, or equivalent capability outside an approved dispatch set, and the selected operation is invoked or exposed with security-relevant authority. The invariant is that external names may select only explicitly authorized operations and objects for the requesting actor and context.

Reflection and dynamic lookup are mechanisms. Their presence is not a weakness when selection is closed, the resolved member is checked, or all reachable operations are authorized for the caller.

## Conditions that establish the issue

Identify the attacker-controlled name after decoding, the namespace and loader or assembly context, lookup flags and visibility rules, overload/signature selection, receiver or constructed type, argument conversion, invocation, and resulting capability. Prove the chosen member or type is outside the intended allowlist and reaches a sensitive effect.

For class or module loading, bind the textual name to the actual loaded code origin and identity. For field or property access, establish whether accessors or descriptors execute code rather than assuming a passive data read.

## Evidence that is not sufficient

`Class.forName`, `Type.GetType`, `Activator.CreateInstance`, `getattr`, a reflection namespace, or a string matching a dangerous method is not sufficient. The input may be constant, an allowlist may map external names to fixed operations, lookup may fail, the member may be inaccessible, or no invocation may occur.

A private-member bypass flag can enlarge the surface but does not establish a security boundary by itself; identify the caller, target object, runtime policy, and effect.

## Investigation sequence

Trace raw input through normalization and mapping to the final lookup. Recover loader, module, assembly or realm identity and enumerate only members reachable under the actual flags and signature. Follow the returned type/member object to construction, invocation, delegate creation, serialization, registration, or capability transfer.

At binary level, resolve metadata tokens and call sites rather than relying on decompiler method names. Check exception and fallback paths because a failed preferred lookup can select a broader default. Preserve the process identity and resources available to the invoked code.

## Constructed C# example and IL shape

```csharp
object Dispatch(string typeName, string methodName, object argument)
{
    Type type = Type.GetType(typeName, throwOnError: true)!;
    object target = Activator.CreateInstance(type)!;
    return type.GetMethod(methodName)!.Invoke(target, new[] { argument })!;
}
```

```il
ldarg.0
ldc.i4.1
call       class System.Type System.Type::GetType(string, bool)
stloc.0                                                    // selected Type
ldloc.0
call       object System.Activator::CreateInstance(class System.Type)
stloc.1                                                    // receiver
ldloc.0
ldarg.1
callvirt   class System.Reflection.MethodInfo System.Type::GetMethod(string)
stloc.2                                                    // selected MethodInfo
ldloc.2
ldloc.1
ldloc.3                                                    // prepared object[] arguments
callvirt   object System.Reflection.MethodBase::Invoke(object, object[])
```

The symbolic IL is an investigation shape, not exact compiler output. The issue requires attacker influence over the selected names, an admitted sensitive type/member, compatible arguments, and actual invocation. A fixed mapping from external commands to approved members would change the conclusion.

## Primitive and impact limits

The primitive is unauthorized selection of a concrete runtime operation or capability. Impact is the selected operation's effect under the consumer's authority; code execution requires selection or loading of executable behavior, not merely enumeration or metadata access.

## Primary sources and scope

Reviewed 2026-10-09 against Java SE [`Class.forName`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html#forName(java.lang.String)), .NET [`Type.GetType`](https://learn.microsoft.com/en-us/dotnet/api/system.type.gettype), [`Activator.CreateInstance`](https://learn.microsoft.com/en-us/dotnet/api/system.activator.createinstance), and [`MethodBase.Invoke`](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.methodbase.invoke), plus Python [`getattr`](https://docs.python.org/3/library/functions.html#getattr) for a distinct dynamic-member contract. Apply the actual runtime and loader rules; these APIs are examples, not a universal ABI.
