---
id: reference-jvm-class-file-evidence
title: JVM class-file coordinates, descriptors, strings and artifact selection
kind: reference
topics: [jvm, java, class-file, constant-pool, descriptors, jar, bytecode]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# JVM class-file evidence

## Scope and artifact coordinates

Reviewed 2026-10-02 against Java SE 25 specifications and JDK 25 documentation.
This is Java Virtual Machine (JVM) class-file evidence, not Android DEX/ART or a fixed HotSpot object
layout. Older targets need their applicable class-file/API versions.

Inference: identify container hash, exact entry path, class-byte hash, binary
name, method name plus descriptor, and bytecode index (BCI). At runtime add
defining loader, runtime build and definition/code version. A BCI is neither
a ZIP offset nor a native instruction address. Workflow:
playbook-re-jvm-method-and-dispatch; execution rules:
reference-jvm-bytecode-semantics; loading: reference-jvm-loading-and-reflection.

## Class-file header and constant-pool indices

Class files start with CAFEBABE, then minor/major versions. Multibyte fields are
big-endian. Constant-pool entries are variable-sized and indexed from 1;
CONSTANT_Long/Double consume two indices, with the second unusable. [1]

Inference: do not calculate a constant-pool byte offset by multiplying its index
by a fixed entry size. Validate each tag, extent and referenced entry kind before
following it. Keep indices local to the containing class: equal #17 operands in
two classes do not identify the same symbol. Magic bytes alone do not prove a
complete, accepted class file or distinguish every enclosing file format.

## Version acceptance is not just a major-version ceiling

SE 25 supports major versions 45-69. For majors 56+, minor is 0 or 65535.
Version 69.65535 requires SE 25 preview enablement; older preview versions are
not accepted by that SE 25 VM. [1]

Inference: preserve both fields and launch settings. A newer VM does not simply
accept every older preview class. A major version describes format compatibility,
not proof of the exact compiler, runtime in use or available dependency APIs.
Do not label a class malformed solely because the analyst's older tool rejects it.

## Descriptors retain types and return values, not source names

JVM method descriptors have form (parameters)return; arrays use [, references
use Linternal/name;, and V denotes a void return. The implicit receiver is not
encoded among parameters. [1]

Constructed example: (IJ[BLpkg/Request;)Z means int, long, byte[], Request ->
boolean. B/C/D/F/I/J/S/Z denote byte/char/double/float/int/long/short/boolean.
Retain the complete descriptor rather than a decompiler's shortened name.

MethodType.fromMethodDescriptorString resolves named types through its supplied
loader; identical descriptor strings can describe different live MethodTypes
when the named classes have different defining loaders. [2]
Inference: descriptor parsing with live type resolution is not equivalent to a
pure string parser. Resolve identity before joining reflective call evidence.

## Modified UTF-8 differs from standard UTF-8

CONSTANT_Utf8 uses modified UTF-8. [1] In this encoding NUL uses C0 80, and
supplementary characters use separately encoded UTF-16 surrogates, not standard
UTF-8's four-byte form. DataInput.readUTF has a two-byte encoded-byte length,
not a character count. [3]

Constructed example: A, NUL, U+1F600 encodes as
41 C0 80 ED A0 BD ED B8 80: nine modified-UTF-8 bytes, four UTF-16 units.
Its standard UTF-8 representation has six bytes. These are distinct encodings,
not evidence that one decoder accepts all the other's byte sequences.
Inference: preserve raw bytes and the exact decoding API before comparing names,
wire lengths or a JNI transition. Do not use C-string truncation or ordinary
UTF-8 decoding as a class-file string parser.

## Code and exception metadata use method-local coordinates

Code contains max_stack, max_locals, code_length, instruction bytes and handler
metadata. code_length is 1-65535. Native/abstract methods have no Code attribute.
Handler coverage is [start_pc,end_pc); catch_type=0 catches all exceptions. [1]

Inference: the absence of Code can be legitimate, not successful recovery of an
empty method. Resolve native implementations separately. End offsets delimit
coverage and are not necessarily instruction addresses to execute. A catch-all
entry is not proof of a particular source finally statement or guaranteed
resource release: inspect its body and every exit. Ordered handler behavior is
in reference-jvm-bytecode-semantics.

## Stack maps are type-verification evidence, not input validation

StackMapTable supports bytecode type checking. For class-file version 50.0+,
absence means an implicit zero-entry table, not automatic exemption from
verification. [1]

Inference: stack/type consistency does not establish tenant authorization,
protocol validity, bounded allocation or absence of logic bugs. Keep verifier
acceptance separate from application checks. A decompiler failing to reconstruct
structured source does not prove the VM rejects the bytecode; conversely,
readable reconstructed Java does not prove the original bytes verify.

## Generic source types and bridge methods need separate evidence

Java erasure removes parameterization; a type variable erases to its leftmost
bound's erasure, not invariably Object. [4] Compiler-generated bridge methods
can connect source overrides to JVM method signatures, including covariant
return cases. [5]

Inference: a displayed List<Request> is not proof that all runtime elements are
Requests or validated Requests. Recover actual casts and consumption checks.
Do not drop a synthetic/bridge method as irrelevant before following its
forwarding/cast behavior. Preserve full return descriptors when two JVM methods
look identical after the decompiler hides their return-type difference.

## Multi-release JAR selection changes the bytes under investigation

For a JAR marked Multi-Release: true on an applicable class/module path, lookup
searches META-INF/versions/N downward to 9, then the base entry, for runtime
release N. Boot-class-path use is an exception: the JAR is treated as ordinary.
A module descriptor on the class path does not make the JAR an explicit module.
[6]

Inference: compare the selected entry, not just the archive filename or base
class. A patch in one versioned entry may not affect another deployment. Record
the loader/tool's actual selection rules before claiming the target runs the
bytes inspected. Custom packaging/loading needs its own trace.

## Static disassembly describes selected bytes, not the active class

A class-file disassembly needs exact input identity: container and entry, class
hash, method name/descriptor, instruction bytes and exception metadata. An
inspector's implicit archive selection need not match the target's class loader.
Multi-release selection rules therefore matter before interpreting an apparently
missing method or patch. [6]

Inference: retain the selected bytes and the inspection capability's version and
limits. Static decoding does not execute the class's main method, but it parses
potentially malformed input. Its output is not an observation of a live JVM's
selected or transformed definition; establish that connection separately through
loader and definition identity. No particular disassembler is required.

## Sources: format and runtime types

1. [JVMS 25 chapter 4](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-4.html): 4.1, 4.3, 4.4.5/7, 4.7.3/4; format, versions and local coordinates.
2. [MethodType](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/invoke/MethodType.html): fromMethodDescriptorString/toMethodDescriptorString and loader identity.
3. [DataInput](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/DataInput.html): modified UTF-8 and readUTF byte length.
4. [JLS 25 type erasure](https://docs.oracle.com/javase/specs/jls/se25/html/jls-4.html#jls-4.6): parameterized types and type-variable bounds.

## Sources: bridges and artifact selection

5. [Method.isBridge](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/reflect/Method.html#isBridge()): JVM/source signature differences.
6. [JAR specification](https://docs.oracle.com/en/java/javase/25/docs/specs/jar/jar.html): modular and multi-release JAR lookup and boot-loader exception.
