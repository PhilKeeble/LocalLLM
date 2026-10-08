---
id: reference-validation-tsan-race-evidence
title: ThreadSanitizer conflicting accesses, synchronization visibility and logical races
kind: reference
topics: [tsan, threadsanitizer, data-race, synchronization, atomics, instrumentation]
platforms: [linux, macos, android, freebsd, netbsd]
architectures: [x64, arm64, powerpc]
---
# TSan race evidence

## A data-race report needs both accesses and the ordering question

ThreadSanitizer instruments code to detect data races. Reports identify conflicting
accesses and threads, with available creation stacks. Preserve both access sites,
widths, object identity and the synchronization that should order them. [1]

For ordinary C++ threads, conflicting actions with at least one non-atomic action
and no happens-before order constitute a data race. [2] This is an ordering
property, not a requirement that both instructions physically execute at the
same instant. Do not reduce the evidence to whichever thread appears first in a log.

## Unobserved synchronization can produce misleading reports

Clang warns that uninstrumented dependencies can cause missed races or false
reports. A TSan ignorelist can remove all instrumentation from a function, losing
atomic synchronization and stack evidence. In contrast, no_sanitize("thread")
omits plain non-atomic load/store instrumentation but retains other instrumentation.
These exclusions are not interchangeable. [1]

Establish actual instrumentation and synchronization visibility before dismissing
a warning or accepting a clean run. A custom lock's name is not proof that the
detector observed its ordering. Scheduling under instrumentation is not every
production schedule.

## Data-race freedom does not prove transaction correctness

Constructed example: two threads separately lock to check a remaining quota,
unlock, then each lock to spend it without rechecking. Every access can be ordered
while the combined operation grants twice. TSan silence does not refute this
logical race. Recover the compound invariant and commit point using
reference-concurrency-memory-order-atomic-invariants.

## Source and scope

Reviewed 2026-10-02. Actual compiler/runtime and supported target must match;
the presence of ASan support does not establish TSan support.

1. [Clang TSan](https://clang.llvm.org/docs/ThreadSanitizer.html): reports, exclusions and uninstrumented modules.
2. [C++ data races](https://eel.is/c++draft/intro.races): conflicting actions and happens-before.
