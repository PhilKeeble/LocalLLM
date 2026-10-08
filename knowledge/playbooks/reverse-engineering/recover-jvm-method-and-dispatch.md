---
id: playbook-re-jvm-method-and-dispatch
title: Recover a JVM method, selected class definition and dynamic dispatch path
kind: playbook
topics: [reverse-engineering, jvm, java, bytecode, reflection, dispatch, class-loading]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Recover a JVM method and dispatch path

## Preserve the selected artifact and runtime context

Reviewed 2026-10-02. Record container/entry/class hashes, runtime vendor/build,
launch configuration, class path/module path, versioned JAR entry and known
agents/custom loaders. Separate JVM class files from Android DEX/ART and native
code. Do not infer the active class from a matching archive filename alone.

Inspect preserved bytes without loading unknown classes or invoking constructors,
initializers or bootstrap methods. Use bounded extraction/parser resources.
Record disassembler version and explicit input selection; compare decompiled
source to bytecode for security-relevant operations. Missing dependencies or
unsupported format in the analyst's tool are not yet target failures.

## Establish exact method and bytecode coordinates

Keep class-byte identity, binary name, defining loader when known, method name,
complete descriptor, definition version and BCI. Resolve operands against the
caller's constant pool; do not join equal pool indices across classes.
Separate generic source/Signature metadata from the actual method descriptor.

Identify Code versus abstract/native declaration. Decode instruction boundaries,
wide operands, switch padding/counts and branch bases. Preserve code extent,
local/stack types and exception table entries. For each guard and sink show the
actual compared/converted value, including integer wrap, signedness and casts.
Facts: reference-jvm-class-file-evidence and reference-jvm-bytecode-semantics.

## Reconstruct ordinary and exceptional control flow together

Follow fallthrough/branch edges and ordered applicable handlers. Track earlier
field writes, callbacks and resource acquisitions through rejection, cleanup,
rethrow and catch-and-return paths. Do not assume a Java exception undoes work.
Distinguish verifier rejection from an application check or runtime linkage error.

State the operation invariant: an allowed range, ownership/tenant relation,
authorized operation or legal state transition. A wrapped integer alone is not
a finding until its feasible downstream use violates that invariant. A native
corruption claim requires the separate native allocation/access evidence.

## Resolve receiver and loader before accepting a call edge

Record invocation opcode, owner/name/descriptor and actual receiver type.
Trace resolution and selection separately, including bridges, interface
implementations, initialization and native binding. Follow delegation to the
defining loader; equal printed class names do not prove identical live types.

Include class initializers that run before the intended operation. Preserve the
first initialization exception before diagnosing later NoClassDefFoundError as
a missing dependency. A loader cache or already erroneous Class changes a repeat
test; document the state rather than silently treating it as fresh execution.

## Follow reflection, handles and bootstrap results explicitly

Recover input-controlled class/member names, parameter Class identities,
discovery API, caller module, effective access configuration and actual Method.
For Method.invoke retain receiver-selected implementation and failure stage.
Separate member discovery, access permission and application authorization.

For handles recover Lookup provenance/modes, creation, adapters, bound receiver
and complete invoke/invokeExact descriptor. For invokedynamic or dynamic
constants follow bootstrap handle/arguments and the installed result. Keep
bootstrap execution separate from target execution, including concurrent attempts.
Facts: reference-jvm-loading-and-reflection.

## Bind observed execution to the selected class definition

When an authorized runtime observation is necessary, record loader/Class,
definition version, active frame, JIT/native range and observation time. Preserve
known instrumentation or replacement history; old frames and new invocations
can differ. Do not attach agents, redefine classes or alter module access merely
to make an inspection succeed without authorization for that change.

Separate bytecode/configuration deductions from observations of the active
definition and exact executed path. If no runtime evidence is available, state
which loader, receiver or generated-code premise remains unresolved. Arithmetic
reasoning alone does not establish VM acceptance, JIT behavior, loader execution
or target exploitability.

For malware analysis, follow class loading, initialization, reflective arguments
and installed dynamic-call targets into actual effects. A method or bootstrap
name is a lead, not proof of execution or intent. Ordinary runtime machinery can
support either benign or malicious behavior; recovered control/data flow decides
what the specimen can do and observations establish what it did in that run.

## Sufficiency and counterevidence

A supported hypothesis ties controlled input to the selected artifact/method,
actual guard-to-use path, runtime/loader scope and violated invariant. Include
the missing edge if any. Counterevidence can be a different selected JAR entry,
failed resolution/access before target entry, checked arithmetic with an effective
failure path, or a receiver that cannot reach the suspected implementation.

This workflow covers class/bytecode/loading/reflection. It does not by itself
validate JNI reference/pointer lifetimes or object-deserialization filters and
callbacks. Use playbook-re-jni-boundary for the native transition and
playbook-re-jvm-deserialization-boundary for Java object reconstruction; a
type-safe Java frame does not establish a safe native or serializer boundary.

## Sources and factual homes

- [JVMS 25](https://docs.oracle.com/javase/specs/jvms/se25/html/index.html): format and instruction contracts, not fixed implementation layouts.
- [JDK 25 MethodHandle](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodHandle.html): typed dynamic calls.

reference-jvm-class-file-evidence, reference-jvm-bytecode-semantics and
reference-jvm-loading-and-reflection retain scoped facts and inspected source
sections. This is investigation guidance, not evidence of a real target defect.
