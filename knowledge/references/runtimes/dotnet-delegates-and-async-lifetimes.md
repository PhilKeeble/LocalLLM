---
id: reference-dotnet-delegates-async-lifetimes
title: .NET delegates, closures, async state and cancellation lifetimes
kind: reference
topics: [dotnet, delegates, closures, async, cancellation, callbacks, lifetime]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET delegates and async lifetimes

A delegate is a typed callable value whose invocation list identifies methods
and, where needed, target instances. A closure retains captured variables used
by a callable. Those references, the callable's execution, and any asynchronous
operation it starts can all have different lifetimes. [1,2]

## Scope and representation limits

Reviewed 2026-10-02. The C# language/API contracts below describe observable
behavior; compiler-generated field names, class/struct choices and internal
delegate layout are not stable binary ABIs. Classic Task await behavior is not
a blanket contract for every custom awaiter or runtime extension.
Metadata and method identity: reference-dotnet-metadata-il-evidence.
Native transition investigation: playbook-re-dotnet-native-boundaries.

## A delegate snapshot retains its invocation list

C# delegate instances have immutable invocation lists. Combination/removal
produces another delegate rather than editing the old instance. Invocation
processes list entries synchronously in order; an uncaught exception stops
remaining entries. With a return value, the final invoked entry supplies it. [1]

Inference: removing an event handler does not revoke a delegate snapshot already
copied by another thread. This is a possible stale-callback schedule, not proof
of a defect without the publisher's synchronization and object-lifetime contract.
An invocation list is not automatically parallel, and no exception handler is
implicitly inserted around each subscriber. Locate the actual snapshot and
dispatch, not only the event add/remove methods.

## Multicast task-returning delegates do not implicitly join all tasks

Constructed C# delegate combination: first Func<Task> returns unfinished task A;
second returns completed task B. Invoking the combined delegate returns B,
following the final-return rule, not Task.WhenAll(A,B). [1] Awaiting that returned
task alone therefore does not establish that A completed. An async method can
return its task before its asynchronous work finishes. [5]

Inference: distinguish invocation completion from asynchronous operation
completion. If a framework explicitly enumerates delegates and joins results,
that is a different path requiring its own evidence. An earlier operation's
failure or resource use may outlive the caller's apparent completion unless
its task is observed through another documented owner.

## Captured variables are shared state, not a frozen authorization snapshot

C# lambdas can capture outer variables and extend their lifetime; multiple
lambdas can observe modifications to a shared captured variable. A static lambda
cannot capture enclosing locals or instance state, although it can access static
members and constants. [2]

Constructed sequence: capture variable principal=A, queue a callback, then assign
principal=B before the callback reads it. The capture does not promise that the
callback uses A. Conversely, an explicit copy into separate immutable state has
a different trace. Recover the captured storage, aliasing and read time; a
compiler-generated closure object name is not evidence of an authorization flaw.
GC reachability keeps objects alive, not logically authorized or undisposed.

## Async state-machine metadata routes analysis beyond the stub

For compiler-generated async methods, AsyncStateMachineAttribute associates the
stub with its generated state-machine type. The original name can therefore
refer to a small method that starts the machine, not the whole operation.
Microsoft explicitly permits the emitted IL details to change. [3]
IAsyncStateMachine.MoveNext advances that machine. [4]

Inference: follow the mapped state-machine method, persisted values, awaiter
registration and resume branches. Do not classify generated state switches as
an application wire protocol without evidence. Recover which values are checked
before suspension and which are reloaded after it; names such as state or
builder are clues, not proof of a particular layout or completion state.

## Await can complete synchronously and does not block like Result

Awaiting an already completed operation continues without suspension. For an
incomplete operation, await can suspend the async method and return control to
its caller without blocking the evaluating thread. [5]
Task<TResult>.Result instead blocks until completion when accessed early. [6]

Inference: await does not guarantee a new thread, a context switch or an
interleaving window. Conversely, after an actual suspension, the earlier local
check need not still describe mutable shared state at use. Record actual awaiter
completion, scheduler/context and values. A deadlock claim needs a wait cycle,
not the presence of .Result alone.

## Async void and task-returning exceptions have different owners

An async void method cannot be awaited by its caller, and caller-side try/catch
around that invocation does not catch exceptions thrown by its async body.
Task/Task<T>-returning async methods store exceptions in the returned task;
awaiting that task propagates them. [6]

Inference: an async lambda converted to a void-returning delegate may be an
async-void boundary. Recover the selected delegate signature, not just the
lambda's source-like spelling. A non-async method returning Task can still
throw synchronously before returning it; do not extend async-body exception
rules to every API whose return type is Task. Trace actual exception ownership
and response/cleanup behavior instead of equating invocation return with success.

## ConfigureAwait false is not a thread or identity reset

For Task awaiting, ConfigureAwait(false) avoids capturing the original
SynchronizationContext/nondefault TaskScheduler for continuation scheduling.
It does not guarantee another thread: an already completed await can keep
executing synchronously. ExecutionContext is separate; normal AsyncLocal data
flow across await is not suppressed by ConfigureAwait(false). [7]

Inference: this flag is neither an authorization reset nor evidence that
request-scoped data was cleared. A UI/thread-affinity assumption needs the
actual continuation path; an identity-flow assumption needs the applicable
context/API contract. Custom awaiters or explicitly suppressed execution-context
flow require separate analysis. Do not equate logical async context with a
Windows impersonation token without establishing the token-flow mechanism.

## Cancellation notification is not operation completion

.NET CancellationToken cancellation is cooperative: listeners choose how to
observe and respond. Calling CancellationTokenSource.Cancel notifies listeners;
callbacks invoked by that Cancel path run synchronously. [8,11] Cancel() uses
the Cancel(false) exception policy, aggregating callback failures; Cancel(true)
can stop remaining callbacks on the first exception. A cancellation request is
not a join of every other concurrent cancellation/operation path. [11]
This callback rule does not mean all operations have finished. It must not be
generalized to a distinct CancelAsync protocol without checking that API.

Inference: retain request resources until their real terminal owner releases
them, not merely until IsCancellationRequested becomes true. A callback can
reenter code or wait for a lock held by the cancelling thread; prove the actual
schedule. Dispose, cancel request, task terminal state and native completion are
different events. A token ignored by a callee does not force that callee to stop.

## ValueTask consumption is not freely repeatable

The general ValueTask<T> consumer contract allows one consumption: await it or
convert once with AsTask. Repeated awaits, repeated AsTask, mixing consumption
methods or reading Result before completion are unsupported; the result is
undefined by that API contract. [9] This is not a claim that every task-backed
instance visibly fails on second use.

Inference: copying a ValueTask struct does not create a new underlying operation
or independent consumption right. If repeated observation is needed, retain
the single converted Task and follow that object's contract. Recover the actual
return type and backing operation before diagnosing repeat awaits as safe or
incorrect; Task and ValueTask are not interchangeable lifetime models.

## A native function pointer does not root its managed delegate

Marshal.GetFunctionPointerForDelegate requires the managed delegate to remain
rooted; the raw unmanaged pointer does not keep it alive. P/Invoke marshaling a
delegate keeps it alive during that call, not for arbitrary later native storage.
If native code retains it, the root must cover the full callback lifetime. [10]

Inference: GC.KeepAlive at the end of registration is insufficient for a callback
that may run after registration returns. Determine unregister/quiescence before
releasing the root, and distinguish rooting from pinning. Rooting the delegate
also does not prove its captured native handle remains valid or its ABI matches
the caller. Establish which root survives each possible invocation and what
excludes further callbacks after that root is released.


## Sources: delegate and async language contracts

1. [C# delegates, sections 21.5-21.6](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/delegates): immutable invocation lists, order, exceptions and final result.
2. [Lambda capture and scope](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions): shared variables and static lambdas.
3. [AsyncStateMachineAttribute](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.asyncstatemachineattribute?view=net-10.0): stub/type mapping and compiler-version caveat.
4. [IAsyncStateMachine.MoveNext](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.iasyncstatemachine.movenext?view=net-10.0).
5. [C# await operator](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/await): suspension versus already-completed path.
6. [Async return types](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-return-types): Task, Result and async void exceptions.

## Sources: scheduling, cancellation and native callbacks

7. [Microsoft ConfigureAwait FAQ](https://devblogs.microsoft.com/dotnet/configureawait-faq/): scheduling capture versus ExecutionContext/AsyncLocal.
8. [Cancellation in managed threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads): cooperative requests and synchronous callback caveats.
9. [ValueTask<T>](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1?view=net-10.0): consumer restrictions.
10. [Marshal.GetFunctionPointerForDelegate](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getfunctionpointerfordelegate?view=net-10.0): rooting and native retention.
11. [CancellationTokenSource.Cancel](https://learn.microsoft.com/en-us/dotnet/api/system.threading.cancellationtokensource.cancel?view=net-10.0): synchronous callbacks, repeat notification and exception-policy differences.
