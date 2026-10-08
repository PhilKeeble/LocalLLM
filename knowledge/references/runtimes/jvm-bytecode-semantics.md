---
id: reference-jvm-bytecode-semantics
title: JVM bytecode control flow, arithmetic, dispatch and exception evidence
kind: reference
topics: [jvm, java, bytecode, control-flow, integer-overflow, dispatch, exceptions]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# JVM bytecode semantics

## Scope: abstract-machine behavior is not a native layout

Reviewed 2026-10-02 against Java SE 25. The Java Virtual Machine Specification
(JVMS) leaves object layout, garbage
collection and native-code optimization to implementations. [1]
Inference: x64 analysis does not turn a Java int into 64 bits or a reference
into a guaranteed uncompressed machine address. Record runtime/build/options
before interpreting a heap or JIT frame. This reference is not an ART opcode
guide. File coordinates: reference-jvm-class-file-evidence; runtime selection:
reference-jvm-loading-and-reflection.

## Local slots and operand values are not native stack offsets

The JVM's logical method frame has indexed local variables and an operand stack
used by bytecode instructions. A native compiler can implement these values
using registers or other storage; logical slot numbers are not physical offsets.

JVM long/double occupy two local slots; int/float/reference use one. Instance
local 0 carries this; static parameters begin at 0. Category-2 long/double
values contribute two units to operand-stack depth. [1]

Constructed instance descriptor (IJ[B)V: this is slot 0, int slot 1, long slots
2-3, byte-array reference slot 4. This is a logical frame mapping, not an ABI
layout. Inference: reconstruct types across each instruction and join; do not
interpret max_stack as a byte allocation size or infer physical stack addresses
by multiplying local indices by host pointer width.

## Branch offsets originate at the opcode, not the next instruction

For goto and ordinary conditional branches, signed 16-bit offsets are relative
to the branch opcode; goto_w uses a signed 32-bit offset. Targets must be
instruction starts within the same method. [2]

Constructed example: goto bytes A7 FF F8 at BCI 12 target BCI 4, not BCI 7.
Inference: decode boundaries before accepting any target; landing inside a
constant-pool operand is not a valid alternate block. Preserve conditional
fallthrough and exceptional edges, and distinguish signed comparisons from
reference equality. Bytecode coordinates cannot be substituted for native
branch displacements in a JIT disassembly.

## Switch alignment and wide modify instruction boundaries

tableswitch/lookupswitch padding aligns their first operand to a four-byte
boundary relative to method start. Their signed offsets use the switch opcode
as base. tableswitch has high-low+1 offsets; lookupswitch has nonnegative npairs
and ordered match/offset pairs. wide changes local-index encoding; wide iinc
also widens its signed increment. [2]

Constructed tableswitch at BCI 5 has two pad bytes and first operand at 8.
With low=2, high=3 its next instruction is BCI 28; offset -5 targets BCI 0.
Inference: bound counts against remaining Code bytes before allocation/iteration.
Do not align to the enclosing file offset, search operand bytes for opcodes, or
treat wide's embedded opcode as an independent instruction entry.

## Java arithmetic overflow differs from C/C++ undefined overflow

Java integer addition/multiplication retain low-order result bits on overflow.
Integer division by zero throws; minimum signed value divided by -1 returns
that minimum without overflow exception. Shift distances are masked to five
bits for int and six for long; >> sign-extends and >>> zero-fills. [3]

Inference: verify the actual operand widths before a check. Constructed int
0x40000001 * 4 yields 4, so widening that result afterward cannot recover
0x100000004. A positive result does not prove multiplication stayed in range.
This can corrupt counts or logic without a JVM memory-safety violation; a
native-memory consequence needs a separate JNI/unsafe path.

## Narrowing and checked library calls are different operations

Java integral narrowing retains low bits; floating-to-int/long conversion maps
NaN to zero and clamps out-of-range values, with further narrowing for smaller
integer destinations. [4] Math.addExact/multiplyExact and toIntExact instead
throw ArithmeticException on the documented overflow. [5]

Inference: identify the opcode or exact library overload, not merely a source
cast. Constructed (byte)255 is -1, whereas (char)-1 is 65535. A check before
conversion need not constrain the value afterward. Checked-call presence is
not enough if its exception is caught and a truncated/default value reaches
the consumer; follow the failure edge and subsequent use.

## Invocation opcodes constrain selection, not one universal call graph

invokestatic invokes a static method. invokevirtual selects with the receiver;
invokeinterface uses interface invocation rules. invokespecial covers instance
initialization and specified current/supertype calls, not ordinary virtual
selection. invokedynamic uses a dynamically linked call site. [2]

Inference: preserve caller constant-pool entry, full descriptor, resolved class
and actual receiver. A declared method name is not proof of the selected body;
a nonstatic call still needs its receiver even when decompiled syntax hides it.
Bootstrap/MethodHandle resolution has its own evidence in
reference-jvm-loading-and-reflection. A native method requires its real native
binding, not a guessed Java_ export or an absent Code attribute.

## Exception-table order and pre-throw effects remain observable

JVM handler search follows table order and chooses a matching covered handler;
unhandled exceptions unwind to the caller. Precise exceptions retain effects
of preceding instructions; this is not transactional rollback. [1]
Range endpoints and catch_type are defined in reference-jvm-class-file-evidence.

Inference: include the earliest applicable handler, rethrows and cleanup when
following a rejected operation. A prior field write, callback or native effect
can survive a later exception. Decompiled nested try blocks may conceal the
actual handler order. A catch that logs and returns a default is not proof that
the operation failed closed or that partial shared state is unusable.

## Sources

1. [JVMS 25 structure](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-2.html): 2.6, 2.7, 2.10; logical frames, implementation freedom and exceptions.
2. [JVMS 25 instructions](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-6.html): goto/conditionals, switches, wide and invocation operations.
3. [JLS 25 expressions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-15.html): 15.17-15.19; integer arithmetic/division and shifts.
4. [JLS 25 conversions](https://docs.oracle.com/javase/specs/jls/se25/html/jls-5.html#jls-5.1.3): integral and floating-point narrowing.
5. [Math exact operations](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Math.html): addExact, multiplyExact, toIntExact and exceptions.
