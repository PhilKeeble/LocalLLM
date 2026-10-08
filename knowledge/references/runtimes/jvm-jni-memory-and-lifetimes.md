---
id: reference-jvm-jni-memory-and-lifetimes
title: JVM JNI reference, string, array and direct-memory lifetime contracts
kind: reference
topics: [jvm, java, jni, references, ownership, strings, arrays, direct-buffers]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# JNI memory and lifetimes

## Scope and evidence

Reviewed 2026-10-02 against the JDK 25 JNI specification. Documented contracts
and labeled investigation deductions are not target observations. A Java object
reference, acquired element/string pointer and application-owned native address
are different resources. Binding/callback/thread context:
reference-jvm-jni-binding-and-calls. Workflow: playbook-re-jni-boundary.
Modified-UTF-8 encoding has its shared factual home in
reference-jvm-class-file-evidence; this document concerns its native boundary.

## Local and global references are handles, not object-address pins

A local JNI (Java Native Interface) reference is thread/call-scoped; a strong
global reference survives until explicitly deleted. These references retain
object reachability for the garbage collector (GC), not an immobile object
address. Weak global references have the separate acquisition rules below. Method/field
IDs do not keep their class alive and become invalid after class unloading. [1]

Investigation: storing a local handle in a C global variable does not promote
it. For a retained callback, establish a live strong reference, the actual thread's
environment, and release only after all users are quiescent. A global handle
alone neither serializes concurrent state changes nor proves associated native
memory remains allocated. Cache IDs with an explicit class-lifetime strategy;
do not delete an ID as if it were a jobject. Review the cost of keeping loaders
alive as well as premature release.

## Weak references require acquisition, not a check-then-use claim

NewLocalRef can promote a live weak reference; check for NULL before use.
IsSameObject tests object identity. PopLocalFrame can preserve its result as
a reference in the preceding frame. [2]

Investigation: a weak-handle NULL comparison followed by separate use leaves
a collection window. A successfully acquired strong reference must cover the
whole operation and then be released appropriately. NULL is not uniquely proof
that the referent was collected; retain applicable error state. Raw handle-bit
equality is not a sound replacement for JNI object identity. In native loops,
bound accumulated local references; after popping a frame use the returned
reference, not an old handle from that frame. A long-running attached worker
must not assume each internal work item constitutes a returning JNI native call.

## String units and termination must be proved independently

JDK 25 does not promise NUL termination for GetStringChars, GetStringUTFChars,
GetStringRegion, GetStringUTFRegion or GetStringCritical buffers. GetStringChars
uses jchar UTF-16 units; GetStringUTFChars uses modified-UTF-8 bytes.
GetStringUTFLengthAsLong, added in JDK 24, reports modified-UTF-8 byte length;
deprecated GetStringUTFLength can report only a representable prefix. [2]

Investigation: track UTF-16 units, modified-UTF-8 bytes and native buffer capacity
separately. Standard UTF-8 lengths are not interchangeable with JNI modified
UTF-8. Inspect the consumer's explicit length versus strlen-style scanning;
do not justify an unbounded scan from a pointer type alone. An implementation
observed to append zero does not expand the portable documented contract.
Match each acquired string pointer to its release and prevent retention beyond
that lease. Compiling against newer headers does not make a newer table entry
available on an older VM; record the supported interface before calling it.

## String-region capacity is a native allocation question

GetStringUTFRegion takes UTF-16 start/length but writes modified-UTF-8 bytes. [2]
The modified encoding needs at most three bytes per UTF-16 code unit. [3]

Constructed capacity reasoning: for a previously validated source range of n
UTF-16 units, checked 3*n+1 native bytes provide the maximum encoding plus a
spare terminator byte. This is an allocation bound, not the actual output count
or a claim that the API always writes a terminator. Check multiplication/addition
and destination representation before allocation. Use the actual produced
extent/established termination policy when passing the buffer onward.

Investigation: separately prove source-range validity and destination extent.
A valid Java string slice does not establish that an independently allocated
C buffer is large enough. Do not use native byte capacity as the Java unit count.
No large string or VM allocation was executed to validate this arithmetic.

## Array release modes are not transactional rollback

JNI array access may copy or pin and does not supply exclusive access. [1]
For a copied array, release mode 0 copies back/frees, JNI_COMMIT copies back/keeps
the copy, and JNI_ABORT frees without copying. Noncopy release ignores mode. [2]

Investigation: JNI_ABORT cannot undo writes already made through a direct array
pointer. After JNI_COMMIT of a copy, account for a later final release; do not
generalize copy retention to noncopy pointers. Record isCopy when available,
but ensure correctness for both permitted outcomes rather than depending on
one VM run. Follow native index/count arithmetic and concurrent Java accesses.
For region-copy operations, prove the destination native allocation separately
from the Java array range; a Java bounds check is not a C-buffer extent proof.

## Critical access restricts the entire intervening path

JNI critical access may still copy. Primitive critical access prohibits arbitrary
JNI calls and system calls that may wait for another Java thread; documented
nested primitive critical acquisitions are permitted. String critical access
prohibits arbitrary JNI calls and blocking. [2]

Investigation: keep the critical lease brief and inspect all intervening callees,
not just the immediate loop:
logging, allocation helpers, callbacks and locks can add prohibited work.
Determine whether a wait depends on Java progress and whether release occurs
on every path. Critical does not mean mutual exclusion, guaranteed zero-copy or
permission to retain a pointer asynchronously. Pending-exception cleanup rules
do not grant a general exemption from this region's restrictions.

## Direct-buffer reachability does not own the native allocation

NewDirectByteBuffer requires byte capacity in 0..Integer.MAX_VALUE despite its
jlong parameter. GetDirectBufferCapacity counts elements and can return -1. [2]

Investigation: distinguish a ByteBuffer from a typed view before converting
capacity to bytes; validate failure before casting to unsigned size_t. Establish
which address/range was wrapped, position/limit handling, native allocator,
owner and actual final-use event. A JNI global reference keeps a wrapper
reachable, not a separately freed native allocation valid. A close/dispose path,
pool reuse or asynchronous callback may end that allocation's lifetime first.
Neither directness nor successful wrapper creation proves a permitted write,
byte order, alignment or range appropriate for the native consumer. An alias
or slice must be reconciled with the same underlying owner's release timeline.

## Primary sources and inspected sections

1. [JDK 25 JNI design](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/design.html): references, arrays, member IDs and class unloading.
2. [JNI functions](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/functions.html): local/weak references, string operations and length versions, array releases, critical access and direct buffers.
3. [JNI types](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/types.html): modified UTF-8 code-unit representation.
