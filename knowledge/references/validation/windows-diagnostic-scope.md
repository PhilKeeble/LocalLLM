---
id: reference-validation-windows-diagnostics
title: Windows memory diagnostics, injected failures and exception interpretation
kind: reference
topics: [windows, asan, application-verifier, pageheap, windbg, first-chance, diagnostics]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Windows diagnostic mechanisms and observation limits

## MSVC ASan coverage depends on modules and allocator overrides

Microsoft documents incomplete detection when a process mixes instrumented and
uninstrumented code. Replacement new/delete implementations, including MFC
overrides, can also cause missed or misclassified allocation errors. [1]

Investigative consequence: identify the allocating/releasing implementation and
loaded modules before interpreting a report category or silence. A sanitizer DLL
loaded into a process is not proof that every memory access is instrumented.
The scope of a compiler-inserted check differs from interception of an API call.

## An x64 ASan first-chance exception can belong to shadow commitment

Microsoft documents x64 ASan shadow pages being committed on demand through
exceptions handled by its runtime; WinDbg can expose these first-chance stops. [1]
This is not a rule that every first-chance access violation in an ASan process
is harmless. Match the fault address, instruction, runtime path and handler.

Keep break policy separate from exception handling. Silently swallowing exceptions
can change application behavior, while suppressing first-chance stops can hide
useful evidence. See reference-windows-seh-vectored-handlers. Classify the event
before choosing a separately authorized observation policy.

## Application Verifier layers change which errors are monitored or introduced

Application Verifier has separately selected verification layers. Its Cuzz layer
perturbs scheduling; low-resource simulation injects failures. Configuration is
persistent and hooks apply to newly started processes, not retroactively to a
running instance. A verifier stop identifies a reason with its stop number. [2]

Investigative consequence: preserve layers, stop code/parameters and actual API
outcome. A low-resource failure is a deliberately introduced condition; determine
whether the application mishandles it before calling it a defect. A changed
schedule may expose a valid race candidate without proving its production frequency.
Do not enable layers or restart shared applications merely to interpret a dump.

## PageHeap detection is not application-object validation

GFlags standard PageHeap checks allocation-tail patterns at free; full PageHeap
uses an inaccessible boundary page. Settings must precede launch and persist until
changed. [3] This distinguishes delayed corruption detection from a boundary fault;
neither proves all subobject accesses or semantic fields are valid.

Detailed facts, !heap evidence and allocator limitations remain in
reference-windows-heap-identity-diagnostics. First detected error versus initiating
operation is covered by reference-validation-detection-point-corruption.

## Sources and scope

Reviewed 2026-10-02. Windows user-mode diagnostics, not kernel Driver Verifier.
Actual architecture and toolchain support must be established for each mechanism.

1. [Microsoft ASan limitations](https://learn.microsoft.com/en-us/cpp/sanitizers/asan-known-issues?view=msvc-170): mixed modules, overrides and x64 first-chance handling.
2. [Application Verifier overview](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/application-verifier): layers, interventions, startup and persistence.
3. [GFlags/PageHeap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/gflags-and-pageheap): modes and configuration lifetime.
