---
id: reference-python-reference-ownership
title: CPython strong and borrowed references, stolen ownership and re-entrant cleanup
kind: reference
topics: [python, cpython, refcounts, borrowed-references, ownership, reentrancy, allocation]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# CPython object lifetime and ownership evidence

## New, borrowed and stolen references describe responsibility
A strong reference keeps an object alive; the holder eventually releases it.
A borrowed reference relies on another owner. C functions called by Python borrow
their argument objects during the call; retaining them beyond it requires ownership.
A successful Python-callable C function transfers ownership of its result to
the caller. [1]

Track reference responsibilities, not pointer copies. Assigning a PyObject* to
a second variable does not create another owned reference. A "stolen" reference
means the called API consumes the caller's ownership; whether it does so on an
error path is API-specific. Do not apply one steal rule to all container or module
functions. Reference ownership does not itself authorize access to the object.

## Py_INCREF, Py_DECREF and immortal objects
Py_INCREF acquires a strong reference; Py_DECREF releases one and can invoke
deallocation when the last strong reference is removed. Their X variants accept
NULL. Immortal objects need not change a counter for those operations; a large
observed count need not equal the number of live owners. On free-threaded builds,
a count of one does not establish exclusive access by the current thread. [2]

Do not derive safe lifetime or synchronization from one memory snapshot of a
reference counter. Recover acquisitions, transfers and releases on the relevant
path. An optimized or special-case missing increment is not alone a leak or UAF.

## Py_DECREF and Py_CLEAR: deallocation can re-enter Python
Releasing a final reference can invoke Python code, including __del__.
Reachable state must therefore be consistent before the release. Py_CLEAR clears
the owning slot before decrementing its old value; Py_SETREF installs the new
value before releasing the old one. [2]

Investigate a destructor as a callback edge: which globals, containers or extension
objects can it revisit? Setting a slot after DECREF can be too late. These macros
address local update ordering, not every compound invariant or native lock. A GIL
does not prohibit same-thread re-entrancy through a destructor.

## Borrowed list items can become invalid across unrelated calls
CPython's extension guide demonstrates a borrowed list item becoming invalid
when replacing another item triggers a destructor that mutates the list. [1]
The list itself staying alive does not keep every old member alive.

Trace each intervening call, destructor, callback and container mutation before
using a borrow again. Acquire required ownership while the borrow is still valid;
incrementing an already stale pointer is not a repair. For concurrently mutable
lists, an unsynchronized borrow-then-increment sequence can itself race. Relevant
strong-reference APIs and free-threaded limits are in
`reference-python-interpreter-lifetime`.

## List setters: stolen references and unchecked initialization
PyList_SetItem consumes the supplied item reference even on error; on success it
also releases the replaced item. PyList_SET_ITEM consumes the new reference but
does not release a replaced item and supplies no normal error checking.
PyList_New with positive length initially contains NULL slots, not None values. [3]

Do not expose a partially filled new list to Python. Distinguish fill-once
construction from replacing a live entry. After a failed stealing call, another
DECREF of the transferred reference can be wrong; after unchecked replacement,
the displaced ownership can leak. A debug assertion is not a production bounds
check. Audit the actual function/macro and feasible failure path.

## Module insertion: PyModule_AddObject has a different error-path rule
PyModule_AddObject steals its value reference only on success. PyModule_Add steals
even on error; PyModule_AddObjectRef does not steal the caller's reference.
The latter two APIs were added in 3.13 and 3.10 respectively. [4]

Use the identified callee's rule when tracing initialization failures. Similar
names do not justify identical cleanup. Preserve which object was created, which
insertion succeeded and what the cleanup still owns; partial module population
must not silently become proof that all registered operations are ready.

## Python allocation domains and native deallocators must match
CPython distinguishes raw, mem and object allocator domains. Allocate and release
through the same domain: PyMem_Malloc pairs with PyMem_Free, not arbitrary free.
Raw APIs can operate without an attached Python thread state; mem APIs require
one. Free-threaded builds require the object domain for Python objects and not
for unrelated native buffers. [5]

Establish allocation origin and exact pointer before interpreting a free. A
PyObject* must follow object destruction, not be treated as a raw buffer merely
because its address is on the heap. Shared low-level allocator implementation
does not make API families interchangeable or remove object finalization duties.

## PyCapsule: a named opaque pointer is not validated native storage
PyCapsule wraps a non-NULL native pointer and can have a destructor callback.
PyCapsule_GetPointer requires an exact capsule-name match, including NULL names.
The name string must outlive the capsule; it is not automatically copied into
independent storage. PyCapsule_Import obtains a pointer through module import
and attribute lookup. [6]

Recover the pointer's real type, allocation and destructor contract. A matching
name checks the capsule interface, not whether the pointed-to object is live,
large enough or authorized for this caller. Retaining the extracted pointer does
not retain the capsule owner. In behavior recovery, capsule import can explain
an indirect native call whose implementation is absent from ordinary OS imports.

## Extension GC traversal: published object fields must be valid
CPython container types participating in cyclic garbage collection provide
Py_TPFLAGS_HAVE_GC and traversal support; mutable containers also need clearing
support. Reference-bearing fields must be initialized before GC tracking and
must not be invalidated while still exposed to traversal. GC allocation and
deallocation must follow the corresponding type allocator/free contract. [7]

Inspect effective type slots, including inherited behavior, before calling a
missing local function a defect. Compare construction, tp_traverse, tp_clear and
deallocation paths. Traversing an uninitialized field, omitting an owned edge or
clearing a field twice are different hypotheses requiring their own path evidence.
Reference counting alone does not explain every cycle-related lifetime.

## Primary sources and scope
Reviewed 2026-10-02 against Python 3.14.8 documentation. Ownership statements name
specific APIs; they are not generalized from spelling or a fixed refcount layout.
For buffer ownership use `reference-python-buffers-text`; interpreter identity
and finalization are separate from object reference ownership.

1. [Extending Python: reference ownership and Thin Ice](https://docs.python.org/3/extending/extending.html): arguments, results and invalidated borrows.
2. [Reference counting](https://docs.python.org/3/c-api/refcounting.html): strong references, immortal objects and re-entrant release.
3. [List objects](https://docs.python.org/3/c-api/list.html): initialization and setter ownership.
4. [Module objects](https://docs.python.org/3/c-api/module.html): AddObject/Add/AddObjectRef differences.
5. [Memory management](https://docs.python.org/3/c-api/memory.html): allocator domains and thread-state constraints.
6. [Capsules](https://docs.python.org/3/c-api/capsule.html): pointer/name/destructor contracts and import behavior.
7. [Cyclic garbage collection support](https://docs.python.org/3/c-api/gcsupport.html): traversal, clearing and tracking order.
