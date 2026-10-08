---
id: reference-windows-rpc-context-callback-lifetime
title: Windows RPC context handles, rundown and callback lifetime
kind: reference
topics: [windows, rpc, context-handles, callbacks, lifetime, concurrency]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows RPC context handles, rundown and callback lifetime

## Context handles are opaque client references to server state

Scope: Microsoft RPC/MIDL, reviewed 2026-10-02. A `[context_handle]` retains
server-side state across calls; its associated data is not transmitted to the
client. It is not a transferred Win32 kernel handle, a serialized structure or
a client-dereferenceable server address. Record server instance, context type,
creating operation and application ownership separately.

To close context, the server returns NULL through the `[in,out]` context argument
when it no longer maintains that state. An `[in]`-only context argument cannot
reflect that change to the client. A non-NULL context used with another binding
must refer to the same server address space. Do not infer safe reuse after close
or reconnect from a saved numeric value; establish the target runtime and
application behavior.
[context_handle](https://learn.microsoft.com/en-us/windows/win32/midl/context-handle).

## Rundown is a cleanup path, not a guaranteed immediate disconnect destructor

Windows RPC can invoke a server context rundown routine after communication
breaks, for each context the client had opened. A context-handle typedef requires
its corresponding rundown routine; putting the attribute directly on a parameter
does not cause that typedef-based routine to run. Runtime context bookkeeping
cleanup is not the same as releasing every application resource.

Investigate normal close, failed creation and rundown separately. Check retained
files, allocations, registrations and application references, including partial
initialization. Do not infer immediate cleanup at a particular disconnect instant
or after every call. A missing ordinary close call is not alone a proven leak
if another evidenced ownership path releases the resource; a present rundown
symbol is not proof that the active context type reaches it.
[Server context rundown](https://learn.microsoft.com/en-us/windows/win32/rpc/server-context-run-down-routine).

## Context serialization is scoped, not a process-wide application lock

Microsoft RPC defaults to serializing calls using the same context-handle
instance at the server. Windows XP introduced per-method exclusive/shared
context access through serialized/nonserialized declarations. Historical
`RpcSsDontSerializeContext` permits concurrent dispatch, with rundown still
waiting for outstanding client requests; inspect actual mode and target version.
[Multithreaded contexts](https://learn.microsoft.com/en-us/windows/win32/rpc/multithreaded-clients-and-context-handles).

Inference: serialization for one context instance does not prove protection of
global state shared by other contexts, worker threads or other interfaces.
Build a conflict set naming the state and every accessor before declaring a
race or dismissing one. A nonserialized reader may overlap other readers; a
routine called a reader can still mutate a cache or reference count. Establish
the actual conflicting accesses and lifetime interval rather than deriving a
race solely from a MIDL attribute.

## An IDL callback is not an interface security callback

MIDL `[callback]` denotes a client-side operation invoked at the server's request
within the original RPC call context; callbacks can nest. This is distinct from
the server's interface-admission security callback. Static callbacks use the
original binding and cannot take binding-handle parameters; context handles
cannot be used with callbacks. These rules do not describe every COM callback
object or an application's separate reverse connection.
[MIDL callback](https://learn.microsoft.com/en-us/windows/win32/midl/callback),
[context restrictions](https://learn.microsoft.com/en-us/windows/win32/midl/context-handle).

Investigation implication: classify the callback mechanism before assigning its
identity, thread or cancellation behavior. Trace the outward call and any
nested entry while invariants are temporarily broken. Holding a lock or having
only one apparent request thread is not proof against reentrancy. See
`reference-concurrency-locks-waits-reentrancy` for feasible wait and reentry
evidence; do not assume that merely declaring a callback establishes a deadlock.

## Retained work needs lifetime evidence beyond the RPC return

For a Windows RPC manager that queues work, distinguish call completion,
application completion, explicit context close and rundown. Investigative
requirements: identify whether queued code copies data or retains pointers,
which reference keeps context alive, and which event permits final release.
Do not equate opaque context validity with authorization for a new operation;
the application must still enforce its resource and state policy.

Constructed candidate: a manager saves a pointer into per-call input and returns;
a later worker uses it. This is not automatically a use-after-free: establish
the pointer's allocation owner, actual release and subsequent use. Similarly,
two cleanup functions are not a double free unless a feasible path applies both
to the same owned resource. Use `reference-windows-ndr-marshaling-contracts` for
referent classes and `reference-concurrency-refcounts-reuse` for retained
references. Use the RpcAsyncCancelCall section for that API's specific rules;
do not generalize them to every cancellation mechanism.

## Strict interface association is not context type or resource authorization

MIDL strict_context_handle restricts accepted contexts to those created by the
same interface; an interface without that attribute cannot accept contexts
created by a strict interface. This is not a distinct type ID for every context
typedef or an authorization decision about the resource inside it.
[strict_context_handle](https://learn.microsoft.com/en-us/windows/win32/midl/strict-context-handle).

type_strict_context_handle is a functional superset: MIDL assigns unique type
IDs, unlike strict_context_handle's type ID zero. It requires `/target NT60` or
later and cannot be combined with strict_context_handle. Without type-strict
enforcement, a recovered typedef name alone does not prove runtime context-type
checking. Check the target's generated metadata and manager validation before
claiming either type confusion or guaranteed type separation. Even a matching
type does not authorize every caller, operation or state transition.
[type_strict_context_handle](https://learn.microsoft.com/en-us/windows/win32/midl/type-strict-context-handle).

## Serialized and nonserialized context methods can form a mixed access model

For Windows XP and later RPC contexts, context_handle_serialize and
context_handle_noserialize support exclusive/shared access to the same context.
The serialization attribute can override a RpcSsDontSerializeContext default.
Creation is implicitly serialized; methods modifying or destroying context
should be classified separately from read-only shared accesses. This is not a
global application lock or proof that the implementation is actually read-only.
[Serialized contexts](https://learn.microsoft.com/en-us/windows/win32/midl/context-handle-serialize),
[Nonserialized contexts](https://learn.microsoft.com/en-us/windows/win32/midl/context-handle-noserialize).

Investigation implication: do not interpret a nonserialized reader as necessarily
overlapping an exclusive writer. Recover both methods' access modes, runtime
version and the particular context instance. Conversely, reader-reader overlap
can expose hidden writes to caches or counters, and workers outside the RPC
context protocol may still conflict. A race claim needs a feasible overlap and
conflicting accesses, not just the word noserialize in recovered metadata.

## Static IDL callbacks have transport and cancellation restrictions

MIDL `[callback]` uses the original call context and can nest. It is supported
for connection-oriented and local RPC, not connectionless RPC. Microsoft's
contract prohibits RpcCancelThread for a call that might dispatch a static
callback, unless cancellation is guaranteed before any callback is issued or
the call never generates one. This is not a blanket rule for COM callback
objects, interface-admission security callbacks or arbitrary application IPC.
[MIDL callback restrictions](https://learn.microsoft.com/en-us/windows/win32/midl/callback).

Investigation implication: pair the concrete callback mechanism with the actual
cancel API and request state. A generic assumption that cancellation interrupts
all nested work can invalidate both lifetime and deadlock analysis. Retain which
side is waiting and what can reenter while the original call remains active.

## RpcAsyncCancelCall requests cancellation; it does not prove server rollback

For Windows asynchronous RPC, a client may cancel only after the issuing thread's
asynchronous invocation has returned successfully; a synchronous issue failure
must not be asynchronously canceled. RpcAsyncCancelCall returning RPC_S_OK means
the request was processed, not that application side effects were undone.

With fAbort=TRUE the client does not await a server response; this does not prove
server execution stopped. With FALSE the client waits for server completion,
without a built-in timeout. Server cancellation polling and timing can permit
normal completion. The client must still await original-call completion and
use RpcAsyncCompleteCall to obtain completed/failed/canceled status. Do not free
call-associated state solely because the cancel request succeeded. Application
resource release and transactional rollback need their own evidence.
[RpcAsyncCancelCall](https://learn.microsoft.com/en-us/windows/win32/api/rpcasync/nf-rpcasync-rpcasynccancelcall).
