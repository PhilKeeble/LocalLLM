---
id: reference-linux-signals-fork-exec-state
title: Linux signals, forked threads and state across exec
kind: reference
topics: [linux, signals, fork, exec, threads, reentrancy, inherited-state]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Signal and process-transition evidence

## Fork from a multithreaded process does not copy all running threads

Linux fork creates a child with the calling thread while copying the address
space, including synchronization-object state. The documented safety rule
restricts calls in that child to async-signal-safe functions until exec. [1]

For investigation, distinguish inherited bytes/lock state from a live child
thread that can release a lock. A child deadlock or failed helper is not evidence
of deliberate evasion without the actual operation and prerequisites. Identify
atfork handlers and supported wrapper behavior rather than assuming all launch
APIs implement the same transition. Parent and child descriptors also retain
shared open-file descriptions; use reference-linux-descriptors-open-file-descriptions.

## Signal disposition and per-thread mask answer different questions

Linux signal dispositions are process-wide, while each thread has its own mask
of blocked signals. Signals can be process-directed or thread-directed. [2]

Investigate handler registration, selected target, mask, pending state and actual
delivery. Registration does not establish execution, and a blocked signal is
not necessarily absent. A process-directed signal cannot be assigned to one
thread merely from its process ID. Bind the handler's effect to the captured
thread and state; kernel-generated faults and externally requested signals need
their own provenance. Signal names alone establish neither maliciousness nor
the operation that caused a failure.

## A signal handler can interrupt partially updated application state

POSIX async-signal-safety concerns functions usable from a signal handler;
thread-safety alone is a different guarantee. The signal-safety manual explains
how interrupted library state can make a nested call unsafe. [3]

For investigation, trace interrupted operation, shared state, handler calls and
the relevant safe-function contract. A mutex-protected main-thread operation
does not automatically make a handler call safe or prevent reentrant deadlock.
Conversely, handler presence alone is not a defect. Establish the same object's
inconsistent state or unsupported call context, retaining delivery and masking
conditions. Do not assume a compiler-generated signal frame has a portable layout.

## Successful exec resets caught handlers but preserves the signal mask

Linux execve resets caught signal dispositions to defaults. The signal mask is
preserved across exec; fork inherits a copy of that mask. [2][4]

For investigation, separate successful exec from a failed attempt that continues
in the original image. A new executable image does not imply a fresh unblocked
signal environment. Likewise, a pre-exec handler registration does not prove
the new image retained that handler. Preserve supported ignored/default behavior
and exception cases from the actual contract; this section only states caught-
handler and mask distinctions, not a complete process-state reset matrix.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19 and its POSIX-scoped safety discussion.
No kernel signal-frame offsets, signal-number table or particular launch-tool
defaults are assumed.

1. [fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html): multithreaded child and copied state.
2. [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html): dispositions, masks, direction and inheritance.
3. [signal-safety(7)](https://man7.org/linux/man-pages/man7/signal-safety.7.html): async-signal-safety and reentrancy.
4. [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html): caught-handler reset.

Workflow: playbook-linux-async-lifetime. General reentrancy evidence remains in
the shared concurrency references.
