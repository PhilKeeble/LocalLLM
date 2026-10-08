---
id: reference-concurrency-locks-waits-reentrancy
title: Lock coverage, waits, deadlocks and reentrant callbacks
kind: reference
topics: [concurrency, locks, deadlocks, reentrancy, callbacks, signals]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Lock coverage, waits, deadlocks and reentrant callbacks

## Scope and lock identity
Reviewed 2026-10-02. Standard-library facts are scoped to C++ mutex/condition_variable;
signal facts below to the Linux/POSIX contracts reported by Linux man-pages.
Other lock, event and callback APIs need their own ownership and wakeup contracts.
The lock address/object matters: identical lock function names do not prove two
paths serialize each other. Recover per-object versus global locks, recursive
behavior, read/write modes and lifetime. An attacker-controlled request can
select a different object and therefore a different lock from the one assumed.

## Mutex ownership and coverage
C++ mutex unlock requires ownership by the calling thread and synchronizes with
subsequent acquisitions of that same mutex. Relocking a nonrecursive mutex while
owning it violates its precondition and can deadlock. Destroying an owned mutex
is undefined behavior. [1]

Investigation inference: protection must cover the relevant check, state update
and dependent use, or another protocol must bridge gaps. A pointer copied under
a lock can become dangling after unlock unless a reference, pin or other lifetime
guarantee persists. Error returns, exceptions and callbacks can bypass expected
unlock paths. Record lock/unlock pairs on each feasible exit; a lock held during
validation but absent during mutation is not automatically sufficient coverage.

## Condition variables are not durable permission tokens
C++ condition_variable::wait atomically releases the supplied mutex and blocks,
then reacquires it before returning. It can wake spuriously; the predicate form
rechecks in a loop. Concurrent waiters use the required same mutex. [2]

Consequently a wakeup, notify or non-timeout return alone does not prove the
application predicate is currently true. Another waiter may consume the item
before this thread reacquires the lock. Trace predicate changes under the agreed
synchronization, including shutdown. A wait releases its lock: assumptions made
before waiting must be re-established afterward. A timeout is not proof that
the operation being awaited has ceased running or relinquished its resources.

## Deadlock requires a feasible wait dependency
Constructed deadlock: thread A holds L1 and blocks acquiring L2; thread B holds
L2 and blocks acquiring L1. Both holds and waits must coexist. Opposite lock
orders in mutually exclusive states are a candidate, not a proved deadlock.
Include joins, completion waits, callbacks and event-loop dispatch in the
dependency graph, not only mutex calls. A shutdown thread waiting for a worker
while holding the lock that worker needs can deadlock without two lock APIs.

Distinguish indefinite wait, bounded timeout, starvation and livelock. A timeout
may prevent permanent deadlock while still causing resource exhaustion or an
incorrect fail-open path. Record the failure recovery and attacker control of
the prerequisite operations; a paused debugger thread alone is not a target hang.

## A condition-variable deadline does not bound mutex reacquisition

C++ condition_variable::wait_until reacquires its supplied mutex before returning;
that reacquisition can itself block. Expiry unblocks the timed wait, not necessarily
the complete function within a hard wall-clock bound. [2]

Investigative inference: include the lock holder in the dependency analysis after
the deadline. An application that relies on this return to cancel work or release
another resource may retain that resource longer than the nominal interval.
Distinguish this API contract from a timer that terminates a separate worker.
For CPU-active retry loops rather than blocked waits, use
reference-parser-algorithmic-work-graph-bounds; for end-to-end budget recovery,
use playbook-re-algorithmic-resource-boundary.

## Reentrancy can occur on one thread
Constructed callback sequence: operation sets state=UPDATING, calls an external
callback, callback reenters close(), which destroys or changes the object; outer
operation resumes with a stale pointer or assumption. No second worker thread
is necessary. Recursive locks can allow this sequence; nonrecursive locks may
instead self-deadlock. A lock is not a general reentrancy guard.

For callback, destructor, nested IPC or event-pumping calls, establish whether
that particular API can invoke user code before return. Record state exposed
at callout, permitted nested entries, retained lifetime and post-call checks.
Do not assume every synchronous IPC call pumps messages or every callback is
inline: those are runtime-specific facts requiring evidence.

## Signals and library reentrancy
Linux signal-safety documentation distinguishes async-signal-safe functions
from ordinary library calls. Buffered stdio such as printf is not guaranteed
async-signal-safe; interruption while internal state is partially updated can
make a nested invocation unsafe. Safety of a listed function does not make
the handler's own shared state protocol correct. [3]

Investigate handler registration, blocked signal masks per relevant thread,
shared fields, allowed operations, saved error state and interrupted cleanup.
Ordinary thread safety or a library's internal mutex is not proof of signal
safety: a handler can interrupt the same thread while it owns that mutex.
Avoid importing this POSIX signal model into Windows exception or APC analysis.

## Primary sources
Reviewed 2026-10-02. C++ living draft; Linux man-pages signal-safety documentation.
The constructed dependency/callback examples are investigative reasoning.

1. [C++ mutex contracts](https://eel.is/c++draft/thread.mutex.requirements.mutex).
2. [C++ condition-variable wait](https://eel.is/c++draft/thread.condition.condvar).
3. [Linux signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html).
