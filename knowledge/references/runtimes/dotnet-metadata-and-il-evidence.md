---
id: reference-dotnet-metadata-il-evidence
title: .NET metadata tokens, method bodies and IL interpretation
kind: reference
topics: [dotnet, cli, metadata, il, dispatch, exceptions, integer-conversions]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET metadata and IL evidence

## Scope and coordinates

Reviewed 2026-10-02. ECMA-335 sixth edition (2012) defines the Common Language
Infrastructure (CLI). Its intermediate language (IL) is the instruction form
described here; it is not the processor's native instruction set. The scoped
layout rules below use that edition; Microsoft opcode/API contracts corroborate
interpretation.
These are not assertions about every newer runtime extension, obfuscator or
compiler lowering. A managed method, its IL body and a generated native code
version are distinct objects. Runtime/loading identity is in
reference-dotnet-loading-code-identity; PE CLR-header routing remains in
format-pe-directories-loader-metadata.

An investigation coordinate should retain module artifact/hash, MVID (module
version ID) when available, method token and IL offset. MVID is a metadata GUID
used to distinguish module versions, not a content hash or publisher check. [14]
Native observations additionally need the actual code range/version and runtime
build. A token is not a PE RVA,
and an IL offset is not a byte offset into JIT machine instructions.

## Metadata table tokens are module-local, not executable addresses

For table tokens, the high byte identifies the table and the low 24 bits give
its row. Example: 0x06000004 identifies MethodDef row 4, not code at RVA
0x06000004. Names and signatures reside in metadata heaps referenced by tables;
their display strings do not replace the signature. [1]
MemberInfo.MetadataToken identifies an element only together with its Module.
The same integer in another module need not denote the same member. [2]

Inference: rebuilds, rewritten metadata or a different module invalidate a bare
token-based match. Keep the actual artifact, not only its assembly display name.
A call-site reference must be resolved in its containing module; do not assume
every four-byte IL operand is a MethodDef token. Strings, branches, constants
and different operand kinds require the instruction's own decoding contract.

## Heap indexes and coded indexes are not ordinary IL tokens

In ECMA-335 II.22/II.24.2.6, metadata columns can hold simple table indexes,
heap indexes or coded indexes combining row and table-selection tag bits.
The #~ stream records present tables and their row counts. HeapSizes controls
string/GUID/blob index widths; simple table indexes widen from two to four
bytes at 65536 rows. [3]

Inference: a parser that assumes every column is a four-byte token loses row
boundaries. Coded-index tag counts affect their width threshold independently.
Use the exact column schema and checked extents; do not reinterpret a heap
offset or coded index with the high-byte/low-24-bit token split. Unexpected
streams or malformed rows are unsupported input until their format is established,
not permission to guess a fixed record size.

## Method headers define the IL extent, not just an entry address

ECMA-335 II.25.4 tiny headers have low bits 2 and a six-bit body length above
them; they permit no locals, exception-handling (EH) sections or other extra
sections and at most eight stack items.
Fat headers have low bits 3, a header size in four-byte units, MaxStack, CodeSize
and LocalVarSigTok. Extra method sections begin at the next four-byte boundary
after the IL body. [3]

Constructed tiny header 0x1A describes six body bytes after one header byte.
Do not include the header or alignment padding in IL offsets. A metadata RVA
needs PE mapping before reading that header. Bounds must cover header, code
and each extra section separately; MaxStack is an evaluation-stack item count,
not a native stack allocation size. A method declaration does not guarantee
that it has a recoverable ordinary IL body.

## Call and callvirt do not directly encode native vtable layout

IL call resolves the method named by its descriptor; it can invoke a virtual
method nonvirtually, such as a specified base implementation. Instance calls
carry the instance before explicit arguments; the signature's instance marker
is not an extra user parameter. [4]
Unprefixed callvirt consumes an object reference and arguments, uses runtime
dispatch for virtual methods and throws for a null receiver. It can also call
non-virtual instance methods. [5]

Inference: callvirt alone does not prove an overridable method or a native
vtable access, and call alone does not prove a static method. Recover signature,
receiver and metadata flags before constructing the call graph. JIT inlining
or devirtualization can change emitted instructions without changing IL's
required observable semantics.

## Constrained callvirt depends on the actual receiver type

For the classic constrained. T / callvirt pattern, the receiver is a managed
pointer to T. With reference T it is dereferenced to obtain the object; with
a value T implementing the method, the pointer can be passed directly. The
documented fallback for unoverridden Object/ValueType/Enum methods boxes the
value. [6] This section describes that instance-call pattern, not every newer
runtime extension involving constrained static interface calls.

Inference: constrained. does not invariably box or invariably avoid boxing.
Resolve the closed type and actual method implementation. A decompiler's
temporary copy may hide whether a value-type mutation reaches original storage;
follow the managed address and stores rather than assigning reference-type
semantics to every this argument.

## Generic call resolution needs its enclosing context

Module.ResolveMethod accepts generic type and method argument arrays describing
the context in which the token occurs. A MethodSpec using var/mvar can fail
resolution if those arguments are missing. Type parameters and method parameters
are distinct substitutions. [7]

Inference: a failed context-free resolution is not evidence of a corrupt call
or an absent method. Preserve the declaring generic type, generic method and
instantiation; follow the resolved signature into argument/return analysis.
A generic definition's token is not sufficient to identify every closed
operation, and native addresses need their own code-version evidence.

## Signed branch displacements and switch bases

IL br.s uses a signed one-byte displacement from the following instruction.
Targets must land at the first prefix if an instruction has prefixes. [8]
Constructed bytes 2B FE at IL offset 0x10 branch to 0x10: next offset 0x12
plus -2, not 0x110 and not 0x0E.

IL switch contains a uint32 target count followed by signed int32 displacements;
all are relative to the instruction after the entire table. The selector is
compared unsigned with the count; out-of-range values fall through. [9]
Constructed switch at 0x20 with two targets has next offset 0x2D; offsets
-13 and +4 target 0x20 and 0x31. Count/table bounds and target instruction
boundaries must be checked before treating bytes as a valid control-flow graph.

## Exception regions add edges absent from ordinary branches

GetMethodBody exposes IL, locals and exception clauses. Catch, filter, finally
and fault clauses must be interpreted by their kind; not every clause supplies
a meaningful catch type. Trimming can change IL, branches and locals. [10]
IL leave empties the evaluation stack and runs applicable surrounding finally
handlers while exiting protected regions; it is not interchangeable with br.
It cannot be used to exit a finally handler. [11]

Inference: reconstruct protected ranges and cleanup edges before declaring
a release skipped or a second release reachable. Normal leave does not prove
that every abnormal termination runs cleanup. A handler's mere presence does
not prove it protects the security-sensitive operation or that cleanup succeeds.

## Conversion opcode determines width and overflow behavior

For integer narrowing, conv.i4 discards high bits rather than raising an
overflow exception. [12] conv.ovf.i4.un instead interprets the source as unsigned,
targets signed int32 and throws OverflowException when not representable; .un
does not make the destination unsigned. [13]

Constructed source 0xFFFFFFFF as a 32-bit unsigned value cannot fit signed
int32 under conv.ovf.i4.un. An unchecked integer reduction to 32 bits retains
those bits. Preserve original width, opcode and subsequent signed/unsigned
comparison; a source-language checked region reconstructed by a decompiler is
not evidence that every IL arithmetic or conversion instruction checks overflow.


## Sources: metadata and dispatch

1. [Metadata and self-describing components](https://learn.microsoft.com/en-us/dotnet/standard/metadata-and-self-describing-components): tables/heaps and MethodDef token example.
2. [MemberInfo.MetadataToken](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.memberinfo.metadatatoken?view=net-10.0): module-relative identity.
3. [ECMA-335 sixth edition](https://ecma-international.org/wp-content/uploads/ECMA-335_6th_edition_june_2012.pdf): II.22, II.24.2.6 (printed pp. 209, 273-274), II.25.4 (pp. 284-287). Selected rules paraphrased, not a copied specification.
4. [OpCodes.Call](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.call?view=net-10.0).
5. [OpCodes.Callvirt](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.callvirt?view=net-10.0).
6. [OpCodes.Constrained](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.constrained?view=net-10.0): classic instance-call cases.

## Sources: generic context and control flow

7. [Module.ResolveMethod](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.module.resolvemethod?view=net-10.0): context arrays and missing substitutions.
8. [OpCodes.Br_S](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.br_s?view=net-10.0).
9. [OpCodes.Switch](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.switch?view=net-10.0).
10. [MethodBase.GetMethodBody](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.methodbase.getmethodbody?view=net-10.0): method bodies and EH-clause example.
11. [OpCodes.Leave](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.leave?view=net-10.0).
12. [OpCodes.Conv_I4](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.conv_i4?view=net-10.0): integer narrowing only; floating-point conversion needs separate analysis.
13. [OpCodes.Conv_Ovf_I4_Un](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.opcodes.conv_ovf_i4_un?view=net-10.0).
14. [Module.ModuleVersionId](https://learn.microsoft.com/en-us/dotnet/api/system.reflection.module.moduleversionid?view=net-10.0): module-version GUID in metadata, distinct from artifact authentication.
