---
id: reference-javascript-native-lifetimes
title: Embedded JavaScript handle lifetime, native buffers, coercion and exception boundaries
kind: reference
topics: [javascript, v8, quickjs, duktape, native-bindings, lifetime, reentrancy]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64]
---
# Embedded JavaScript native-lifetime evidence

## V8 local handles expire with their handle scope

V8 Local handles belong to a HandleScope; leaving that scope removes those handles.
Persistent handles support longer lifetimes, while weak persistent handles do
not provide ordinary strong retention. EscapableHandleScope transfers a local
result into an enclosing scope. [1]

A native field containing copied handle bits is not proof of a retained callback.
Recover creation, scope exit, persistent ownership and teardown. Also distinguish
the lifetime of a JavaScript wrapper from any external native object it addresses.
A surviving wrapper does not establish that a manually freed native resource is
still valid.

## QuickJS JSValue ownership is explicit, not a V8 handle-scope model

QuickJS uses JS_DupValue and JS_FreeValue to manage value references. Native
callback inputs are generally borrowed constant values; returned values are live
owned values. JS_EXCEPTION is an exception indicator, with the exception object
retrieved from the context using JS_GetException. [2]

Follow the specific API's ownership rule, including setters that consume values;
do not apply the callback-argument rule to every function. A copied JSValue is
not automatically an acquired reference. Check exception results before decoding
them as ordinary values, and account for stored callbacks on all teardown paths.

## QuickJS finalizers and GC marking serve separate purposes

A QuickJS native class can attach opaque C data, release C resources in a
finalizer and expose held JavaScript references through gc_mark. Executing
JavaScript from the finalizer is invalid. [2]

Identify whether a native field owns a JSValue, borrows it or merely encodes an
external address. Missing visibility of an owned edge and duplicate resource
cleanup are different hypotheses. A class ID helps identify the wrapper contract;
it does not validate the lifetime or authority of an arbitrary native pointer.

## Duktape heapptr is a borrowed identity, not a GC root

duk_get_heapptr returns an opaque borrowed heap pointer. Using it after collection
is unsafe; a strong reachable backing value, such as a stash entry, preserves
lifetime. Duktape's documented finalizer-based weak scheme has additional rules
and can fail under allocation pressure. [3]

Do not infer retention from a native map of raw pointers. Follow a real reachable
value throughout the callback interval, or establish the exact weak-reference
protocol and its failure limitations. For malware analysis, this map may explain
callback identity without making the pointer itself executable code.

## Duktape buffer data pointers can change independently of wrapper lifetime

duk_get_buffer_data reports a byte span. Dynamic or external-buffer reconfiguration
can invalidate a previously obtained pointer. An external buffer's backing storage
is host-managed, not automatically freed or kept alive by Duktape. [3]

Reconstruct the view offset and byte length used by the native consumer. Inspect
resize/reconfiguration and host-free paths between validation and access. A live
buffer object alone does not prove a stable backing address. Track the original
allocation and the actual accessible slice instead of copying an apparent typed
array element count into a byte-oriented API.

## JavaScript object coercion can execute script during native validation

ECMAScript ToPrimitive can call Symbol.toPrimitive or ordinary valueOf/toString
methods; conversion can also throw. These are specification operations, not
necessarily named functions in the binary. [4]

A native binding that converts an object to a number or string may re-enter
script. After that callback, previously checked state or native storage may have
changed. Distinguish a strict type test from coercion and locate any pending
exception check. Do not conclude all primitive conversions call script; the
object conversion path is the relevant condition.

## Primary sources and scope

Reviewed 2026-10-02. Engine APIs are separate contracts; do not combine V8 handles,
QuickJS references and Duktape stack/heap pointers into one ownership model.
Exact engine configuration and callable wrapper code remain target evidence.
Capability and loader limits: `reference-script-host-isolation`.

1. [V8 embedding guide](https://v8.dev/docs/embed): local/persistent handles, scopes and native wrappers; conceptual API examples, not a fixed current binary layout.
2. [QuickJS manual](https://bellard.org/quickjs/quickjs.html): C API JSValue ownership, exceptions and native classes.
3. [Duktape API reference](https://duktape.org/api.html): duk_get_heapptr/duk_push_heapptr, stashes and buffer-data/external-buffer contracts (2.x).
4. [ECMAScript abstract operations](https://tc39.es/ecma262/multipage/abstract-operations.html#sec-toprimitive): ToPrimitive and OrdinaryToPrimitive, living specification.
