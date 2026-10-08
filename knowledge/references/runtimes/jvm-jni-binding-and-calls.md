---
id: reference-jvm-jni-binding-and-calls
title: JVM JNI native binding, call representations and exception boundaries
kind: reference
topics: [jvm, java, jni, native-binding, callbacks, exceptions, thread-attachment]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# JNI binding and calls

## Scope and investigation routes

JNI (Java Native Interface) connects JVM-managed code and native implementations
or callers. Reviewed 2026-10-02 against the JDK 25 JNI specification. These are interface
contracts, not observations of a target JVM or claims about every historical
runtime. Android ART integration and Java's Foreign Function and Memory API
require separate contracts; neither is inferred from a JNI-looking import.
Bytecode/loader identity: reference-jvm-class-file-evidence and
reference-jvm-loading-and-reflection. Ownership: reference-jvm-jni-memory-and-lifetimes.
Workflow: playbook-re-jni-boundary.

## Bind the Java declaration to the actual native address

JNI dynamic lookup tries short `Java_<escaped-class>_<escaped-method>` before the
long name formed by appending `__<escaped-parameter-descriptor>`; the suffix omits
parentheses and return type. [1]
RegisterNatives supplies name, complete signature and function pointer for a
particular class. [3]

Investigation: retain declaring Class/loader, static versus instance, descriptor,
binding mechanism, loaded module hash and target address/RVA. Absence of Java_
exports does not exclude registered natives. An unused export or registration
table in a file does not prove which target was installed successfully. Follow
the executed registration path and return status, including later rebinding.
Do not join registrations solely by class-name spelling across defining loaders.

## Export spelling is not a C prototype

JNI name escaping maps slash to underscore, underscore to _1, semicolon to _2,
and left bracket to _3; other units outside ASCII letters/digits use _0 plus four
lowercase hexadecimal digits. Native entry arguments begin with JNIEnv*, then
jobject for an instance or jclass for a static method. [1]

Investigation: separate export decoding from native ABI reconstruction. Keep
the return descriptor even though the overload suffix omits it. Confirm target
pointer width, floating-point argument placement and platform calling convention;
do not apply a 32-bit Windows stack-cleanup rule to a 64-bit target. A decompiler
label named this can actually be the environment or class reference. JNI table
calls require identifying the table and slot, not matching an arbitrary offset
to a similarly shaped virtual dispatch table.

## JNI integers and argument arrays have explicit representations

jboolean is unsigned 8-bit, jbyte signed 8-bit, jchar unsigned 16-bit, jint
signed 32-bit and jlong signed 64-bit. jsize is jint, not size_t. jvalue is a
union with typed members, including i, j, d and l. JNI references are opaque;
jmethodID and jfieldID are distinct opaque ID types. [2]

Investigation: preserve signedness before widening a count or converting a
negative sentinel into a native allocation size. Do not substitute C long for
jlong without checking that platform's width. For a constructed (IJ[BLpkg/X;)V
call, four Java parameters require four jvalue entries; the long occupies one
entry, not two entries corresponding to JVM local-variable slots. The implicit
receiver is passed separately. A typed A-call array, V-call va_list and variadic
call are different representations; inspect the actual selected JNI entry.

## Member lookup and callbacks can execute more than expected

GetMethodID initializes an uninitialized class. Ordinary `Call<Type>Method` uses
receiver dispatch; `CallNonvirtual<Type>Method` selects through its supplied class.
AllocObject skips constructors. [3]

Investigation: recover lookup class, member descriptor, static/instance family,
argument representation and return family together. A method ID found on a
base type is not alone evidence of the body invoked by a virtual callback.
Include initializer/callback reentrancy before a native lock or ownership change
is considered complete. If construction establishes an invariant, distinguish
AllocObject plus field assignment from NewObject and the selected constructor.
Neither allocation success nor a discovered member proves application authority.

## JNIEnv belongs to a thread; attachment has ownership

JNIEnv cannot be transferred between threads. [1] GetEnv distinguishes an
unattached thread (JNI_EDETACHED) from an unsupported version (JNI_EVERSION).
Attaching an already attached thread returns its existing environment; attaching
as daemon does not change an existing attachment's daemon status. Detachment
cannot occur with Java frames on the stack. [4]

Investigation: record the callback's actual native thread and acquisition of its
own environment. Distinguish JavaVM* sharing from JNIEnv* sharing. Track whether
this component created the attachment before assigning cleanup responsibility;
unconditionally detaching a caller-owned attachment is not a general cleanup
rule. A worker that outlives its initiating JNI call needs its own reference and
attachment strategy. Do not infer safe shutdown from successful task submission.

## FindClass does not simply use the thread-context loader

FindClass normally uses the native method's declaring loader; Invocation API
calls without a current native method use the system loader. JNI_OnLoad uses
the loading class's loader. [3] A newly attached native thread's context class
loader is initially the bootstrap loader. [4]

Investigation: distinguish these three loader concepts explicitly. A lookup
working during JNI_OnLoad but failing on a worker can be a context difference,
not a missing installation or memory fault. Preserve the name representation,
actual Class/loader and failure stage. Do not change a live application's loader
configuration merely to make an inspection succeed. Unknown class lookup may
execute loader/initializer code; it is not a passive symbol search.

## Pending Java exceptions do not automatically stop native execution

A Java exception remains pending until native code returns to propagate it or
handles/clears it. [1] ExceptionDescribe also clears the exception. Some JNI
NULL failures need not set an exception. [3]

The pending-exception permitted set is ExceptionOccurred/Describe/Clear/Check,
ReleaseStringChars/UTFChars/Critical, `Release<Type>ArrayElements`,
ReleasePrimitiveArrayCritical, DeleteLocalRef/GlobalRef/WeakGlobalRef,
MonitorExit, PushLocalFrame, PopLocalFrame and DetachCurrentThread. Slash-grouped
names expand to their corresponding JNI names, e.g. DeleteGlobalRef. [1]

Investigation: after a throwing JNI operation, preserve both its return value
and exception state before following the next native instruction. A default
primitive value or void return is not proof of success. A trace/debug helper
that describes an exception can change the subsequent path; observation is not
necessarily neutral. Clearing a failure does not undo earlier writes, callbacks
or native resource acquisition. Verify each cleanup operation's eligibility;
the pending-exception allowance does not waive critical-region restrictions.
Do not assume Java exceptions perform C++ stack unwinding through native code.

## JNI entry is not a general argument-validation barrier

Illegal JNI pointer/type arguments can corrupt state or crash the VM; ordinary
JNI does not promise to diagnose programmer contract violations safely. [1]

Investigation: preserve both sides of a native call's preconditions. A Java
verifier-accepted method may still pass an invalid native extent, stale ID or
incorrectly typed handle through native code. Conversely, a diagnostic VM mode
rejecting a misuse is not proof the production VM checks the same condition.
Locate actual checks before the first use; distinguish a managed exception from
a native process fault. Check pointer return status even when no exception is
pending, and do not inspect an invalid pointer merely to classify the failure.

## Library hooks and interface versions are separate evidence

An absent dynamic-library JNI_OnLoad implies JNI 1.1; a present hook reports its
required JNI version. JNI_OnUnload can run in an unknown context during loader
collection. [4]

Investigation: distinguish the JNI interface version from Java language level,
class-file major version and architecture. Record actual runtime/module native
access configuration, load outcome and registration outcome separately; a
permission setting alone proves no native target ran. Do not invoke unload hooks
or destroy the application's VM as diagnostic cleanup. Review hook callbacks
and teardown against their actual context, not a presumed application thread.

## Primary sources and inspected sections

1. [JDK 25 JNI design](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/design.html): interface/thread model, native name resolution, entry arguments and pending exceptions.
2. [JNI types](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/types.html): primitive widths, reference/ID types, jvalue and signatures.
3. [JNI functions](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/functions.html): RegisterNatives, GetMethodID, call families, AllocObject, FindClass and ExceptionDescribe.
4. [JNI invocation](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/invocation.html): GetEnv, attachment/detachment and library lifecycle hooks.
