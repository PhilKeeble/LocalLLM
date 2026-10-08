---
id: reference-go-concurrency-and-unwind
title: Go channel synchronization, cancellation, defer and panic boundaries
kind: reference
topics: [go, goroutines, channels, synchronization, cancellation, panic, cleanup]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm, arm64, riscv64]
---

# Go communication and cleanup contracts

## Scope

Reviewed 2026-10-02 against the Go memory model, language specification and
standard-library documentation. These facts describe language/API obligations,
not a particular runtime's scheduling policy. Scheduler identity and stack
interpretation: reference-go-binary-runtime-evidence. Native resources and
retained pointers: reference-go-cgo-and-unsafe.

## A channel event establishes a particular synchronization edge

A send is synchronized before completion of its matching receive. Closing a
channel is synchronized before a receive that returns zero because of closure.
For an unbuffered channel, the receive also precedes completion of the matching
send. Goroutine termination alone establishes no synchronization edge.
[Go memory model: goroutines and channels](https://go.dev/ref/mem).

Investigative consequence: name the send/receive or close/receive pair, not just
the channel variable. Do not infer that completion of a buffered send means the
consumer processed the item. Identify an explicit completion acknowledgement or
join before releasing external resources or reporting a durable effect.

## Nil, closed and empty channels represent different states

Nil-channel communication cannot proceed. A send to a closed channel panics;
closing nil or already closed channels panics. Receivers can drain buffered
values after closure, then receive zero values with ok=false.
[Channel and close contracts](https://pkg.go.dev/builtin#close),
[Go specification: channel communication](https://go.dev/ref/spec#Send_statements).

Investigative consequence: distinguish an actual zero-valued message from closure
using the Boolean result when relevant. Closing a channel is not proof that all
consumers, senders or callbacks have stopped. Repeatedly selecting a closed
channel can keep a loop runnable even when no useful work remains.

## Select does not prioritize a cancellation case

When multiple communications are ready, select chooses among them pseudo-randomly;
source order is not priority. Channel operands and send values are evaluated
before selection, even for a case not chosen. A default avoids blocking; it does
not prove other work has completed.
[Go specification: select](https://go.dev/ref/spec#Select_statements).

Investigative consequence: a ready cancellation channel does not categorically
exclude another ready send or side effects while evaluating its value. Recover
the application's cancellation/commit invariant and any additional state check
instead of treating select syntax as a transaction boundary.

## Cancellation requests are not joins

context.CancelFunc requests abandonment but does not wait for work to stop.
Context.Done can be nil when cancellation is impossible. The stop function from
context.AfterFunc does not wait for an already started callback to finish.
[Context cancellation and AfterFunc](https://pkg.go.dev/context).

Investigative consequence: trace observation of cancellation, actual terminal
completion and release as separate events. A timeout wrapper can return while
delegated work retains a buffer, handle or authority. Cancellation cannot be
assumed to roll back an external write. Follow any independent completion signal
and the paths that ignore or replace a propagated context.

## Data races can invalidate multiword value consistency

Go's memory model permits multiword accesses to be implemented as separate word
operations. Races can combine inconsistent pointer/length or pointer/type fields;
interfaces, slices and strings can consequently participate in memory corruption.
[Go memory model: implementation restrictions](https://go.dev/ref/mem).

Investigative consequence: bounds checks on a raced slice descriptor do not prove
that all fields came from one coherent assignment. Conversely, identify an actual
unsynchronized conflicting path rather than declaring every shared slice unsafe.
Separate race-free access from a logically incorrect but synchronized operation.

## Defer and recover describe control flow, not rollback

Deferred call arguments are evaluated when defer executes; calls run in reverse
registration order on return or panic unwinding. Deferred functions can alter
named results. Recovery occurs within the panicking goroutine, not a parent
goroutine's deferred handler. It does not resume the faulting instruction.
[Defer, panic and recover](https://go.dev/blog/defer-panic-and-recover).

recover must be called directly by a deferred function to stop the panic.
[Specification: handling panics](https://go.dev/ref/spec#Handling_panics).

Investigative consequence: distinguish an eagerly captured argument from a closure
reading mutable state later. A defer inside a loop can retain resources until
function exit. A recovered panic can leave prior mutations intact or produce
misleading success if an error result is not set. Reconstruct the effective
return and cleanup order, not just the presence of a recovery wrapper.

## Goroutine exit and process exit have different cleanup

runtime.Goexit terminates its calling goroutine and runs deferred calls; it is
not a panic, so recover there returns nil. [runtime.Goexit](https://pkg.go.dev/runtime#Goexit).
os.Exit terminates the program without running deferred functions.
[os.Exit](https://pkg.go.dev/os#Exit).

Investigative consequence: do not draw ordinary panic-recovery edges through a
process-exit path. GC reachability does not substitute for closing a file,
finishing a transaction or draining an asynchronous native user. A fatal runtime
failure must be analyzed under its own behavior, not assumed recoverable because
ordinary bounds panics can be caught.
