---
id: reference-validation-detection-point-corruption
title: Security-check stops and sanitizer reports do not identify every earlier corrupting operation
kind: reference
topics: [crash-analysis, memory-corruption, security-cookie, gs, asan, windbg, root-cause]
platforms: [windows, linux, macos, freebsd, android, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Detection point and prior corruption

## MSVC stack-cookie validation occurs after operations it protects

MSVC /GS places a security cookie in selected functions and checks it on function
exit; Microsoft also documents checking during frame unwinding on 64-bit Windows.
A changed value can indicate an
earlier stack overwrite. /GS detects some overruns; it is not a general proof of
memory safety. [1]

Investigative consequence: a stop in cookie validation identifies the check, not
necessarily the write that changed the value. Recover the protected frame, cookie
initialization, expected value, intervening writes and actual check. Do not assign
the checker as the vulnerable copy routine. A fault before the check can also
precede detection; absence of a cookie stop does not validate all local accesses.

## AddressSanitizer's first reported error is scoped to detection

Clang's AddressSanitizer documentation describes stopping at the first detected
error by default, because continued execution after corruption can produce
misleading results. Reports distinguish the invalid access and available
allocation/deallocation history. [2]

Investigative consequence: preserve the report before subsequent error handling
obscures it, but do not rewrite first detected as first invalid action in all
program history. Establish instrumentation coverage, configuration and relevant
uninstrumented components. A changed crash site in an instrumented build can
identify an earlier detected access without proving identical production layout
or timing. The word ASan in a log does not establish complete coverage or identify
every enabled diagnostic option.
Use reference-validation-asan-addressability for shadow, annotation and coverage
limits, and playbook-validation-interpret-diagnostics for report interpretation.

## Windows heap detection can occur at release rather than at overwrite

GFlags standard PageHeap checks allocation-tail fill patterns when allocations
are freed; full PageHeap uses an inaccessible boundary page. The detailed contracts
and scope live in reference-windows-heap-identity-diagnostics. [3]

Investigative consequence: a corruption stop during free can follow an earlier
write by another function. It does not by itself prove double free, wrong-heap
release or a defect in the allocator. Trace the same allocation generation and
which bytes violated the diagnostic condition. A different diagnostic mode can
move the stop without changing the underlying application error; it can also
change layout and timing. Keep the observations separate.

## An automated failure summary is not an earlier-writer attribution

In user mode, WinDbg !analyze reports the current exception; in kernel mode it
reports the most recent bug check. Verbose output adds detail. Its -c mode can
continue execution for configured known issues. [4]

Investigative consequence: preserve raw exception/context, code and operands
alongside the summary. A named module or failure label is not a demonstrated
earlier writer, source-to-sink path or exploitability conclusion. Do not use an
execution-continuing option as if every analysis command were a passive read.
For the actual observation contract use reference-validation-windbg-context-memory.

## A detector record and a causal chain answer different questions

Constructed example: an unchecked length overwrites a saved pointer, later code
loads that pointer, and a dereference faults. The fault identifies the consumer;
the unchecked write is the candidate initiating error. If the earlier write is
not evidenced, report the invalid dereference and unresolved pointer provenance,
not a confirmed buffer overflow.

Similarly, a same-address allocation after release is a different object generation.
A diagnostic history must connect the accessed bytes to the relevant allocation
and release, not merely a numerically equal address. Use
playbook-validation-first-fault-cause for the backward investigation and
playbook-re-sensitive-data-flow for aliases, value versions and feasible paths.

## Sources and scope

Reviewed 2026-10-02. Product-specific detector examples and explicitly constructed
causal reasoning. Architecture tags do not claim every detector supports every
listed target. A detector's availability and enabled configuration must be
established for the particular capture.

1. [MSVC /GS](https://learn.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check?view=msvc-170): cookie initialization, checks and limited protection.
2. [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): first detected error and report interpretation.
3. [Microsoft GFlags/PageHeap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-and-pageheap): tail-pattern versus boundary-page detection; detailed local reference cited above.
4. [WinDbg !analyze](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-analyze): exception/bug-check scope and execution-continuing option.
