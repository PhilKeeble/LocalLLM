---
id: reference-dotnet-loading-code-identity
title: .NET assembly loading, reflection and generated-code identity
kind: reference
topics: [dotnet, assembly-loading, reflection, jit, readytorun, native-aot, type-identity]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET loading, reflection and code identity

## Scope: runtime and deployment are independent evidence

Reviewed 2026-10-02 against the Microsoft sources below. .NET Framework,
.NET Core/modern .NET, ReadyToRun and Native AOT do not have identical loading
or code-generation behavior. An executable extension, embedded runtime-version
string or CLR directory alone does not identify the complete deployment model.
These references cover documented contracts, not fixed internal object layouts.

Inference: retain target artifact, OS/architecture, loaded runtime build,
dependency configuration, selected assembly instances and any code-generation
settings. A self-contained app still has runtime support; it does not follow
that it uses no runtime or that it is Native AOT. Module-local tokens and IL
coordinates are covered in reference-dotnet-metadata-il-evidence.

## ReadyToRun is not a guarantee that the JIT never runs

JIT means just-in-time compilation of managed methods to native instructions
during execution. ReadyToRun (R2R) assemblies contain intermediate language (IL)
and precompiled native code and target a specific runtime environment.
Some methods/scenarios still require JIT code,
and tiered compilation can replace commonly used R2R methods with JIT-generated
versions. Generics, interop and dynamically created methods are among the
documented reasons that precompilation does not eliminate the JIT. [1]

Inference: the native body found on disk need not be the body executing at the
fault. Record the runtime-selected code range and method mapping at observation
time. A breakpoint at an old address or missing call in one code version does
not establish that the logical method no longer executes. R2R symbol identity
and IL identity are complementary, not interchangeable coordinates.
For code-version and native-address lifetime evidence across runtimes, see
reference-jit-code-identity and playbook-re-jit-generated-code.

## Native AOT is a different execution contract

Ahead-of-time (AOT) compilation produces native code before application execution.
Current Microsoft Native AOT documentation describes publish-time IL-to-native
compilation with no application JIT at runtime. It includes needed runtime
libraries, requires trimming, and does not support dynamic managed assembly
loading such as Assembly.LoadFile or runtime code generation via Reflection.Emit.
Platform/architecture support is version-specific. [2]

Inference: this is not a rule forbidding every reflection operation or every
native-library load. Inspect retained metadata and supported APIs for the target.
No JIT does not imply no garbage collector (GC), no managed types or no native boundary. Native
debug information and machine instructions are needed when ordinary IL-body
recovery is unavailable; do not force a JIT-only debugger model onto that image.

## AssemblyLoadContext separates identities, not security domains

AssemblyLoadContext applies to .NET Core/modern .NET, not .NET Framework.
One context caches one assembly version per simple name; resolving against an
already loaded entry requires a version at least as high as requested. Separate
contexts can hold different assembly instances with equally named types.
Their isolation is name resolution, not a binary security barrier. [3]

Inference: a cast failure between identical printed type names can indicate
different Assembly instances, not heap corruption. Trace Type.Assembly and the
actual load context; sharing an Assembly instance shares its type definitions.
Conversely, loading an untrusted plugin into another context does not sandbox
its file, process or native-call authority. Access policy needs a real boundary.

## Collectible load context unloading is cooperative

AssemblyLoadContext.Unload initiates unloading; completion waits until relevant
code is no longer on thread stacks and blocking strong references/GC handles
are absent. A normal or pinned GCHandle can keep the context alive. This differs
from forced .NET Framework AppDomain unloading. [4]

Inference: a returned Unload call is not proof that code or native dependencies
have been released. Retained delegates, tasks and host caches are lifetime
leads that require a root trace. A weak reference alone is not a strong root.
Do not report a native use-after-unload solely from the request to unload, or
assume that one GC request guarantees completion of the unload protocol.

## Metadata-only reflection differs from executing attribute constructors

MetadataLoadContext treats loaded assemblies as metadata and cannot execute
their code. Its resolver explicitly supplies dependencies; it does not
automatically use the current directory. GetCustomAttributes would execute
constructors; GetCustomAttributesData is the inspection route. Type comparisons
must use types within the same metadata context, not mix them with runtime Types.
[5]

Inference: missing dependency resolution during inspection is not proof that
the target cannot load it. Conversely, using the main execution context plus
attribute construction or reflective invocation is execution, not passive
metadata reading. Unknown assemblies should not be loaded/invoked just to learn
their names; bounded static inspection still needs malformed-input safeguards.

## Reflection method lookup is scoped, not an authorization decision

Type.GetMethod(string) searches public methods and can throw
AmbiguousMatchException for multiple matching overloads. BindingFlags-based
lookup distinguishes instance/static and public/nonpublic members; DeclaredOnly
excludes inherited members. Signature-bearing overloads and generic context
matter; a name alone need not identify one callable method. [7, 8]

Inference: recover the actual Type/assembly/load context, lookup overload,
flags, parameter types, generic arguments and any custom binder. Record which
MethodInfo was selected, not merely the input name. A successful lookup is not
application authorization to invoke that member. An empty lookup under one
set of flags does not prove the member is absent from the binary. Availability
under trimming/AOT is a separate deployment question.

## Reflective invocation and property reads execute target code

MethodBase.Invoke executes the selected method; the instance target and argument
list must satisfy its invocation contract. The ordinary Invoke(object, object[])
path reports a target-thrown exception through TargetInvocationException;
argument-count/type or target failures are different paths. An applicable
DoNotWrapExceptions flag requests unwrapped exceptions, so wrapper absence is
not proof that no reflective call occurred. PropertyInfo.GetValue calls the
property accessor: reading a property is not passive field/metadata inspection.
[8-10]

Inference: distinguish failure before target entry from failure inside the
invoked code, retaining the inner exception and call trace where available.
Getters, methods and custom binders may have side effects; an exception does
not establish rollback. Unknown target code must not be invoked merely to
enumerate metadata. Inspect the actual runtime/overload rather than applying
old .NET Framework reflection-permission rules to every modern deployment.

## Strong-name identity is not publisher trust or authorization

Microsoft explicitly warns against relying on strong names for security.
For .NET Core and .NET 5+, the runtime does not validate strong-name signatures
or use strong names for assembly binding as described for .NET Framework. [6]
The public-key token is not proof that a trusted publisher supplied the running
bytes, and a CLR strong-name field is distinct from an Authenticode signature.

Inference: an allowlist matching display name/public-key token alone cannot be
reported as an authenticated artifact check. Establish the actual verification
mechanism, object and result. Even successfully authenticated code still needs
operation-specific authorization and defect analysis; do not infer safety from
a signing field or load success.


## Sources

1. [ReadyToRun compilation](https://learn.microsoft.com/en-us/dotnet/core/deploying/ready-to-run): mixed IL/native image and tiered replacement.
2. [Native AOT deployment](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/): no JIT, runtime support, trimming and dynamic-code restrictions.
3. [Understanding AssemblyLoadContext](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/understanding-assemblyloadcontext): cache, version, type identity and isolation.
4. [Assembly unloadability](https://learn.microsoft.com/en-us/dotnet/standard/assembly/unloadability): cooperative completion and roots.
5. [MetadataLoadContext inspection](https://learn.microsoft.com/en-us/dotnet/standard/assembly/inspect-contents-using-metadataloadcontext): metadata-only behavior and attribute access.
6. [Strong-named assemblies](https://learn.microsoft.com/en-us/dotnet/standard/assembly/strong-named): identity/security distinction and runtime-family differences.

## Reflection API sources

Reviewed 2026-10-02, .NET 10 API view; overload contracts are distinct from
historical .NET Framework permission notes embedded in the same pages.

7. [Type.GetMethod](https://learn.microsoft.com/en-us/dotnet/api/system.type.getmethod?view=net-10.0): public-name lookup, ambiguity and signature/flag overloads.
8. [BindingFlags](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.bindingflags?view=net-10.0): search scope, DeclaredOnly and DoNotWrapExceptions.
9. [MethodBase.Invoke](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.methodbase.invoke?view=net-10.0): targets, arguments, exception paths and default overload.
10. [PropertyInfo.GetValue](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.propertyinfo.getvalue?view=net-10.0): accessor invocation and retrieval exceptions.
