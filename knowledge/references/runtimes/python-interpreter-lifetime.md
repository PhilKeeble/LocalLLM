---
id: reference-python-interpreter-lifetime
title: CPython thread states, GIL, free threading, module state and finalization
kind: reference
topics: [python, cpython, gil, free-threading, thread-state, subinterpreters, module-state, shutdown]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# CPython interpreter and thread lifetime evidence

## GIL and attached thread state are related but different
The global interpreter lock (GIL) serializes Python object access on conventional
CPython builds. An attached PyThreadState records the thread's interpreter context;
free-threaded builds still require attachment for ordinary Python C API access.
PyEval_SaveThread detaches; PyEval_RestoreThread reattaches. The
Py_BEGIN_ALLOW_THREADS/Py_END_ALLOW_THREADS macros wrap that pair. [1]

In recovered native work, identify the detached interval. Object access there
needs an applicable explicit exception, not an assumption that the original
caller still holds the GIL. A separately acquired buffer may remain usable under
its own contract; that does not permit unrelated Python API calls.

## Native callbacks: select the correct interpreter, not just any GIL
PyGILState_Ensure and PyGILState_Release must be paired on the same thread with
the corresponding handle. Those convenience APIs are not compatible with
subinterpreters. [1]

For a native worker callback, record thread, intended interpreter, retained
objects and callback lifetime. "GIL acquired" alone does not prove the callback
is operating in the objects' interpreter or that the interpreter is still alive.
Verify explicit thread-state management where required. A Python exception in
the callback also needs the native caller's error-handling contract.

## Free threading: individual container locks do not protect a whole algorithm
CPython supports free-threaded builds from 3.13. Container operations commonly
lock internally, but direct fields and unchecked macros may not; PyDict_Next
does not lock the dictionary during iteration. Extensions must protect their
own shared native state. Declaring Py_MOD_GIL_NOT_USED does not prove that code
actually obeys those requirements. [2]

Establish the runtime's actual GIL mode and shared objects. A thread-safe lookup
followed by a thread-safe update is not automatically one atomic authorization
or quota decision. Trace every interleaving-sensitive dependency rather than
clearing a race because one called API has internal locking.

## Borrowed list lookup versus strong acquisition under concurrency
PyList_GetItem returns a borrowed reference; concurrent list mutation can
invalidate it. PyList_GetItemRef, added in 3.13, returns a new strong reference. [3]
The latter protects the acquired object's lifetime, not the list's continued
association with that object or the object's logical state.

Investigate borrow-to-owned conversion as an acquisition sequence, not just the
eventual INCREF. If another thread can remove and destroy the object first,
incrementing it afterward is too late. Prefer evidence of a synchronized
acquisition or an appropriate strong-result API; do not assume all older borrows
are unsafe when the container is actually private or externally protected.

## CPython critical sections can suspend their locks
On free-threaded builds, CPython critical sections are a deadlock-avoidance
mechanism. Blocking operations can suspend an active section's locks and later
resume it. Use Py_BEGIN_CRITICAL_SECTION2 when two objects must be acquired
together; nested one-object sections can suspend the outer lock. The two-object
form does not remove the suspension rule. [2]

A lexical BEGIN/END pair therefore does not prove uninterrupted protection across
callbacks or blocking calls. Identify suspension points and recheck any assumed
association, size or authority after reacquisition. Keep this mechanism distinct
from a native mutex whose release behavior follows its own API.

## Per-module state versus process-global caches
PyModuleDef.m_size requests per-module state obtained through PyModule_GetState;
-1 denotes global-state use incompatible with subinterpreters. [4] Module-local
storage can separate instances, but a native static cache remains process-wide.
The isolation guide distinguishes module-owned state from genuinely global
resources and calls for deliberate sharing or locking of the latter. [5]

Map every cached PyObject*, callback and policy value to its module/interpreter
owner. A nonnegative m_size or support flag is not proof that all globals were
removed. For cross-session contamination, show which instance writes shared state
and which later operation consumes it; separate interpreters are not evidence
that every native dependency is isolated.

## Finalization races: a state check is not a shutdown barrier
CPython 3.14 documents that PyGILState_Ensure or PyEval_RestoreThread during runtime
finalization can hang the calling thread; older versions have different behavior. [1]
Py_IsFinalizing reports shutdown state, not ownership of a lifetime lock. [6]

Investigation guidance: find the stop-admission, callback-unregister and worker-drain
ordering before interpreter teardown. A check followed by an unsynchronized call
can race with shutdown. Strong references do not entitle a worker to keep using
a destroyed interpreter. A blocked callback holding a native lock can also prevent
the finalizing thread from completing.

## Py_FinalizeEx and reinitialization do not reset every native resource
Py_FinalizeEx belongs on the initialization thread with the main interpreter
active. Module destruction order is not dependable, dynamically loaded extensions
are not unloaded, and some extension allocations can survive. Repeated interpreter
initialization is not guaranteed to work for every extension. [6]

Trace native caches and retained pointers across interpreter generations. A DLL
remaining mapped does not mean its previous PyObject* values remain valid.
Audit teardown dependencies rather than assuming another module's globals are
still usable from a finalizer. Treat shutdown cleanup and a successful restart
as separate claims.

## Primary sources and scope
Reviewed 2026-10-02 against Python 3.14.8 documentation. GIL mode, interpreter
selection and shutdown behavior must match the target; private object/thread
layouts are not supplied as universal offsets. The older isolation guide's
process-wide-GIL discussion is not applied to free-threaded or per-interpreter-GIL
configurations. Its module-state design distinctions remain useful.

1. [Thread states and GIL](https://docs.python.org/3/c-api/threads.html): attachment, detachment, GILState pairing and finalization limits.
2. [Free-threaded extension support](https://docs.python.org/3/howto/free-threading-extensions.html): container locks, native state and critical-section suspension.
3. [List objects](https://docs.python.org/3/c-api/list.html): borrowed versus strong item lookup.
4. [Module objects](https://docs.python.org/3/c-api/module.html): per-module storage and m_size.
5. [Isolating extension modules](https://docs.python.org/3/howto/isolating-extensions.html): module-specific versus global resources.
6. [Interpreter initialization and finalization](https://docs.python.org/3/c-api/interp-lifecycle.html): state queries, teardown and repeated initialization.
