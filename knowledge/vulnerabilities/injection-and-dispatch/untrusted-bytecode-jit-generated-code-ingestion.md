---
id: vulnerability-injection-untrusted-bytecode-jit-generated-code-ingestion
title: Untrusted bytecode, JIT input, or generated-code ingestion
kind: vulnerability
topics: [injection, bytecode, jit, generated-code, webassembly, runtimes, trust-gates]
platforms: [cross-platform]
architectures: [any]
---

# Untrusted bytecode, JIT input, or generated-code ingestion

## Definition and violated invariant

An untrusted-code ingestion vulnerability occurs when attacker-controlled bytecode, intermediate representation, shader, rule program, generated source, machine code, or compiled module is accepted and executed without the origin, integrity, authorization, structural validation, and capability restrictions required by the application. Format or type validation and application trust are separate: a structurally valid module can still intentionally exercise every capability the host exposes.

The trust boundary depends on the runtime. WebAssembly modules declare imports and execute within a store and host-defined environment; JVM class loading, .NET assembly loading, eBPF verification, GPU shaders, database procedures, and custom virtual machines have different validators and host interfaces. JIT-generated executable memory is ordinary for many runtimes and does not by itself identify an injection vulnerability.

## Conditions that establish the issue

Recover input provenance, signature or authorization policy, format and architecture selection, validator and its result, compiler/JIT flags, imports and host functions, memory/table/global or equivalent capabilities, module namespace, initialization/start behavior, generated-code mapping and protections, entry selection, effective identity, resource limits, and control transfer. Prove attacker-controlled code passes or bypasses the intended trust gate and reaches an operation outside its authorized capability set.

For native generated code, bind source or bytecode generation to the exact executable range and execution generation. For sandboxed code, enumerate imported or ambient capabilities and any escape or confused-deputy path rather than equating code execution inside the sandbox with host-native execution.

## Evidence that is not sufficient

Bytecode bytes, a compiler/JIT API, executable anonymous memory, a loaded module, successful validation, disassembly, or an exported entry point is not sufficient. The input may be trusted, execution may be absent, validation may enforce the intended policy, or host capabilities may be appropriately constrained.

A signature blob is not a trust verdict, and structural verifier success is not authorization. Conversely, untrusted code can be an intended feature when confinement and exposed capabilities satisfy the product policy.

## Investigation sequence

Trace input through decoding, identity selection, integrity/authentication, authorization, validation, compilation, caching, instantiation, imports, initialization, entry lookup, and execution. Record exact module hash, generation, runtime context, host capability bindings, generated range, protection changes, and observed control transfer. Distinguish requested compilation, successful compilation, instantiation, and execution effects.

At binary level, map the returned module or code handle through entry resolution to the indirect call. Correlate runtime metadata with live bytes and account for relocation, tiering, recompilation, deoptimization, and address reuse before attributing a captured range.

## Constructed WebAssembly host example

```text
module = validate_and_compile(request.module_bytes)
instance = instantiate(module, imports = privileged_host_functions)
entry = instance.export("run")
entry()
```

WebAssembly validation can establish module well-formedness and type safety under the selected specification, while instantiation binds host-provided imports and can run initialization. If product policy requires only approved modules but `request.module_bytes` lacks that authorization gate, a valid attacker module can deliberately invoke every imported function its types permit. Host-native code execution requires an exposed host capability or a separate runtime defect.

## Constructed System V AMD64 indirect-entry shape

```asm
; Illustrative System V AMD64 host-side shape. rax = resolved generated-code entry, rbx = runtime context.
test    rax, rax
jz      .fail
mov     rdi, rbx
call    rax                     ; control transfer to the selected compiled generation
```

This proves execution only after `rax` is tied to the compiled attacker-controlled module and the call is observed or statically reachable. It does not identify the module's imports, validate its provenance, or show escape from the runtime's capability boundary.

## Primitive and impact limits

The direct primitive is execution of attacker-selected instructions in a runtime or virtual machine under the capabilities bound to that instance. Consequences can include misuse of host functions, data access, resource exhaustion, application logic control, or native code execution. Sandbox escape, kernel execution, and privilege escalation each require an additional boundary-crossing primitive or overpowered host capability.

## Related knowledge and primary sources

`reference-runtime-jit-code-identity`, WebAssembly, JVM bytecode, managed loading, and code-provenance references provide deeper runtime evidence. This profile keeps structural validity, authorization, capability binding, and actual execution distinct.

Reviewed 2026-10-09 against the WebAssembly [Core Specification](https://webassembly.github.io/spec/core/), the JVM [class-file verification](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-4.html#jvms-4.10) and [initialization](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html#jvms-5.5) contracts, and Microsoft [.NET assembly loading](https://learn.microsoft.com/en-us/dotnet/core/dependency-loading/overview). The source and assembly are constructed and do not depend on one runtime implementation.
