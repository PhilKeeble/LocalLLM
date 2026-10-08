---
id: reference-jit-code-identity
title: Generated-code identity, compilation versions, native address maps and runtime stubs
kind: reference
topics: [jit, generated-code, code-identity, symbols, jvmti, malware-analysis]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# Identifying generated native code

## One logical method can have several compiled bodies and inlined appearances

JVMTI CompiledMethodLoad reports native code address and size for a compilation.
The specification permits multiple compiled forms of one method and multiple
inlined methods in an address range. Optional address-location mappings can be
absent; location interpretation is given by GetJLocationFormat. [1]

Record process/runtime, method definition, native range, compilation identity and
observation time. A method name alone is too weak to identify a faulting body.
Do not substitute a bytecode offset for a native offset or assume one source line
maps to one contiguous native interval. A missing mapping is missing evidence,
not proof the bytes are unrelated to managed code.

## Compiled-code addresses have lifetimes and may be reused

JVMTI CompiledMethodUnload may arrive after the actual unload but before reuse
by newly generated compiled code. Its method/address parameters are identification
data: the class or memory may already be gone. Movement is represented by unload
followed by load. [1]

Correlate event order and capture time before resolving a historical PC against
the current map. An old symbol name at the same numeric address can misattribute
a crash or behavior. Absence of a load event is inconclusive if collection began
late, events were disabled, or the VM lacked the optional capability.

## Runtime-generated helpers are distinct from compiled application methods

JVMTI DynamicCodeGenerated describes generated VM components, such as interpreter
code, rather than compiled Java methods. Its display name need not be unique. [1]

An executable private-memory region is not automatically a payload. Determine
who generated it, the runtime role, incoming calls and actual effects. Equally,
finding a legitimate JIT does not establish that all private executable regions
belong to it. Attribute each relevant region; distinguish runtime stubs from
application-generated methods and unexplained code.

## GDB JIT symbol registration describes code; it does not authenticate it

GDB's JIT interface lets a runtime register in-memory symbol files using a shared
descriptor/list and a well-known notification function. On attachment GDB can
discover existing registrations. When code is freed, the interface defines a
matching unregister operation. [2,3]

Registered symbols help recover boundaries and names but originate from the
debuggee. Correlate them with bytes and ownership; a plausible registered name is
not trusted provenance. Missing symbols can reflect absent integration or stale
registration rather than malicious concealment. Do not call every unsymbolized
frame an independent native function.

## Native code on disk may differ from the body selected by the runtime

For .NET, ReadyToRun and tiered JIT replacement are covered in
reference-dotnet-loading-code-identity. For JVM definition replacement, active
frames and class identity, use reference-jvm-loading-and-reflection. Definition
replacement and recompilation of the same definition are different events.

During a binary investigation, retain both the original artifact and the native
code actually associated with the observation. Do not claim the disk image's
missing instruction rules out a runtime-generated effect. Conversely, an address
change or new code version is not by itself evidence of code injection.

## Application JIT code and analysis-tool translations have different identities

A binary instrumentation tool can execute generated copies of application code.
Frida Stalker's original and translated ranges are one documented example; see
reference-validation-binary-instrumentation-evidence for the source and cache
rules. This is distinct from the application's own runtime compiling a method.

Investigative consequence: retain both mappings when they coexist. Resolving a
tool-cache PC with the application's JIT map can misidentify the method or invent
a payload address. Attribute executable regions to their generator and code
generation before using their permissions, names or allocation timing as malware
evidence. Missing mappings leave identity unresolved rather than proving evasion.

## Primary sources and scope

Reviewed 2026-10-02. JVMTI 25 is a tooling contract, not a universal code-cache
layout; event capabilities and enablement matter. GDB's living JIT documentation
describes an integration protocol, not all runtime implementations. Workflow:
playbook-re-jit-generated-code.

1. [JVMTI 25 specification](https://docs.oracle.com/en/java/javase/25/docs/specs/jvmti.html): CompiledMethodLoad, CompiledMethodUnload and DynamicCodeGenerated.
2. [GDB JIT interface](https://www.sourceware.org/gdb/current/onlinedocs/gdb.html/JIT-Interface.html): discovery and symbol registration.
3. [GDB unregistering JIT code](https://www.sourceware.org/gdb/current/onlinedocs/gdb.html/Unregistering-Code.html): code-lifetime notification.
