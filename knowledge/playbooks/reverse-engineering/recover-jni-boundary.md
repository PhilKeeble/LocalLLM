---
id: playbook-re-jni-boundary
title: Recover and validate a JVM JNI binding, callback and memory boundary
kind: playbook
topics: [reverse-engineering, jvm, jni, interop, callbacks, ownership, validation]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Recover a JNI boundary

## Define the boundary and preserve identities

Reviewed 2026-10-02. Start with preserved class/JAR and native-library hashes,
runtime vendor/build, architecture, launch/module configuration, class loaders
and relevant inputs. Determine whether this is JNI, another foreign-call API
or an Android-specific integration; do not merge their conventions.

State the invariant: exact native extent, allowed operation, callback ownership,
valid construction state or exception-to-rejection behavior. Trace a specific
entry to the native sink rather than treating a native declaration as a defect.
Prefer static inspection; do not load unknown libraries, attach instrumentation,
enable native access or invoke lifecycle hooks on a shared target to aid discovery.

## Recover the installed binding and both call signatures

Join declaring Class/loader and full descriptor to dynamic export resolution or
executed RegisterNatives records. Preserve the selected pointer, module/RVA,
return status and registration time. Distinguish a candidate table from successful
binding. Follow indirect wrappers and rebinding before naming the executed body.

Reconstruct environment, instance/class receiver and Java parameters under the
actual machine ABI. Recover native widths/signedness, return representation and
callback call family. For A, V and variadic calls, do not reuse one argument-layout
model for all three. Cross-check a long parameter against jvalue entries rather
than bytecode local slots. Facts: reference-jvm-jni-binding-and-calls.

## Trace JNI callback lifetime through cancellation and completion

For each jobject/ID/pointer, record acquisition API, owning thread or frame,
strong/weak/local/global category, extent, release operation and final use.
Build this resource timeline for every retained JNI callback value.
Separate a Java reference's lifetime from the native allocation it wraps and
from a temporary string/array access lease. For copied arrays distinguish
intermediate commit from final release; for direct arrays do not infer rollback.

For asynchronous work, follow submission, callback registration, cancellation,
unregistration and completion/drain. Show that no later user can access released
state; cancellation request alone is not a final-use event. If a class/loader can
unload, include cached member IDs in the timeline. Facts:
reference-jvm-jni-memory-and-lifetimes.

## Preserve units and error channels across the transition

Annotate every length as bytes, UTF-16 units, array elements or buffer-view
elements. Track signed sentinels and checked conversions before multiplication,
allocation and memory access. Establish the source range and independent native
destination range. For strings, prove explicit extent or termination at the
consumer; do not replace JNI modified UTF-8 with ordinary UTF-8 arithmetic.

After a possibly throwing JNI call, record the native result and pending Java
exception independently. Follow propagation, clearing, logging, cleanup and
continued native side effects. Check whether observation helpers change the
exception. A caught Java error does not prove rollback of a preceding native
write, and a pending exception does not prove native execution already stopped.

## Trace callback thread, loader and reentrancy context

Identify the actual callback thread, its own JNIEnv and attachment owner. Keep
GetEnv's detached and unsupported-version outcomes distinct. Do not detach an
attachment merely because a helper successfully requested attachment again.
Resolve FindClass under the specific native-entry or invocation context instead
of assuming it follows the thread-context loader.

Trace initializer and virtual callback bodies before treating an operation as
non-reentrant. Include native locks, critical pointer leases, Java callbacks and
teardown in the same ordering model. A helper that looks like logging may call
Java or block. Native/global reference reachability supplies no lock discipline.

## Evidence sufficient to accept or reject the boundary hypothesis

Retain the actual runtime, native ABI, reference category and storage owner for
the path under review. Distinguish implementation-permitted alternatives such as
copied versus directly accessed arrays, and immediate versus deferred completion.
Correctness must cover the feasible alternatives, not just one observed run.
For text, preserve length units and the consumer's handling of embedded NUL and
supplementary characters. For failure, preserve native return and Java exception
state independently. Label static deductions and runtime observations separately;
neither an arithmetic model nor a candidate binding table proves execution.

A supported finding connects controlled input, actual binding, feasible callback
or access path, resource/representation mismatch and violated invariant.
Counterevidence includes a nonexecuted registration, an effective pre-copy range
check, a retained owner covering all users, or rejection before the suspected
side effect. Report unresolved runtime/ABI/lifetime edges explicitly. A single
no-copy or nonmoving-GC observation is not proof all executions are safe.

For malware behavior recovery, trace the installed native implementation and
callback arguments into their actual operations. Loading a JNI library or retaining
a global reference is ordinary functionality, not evidence of malicious intent.
A vulnerable native boundary and deliberate harmful use are separate conclusions.

## Sources and factual homes

- [JDK 25 JNI specification](https://docs.oracle.com/en/java/javase/25/docs/specs/jni/index.html): versioned interface contracts, not target observations.
- reference-jvm-jni-binding-and-calls: binding, representation, thread, loader and exception facts.
- reference-jvm-jni-memory-and-lifetimes: handles, strings, array modes, critical regions and direct-memory ownership.
- playbook-re-jvm-method-and-dispatch: managed artifact, bytecode and dispatch recovery before the boundary.
