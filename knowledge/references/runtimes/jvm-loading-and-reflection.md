---
id: reference-jvm-loading-and-reflection
title: JVM loader identity, initialization, reflection and method-handle boundaries
kind: reference
topics: [jvm, java, class-loading, reflection, initialization, method-handles, instrumentation]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# JVM loading and reflection

## Scope and evidence categories

Reviewed 2026-10-02 against Java SE/JDK 25 sources. These are documented contracts,
not observed behavior of a production target or a universal model of every
historical JDK. JVM bytecode differs from DEX/ART. A class-file artifact is not
automatically the active definition after loading, transformation or redefinition.
Coordinates: reference-jvm-class-file-evidence. Instruction consequences:
reference-jvm-bytecode-semantics. Workflow: playbook-re-jvm-method-and-dispatch.

## Defining loader is part of live type identity

For ordinary named JVM classes/interfaces, identity combines binary name and
defining loader. The initiating loader can differ through delegation; run-time
package identity also incorporates the defining loader. User-defined loaders
can locate, generate or otherwise supply class bytes. [1]

Inference: equal package/class spellings and identical disk hashes do not prove
two live Class objects are interchangeable. Preserve actual defining loaders,
not just the thread-context loader or the object asked to load the name. A
cast/linkage failure may reflect identity or deployment mismatch, not corrupted
memory. A different namespace/loader alone is not evidence of an OS/process
security boundary or authority restriction.

## Loading without initialization is not a universal no-execution guarantee

Class.forName(name) requests initialization. The (name, initialize, loader)
overload can request loading without initializing that class by passing false;
it does not undo initialization already performed. [2] Loader code itself can
have arbitrary behavior. [1]

Inference: initialize=false is not a safe metadata-inspection sandbox. Unknown
loaders, agents and dependencies must not run merely to enumerate a binary.
Prefer bounded class-file inspection; if live loading is authorized, record
the loader and initialization side effects separately. A successful name lookup
does not establish that the caller may access or invoke every member.

## Initialization can change state before the intended method runs

Java initialization triggers include construction, declared static-method
invocation, and qualifying nonconstant static-field use. Merely reading an
inherited static field initializes its declaring type, not necessarily the
subclass used to spell the access. Recursive initialization by the same thread
can proceed while initialization is incomplete. [3]

Inference: include class initializers in the entry-to-sink path. A default-valued
field observed during a cycle need not be a native uninitialized read. Record
initialization order and side effects before assuming a guard executed against
fully established static state. The full superclass/default-interface procedure
is versioned; do not infer order solely from source class names.

## NoClassDefFoundError can follow failed initialization

Java's initialization procedure marks a class erroneous after initialization
failure. A later initialization attempt for that Class throws
NoClassDefFoundError. A non-Error initializer exception is normally wrapped in
ExceptionInInitializerError on the initial failure. [3]

Inference: NoClassDefFoundError is not conclusive evidence of a missing JAR.
Preserve the first failure/cause, loader and Class identity, including earlier
dependency initialization errors. Retrying with the same Class is not a clean
initialization experiment; a fresh isolated process or deliberately distinct
definition changes state and must be labeled. Rejection does not prove earlier
initializer effects were rolled back.

## getMethods and getDeclaredMethods search different member sets

Class.getMethods covers public methods including inherited ones;
getDeclaredMethods includes nonpublic declared methods but excludes inherited
ones. Named lookup also takes formal parameter Class objects. [2]

Inference: record the exact lookup API, declaring class/loader and parameter
identities. An absent result under one search scope does not prove the method is
absent from the class hierarchy. A matching name does not establish a callable
overload, successful access check or application authorization.

## setAccessible and trySetAccessible do not grant application authority

In JDK 25, setAccessible is constrained by module/package access; it is not an
unconditional bypass. trySetAccessible returns false when access cannot be
enabled rather than that failure's InaccessibleObjectException. [4]

Inference: keep selected member, declaring class/loader, parameter identities,
caller module and effective opens/exports. Finding a private member does not
prove the call succeeds. Conversely, access-check suppression is not application
authorization for attacker-selected operations. Do not generalize a successful
unnamed-module test to a different module configuration.

## Method.invoke performs real dispatch and has distinct failure stages

Method.invoke can dispatch an instance override using the receiver's runtime
type. Static invocation initializes the declaring class if needed. Target-thrown
exceptions are wrapped in InvocationTargetException; access, argument and
initialization failures have distinct documented paths. [5]

Inference: a Method obtained from a base class is not proof its base body ran.
Preserve the receiver, resolved body, underlying cause and whether target entry
occurred. A wrapper exception does not establish a parser rejection, rollback
or complete failure of an earlier side effect. Inspect the invoked body and
caller catch behavior, not just the reflection API import.

## Method handles transfer access already checked at creation

MethodHandles.Lookup checks member access when creating handles, not afresh
against each later handle caller. Lookup objects carry a lookup class and
allowed access modes; sharing one can delegate member-lookup capability. [6]

Inference: trace who obtained and retained the Lookup or MethodHandle and which
members its actual modes permit. A handle reaching lower-trust code may expose
operations that code could not discover directly. That is an authority-flow
lead, not proof of a bypass: establish intended policy and reachable use.
Do not assume method handles use Method.invoke's per-call access behavior.

## invokeExact includes the return type; invoke permits adaptation

MethodHandle.invokeExact requires the resolved call-site type to match the
handle type exactly. invoke can adapt through asType. Type matching includes
live Class identities, not only descriptor spelling; incompatible signatures
can produce WrongMethodTypeException. [7]

Inference: retain argument and return descriptors plus receiver-bound/adapted
handles. A boxed runtime value is not enough to explain the call-site static
type. Distinguish adapter/type-check failure before the operation from an
exception thrown by the target. A decompiler's Object... rendering can hide
the signature-polymorphic descriptor actually present in bytecode.

## invokedynamic and dynamic constants can execute bootstrap code

Dynamic resolution invokes a bootstrap MethodHandle and validates its result:
a computed constant value or a CallSite. Concurrent resolution can run a
bootstrap more than once, while one result is installed. invokedynamic linkage
is specific to the instruction, not merely a shared constant-pool index. [1]

Inference: follow BootstrapMethods, static arguments, type descriptor and the
installed target; do not infer lambda semantics from invokedynamic alone.
Bootstrap side effects or failure may precede the intended operation. One
installed result does not prove exactly one bootstrap execution. A fixed linked
CallSite identity does not itself establish an immutable target; inspect the
actual call-site implementation and changes at observation time.

## Retransformation can leave active frames running old bytecodes

Instrumentation supports class retransformation/redefinition subject to VM
capabilities and constraints. Active frames of affected methods continue using
old bytecodes, while new invocations use the new definition. Redefinition does
not rerun class initialization or reset static variables. [8]

Inference: record agent configuration, definition version and observation time.
A disk patch or a replacement class dump is not proof that an already-running
frame executes that body. Do not trigger redefinition on a shared target for
inspection. Tie a native-code observation to its active managed definition,
not just method name, and keep redefinition separate from JIT optimization.
Compiled-body load/unload and native-address lifetime evidence are in
reference-jit-code-identity; the investigation workflow is
playbook-re-jit-generated-code.

## Historical SecurityManager policy is not a JDK 25 sandbox

The JDK 25 SecurityManager API states that its former security-policy feature
no longer exists. The retained class is deprecated for removal. [9]

Inference: a policy file, SecurityManager import or old analysis recipe does
not establish confinement on a JDK 25 deployment. For older deployments record
the exact runtime and enabled mechanism instead of retroactively applying this
rule. Modules, verifier checks and loaders answer different questions; none is
by itself evidence that arbitrary loaded code lacks process/file authority.

## Sources: identity and initialization

1. [JVMS 25 loading/linking](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html): 5.3 identity/delegation; 5.4.3.6 dynamic linkage/concurrency.
2. [Class API](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html): forName overloads and method discovery.
3. [JLS 25 initialization](https://docs.oracle.com/javase/specs/jls/se25/html/jls-12.html#jls-12.4): triggering uses, recursion and erroneous initialization state.
4. [AccessibleObject](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/AccessibleObject.html): setAccessible/trySetAccessible and module scope.
5. [Method.invoke](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html#invoke(java.lang.Object,java.lang.Object...)): receiver dispatch and failure stages.

## Sources: capabilities and live code

6. [MethodHandles.Lookup](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandles.Lookup.html): access checking, lookup class and delegated capability.
7. [MethodHandle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandle.html): signature polymorphism, exact matching and adaptation.
8. [Instrumentation](https://docs.oracle.com/en/java/javase/25/docs/api/java.instrument/java/lang/instrument/Instrumentation.html): retransformClasses/redefineClasses, active frames and initialization.
9. [SecurityManager in JDK 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/SecurityManager.html): removed policy feature; not an older-runtime reproduction.
