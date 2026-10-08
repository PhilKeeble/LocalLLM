---
id: playbook-validation-first-fault-cause
title: Separate a detected fault from earlier corruption and establish the responsible operation
kind: playbook
topics: [crash-analysis, root-cause, memory-corruption, windbg, gdb, lldb, malware-analysis]
platforms: [windows, linux, macos, freebsd, android, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# From a fault record to a supported cause

## Preserve the event before assigning a bug class

Use existing authorized captures first. Record binary/module identity, process and
thread, capture time, platform/architecture, raw exception or signal, valid event
fields, saved registers, instruction bytes and available memory. Identify missing
data rather than substituting zero or values from another run. A debugger's current
thread/frame can differ from the fault context; use playbook-validation-debugger-evidence.

For Windows, distinguish first-chance notification from an unhandled exception;
first chance does not mean the program's first incorrect operation. Record debugger
handling decisions. For Linux, distinguish a hardware-origin report from a signal
sent by software before interpreting a fault address. Other platforms require their
own reporting contracts, not copied Linux numeric constants.

## Identify the failed access, not just the nearest symbol

From the matching instruction and saved context, determine whether the reported
operation reads, writes or fetches instructions. Recover the effective address,
access width and relevant operands where the architecture and capture permit.
Distinguish the instruction address from the accessed address. Do not assume every
reported event has a precise access address or a single memory operand.

For a multi-byte access, compare the entire attempted range with independently
established object bounds, lifetime and mapping permissions in the same process
instance. A readable page is not proof of a valid object, and the start address
being inside an object does not validate the full width. For an indirect transfer,
separate a failure reading its target pointer from a failure fetching instructions
at the resulting destination. A symbol name alone proves neither operation.

## Trace backward from the consumed value to the responsible definition

For the failing pointer, index or length, recover its last relevant definition,
copies, arithmetic, conversions and validation on the feasible path. Distinguish
data originating in an input from data an actor can actually control at the sink.
Follow aliases and intervening calls; a decompiler variable can represent several
machine-level value versions. Use playbook-re-sensitive-data-flow.

For suspected stale memory, connect the access to one allocation generation and
its ownership/release history. A later object at the same address is not the same
object. For suspected corruption, identify the earlier write, its full extent and
the violated boundary; a damaged pointer alone leaves its writer unresolved.
Keep competing explanations such as wrong context, storage failure, invalid type
interpretation and intentional error signaling until evidence excludes them.

## Treat delayed detectors as limits on chronology

A stack-cookie check, heap check at free, sanitizer report or asynchronous tag fault
may detect an error after the initiating operation. Preserve the detector's actual
scope and the interval it constrains; do not call the reported function the earlier
writer without a causal link. An automated crash summary is not that link.
Use reference-validation-detection-point-corruption and
reference-validation-signal-origin-fault-precision for qualified examples.

Constructed bounds example: a copy attempts 20 bytes starting at the base of an
independently proven 16-byte destination. The final four bytes exceed it even if mapped
memory prevents an immediate fault. A later crash is not needed to establish the
bounds violation, but attributing that crash to the copy requires additional
data-flow evidence. Conversely, an observed crash does not prove this copy occurred.

## Separate exception-driven behavior from malicious intent

For malware analysis, recover the trigger, applicable handler, context changes and
continuation. A deliberately raised exception can participate in control flow;
the exception alone does not prove evasion or malicious behavior. Determine which
subsequent actions and effects are evidenced. Debugger handling changes can alter
the application's path, so preserve them as interventions rather than silently
treating the resulting trace as unmodified behavior.

For vulnerability analysis, state the violated contract and reachable operation
separately from impact. A caught fault does not repair earlier damage; an unhandled
fault does not establish arbitrary code execution. Record the actual terminal or
recovery path and any completed effects before it. Windows dispatch details live
in reference-windows-seh-vectored-handlers.

## Report observation, causal explanation and uncertainty separately

A useful result names the input/state prerequisite, detected operation, relevant
addresses and widths, earlier operation if established, violated invariant,
observable consequence and remaining alternatives. Cite raw evidence for each link.
Use candidate cause when the backward chain is incomplete; do not silently promote
crash classification or tool confidence into a demonstrated cause.

If another observation is necessary, choose the smallest authorized isolated
observation that distinguishes the competing explanations. Changes to diagnostic
mode, scheduling, memory layout or exception handling belong in the record.
Neither forcing a branch nor overwriting a pointer proves natural reachability.
This workflow does not require execution when existing evidence is sufficient.
If simplifying the triggering conditions, use playbook-validation-failure-minimization
to preserve the relevant causal chain rather than merely any terminal fault.

## Source basis and scope

Reviewed 2026-10-02. Investigative synthesis, with platform-specific facts kept in
the linked local references. Architecture/platform tags identify intended uses;
they do not assert identical exception semantics or debugger capabilities.

- [Microsoft EXCEPTION_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-exception_record): event fields and code-dependent access information.
- [Microsoft debugger exception handling](https://learn.microsoft.com/en-us/windows/win32/debug/debugger-exception-handling): debugger opportunities and application dispatch.
- [Linux sigaction](https://man7.org/linux/man-pages/man2/sigaction.2.html): origin-dependent signal information.
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): first detected error and available access/lifetime history.
