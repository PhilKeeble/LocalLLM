---
id: playbook-validation-interpret-diagnostics
title: Interpret sanitizer and platform diagnostic reports without overstating coverage
kind: playbook
topics: [sanitizers, asan, ubsan, msan, tsan, pageheap, application-verifier, malware-analysis]
platforms: [windows, linux, macos, android, freebsd, netbsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Match the diagnostic mechanism to the investigation question

## Identify what was actually monitored

Start from existing authorized reports, dumps, build records and disassembly.
Record binary identity, compiler/runtime, OS/architecture, instrumented modules,
enabled checks, exclusions, runtime options, allocator and capture interval.
A tool's name in a log or an imported runtime does not prove the disputed operation
was monitored. Platform/architecture tags are not promises of universal tool support.

Separate compiler instrumentation, runtime interception, allocator checks and
page-permission faults. Loading a runtime beside an arbitrary binary does not
insert missing compiler checks into its instructions. An instrumented wrapper
around an uninstrumented parser does not establish instrumentation inside it.
Any new execution or configuration changes require separate authorization and an
appropriate isolated environment; interpreting a report needs no live experiment.

## Select the rule that answers the disputed question

| Question | Relevant evidence and local reference |
| --- | --- |
| Invalid memory access or release? | ASan access/allocation evidence: reference-validation-asan-addressability |
| A selected language/arithmetic check failed? | UBSan exact check and reporting mode: reference-validation-ubsan-check-semantics |
| A consumed value lacked initialization? | MSan origin and use: reference-validation-msan-initialization-origins |
| Conflicting accesses lacked ordering? | TSan access pair and synchronization visibility: reference-validation-tsan-race-evidence |
| Windows allocator/API diagnostic? | Layer, stop and runtime scope: reference-validation-windows-diagnostics |
| Memcheck use or leak report? | Initializedness and reachability categories: reference-validation-memcheck-report-meaning |

These mechanisms are not interchangeable. A bounds diagnostic does not validate
authorization; a race diagnostic does not identify every transaction error.
For synchronous/asynchronous ARM64 Linux MTE events, use
reference-validation-signal-origin-fault-precision rather than ASan shadow rules.

## Extract raw report evidence before accepting its classification

Keep the diagnostic category, actual access or check, address, width, operands,
thread, raw PCs, module identities and available allocation/free/origin stacks.
Use matching symbols; preserve unresolved addresses rather than inventing names.
Separate the offending-use stack from allocation, release, thread-creation and
value-origin stacks. Their first frames answer different questions.

For Windows, record exception chance, context and verifier parameters. An expected
runtime event and an application defect require different evidence. For a trap,
recover the branch and check that led to it; an illegal-instruction label alone
does not identify UBSan or the violated rule. Do not turn a detector label into
an earlier corrupting write without the chain in playbook-validation-first-fault-cause.

## Determine whether reporting continued, stopped or was unavailable

Preserve the reporting destination, suppressions, recovery/trap policy and process
termination evidence. A normal exit can coexist with a recovering diagnostic;
a nonzero exit can reflect runtime startup failure instead of a target defect.
A missing log, failed symbolizer or missing captured memory remains an evidence
gap. Do not report a clean execution merely because the observer saw no crash.

If a fuzzer consumes only crashes, determine whether that matches the configured
diagnostic's failure behavior. The observation rule belongs in the analysis record;
it must not silently turn recovering warnings into successful test cases.
Disabling a report changes visibility, not the application's violated invariant.

## Check report validity without assuming either infallibility or noise

Recover the actual target operation and compare it with the diagnostic's contract.
Check mixed instrumentation, custom allocators, annotations, assembly boundaries,
symbol identity and synchronization visibility where relevant. If an apparent
false positive depends on a missing annotation or unsupported configuration,
record the specific evidence; do not dismiss a warning solely because it is inside
a familiar library. Conversely, tool confidence does not replace that evidence.

For a candidate leak or stale use, apply playbook-validation-allocation-lifetime-trace.
For a concurrent candidate, identify which ordering or lifetime guarantee is absent.
Absence of a warning over one input/schedule does not establish correctness over all paths.

## Compare diagnostic builds and malware behavior with the original target

Instrumentation can change code, allocation layout, timing and termination. A
rebuild may also change dependencies, compiler options or conditional code.
Associate the reported operation with the original binary's instruction/data flow;
record differences that prevent direct transfer. A changed crash location may be
earlier detection, not a new root cause or proof of identical exploitability.

For malware analysis, identify diagnostic helpers separately from application
behavior. Sanitizer imports, shadow checks and quarantine activity are not evidence
of evasion. A clean memory-safety run does not establish benign intent: harmful
file, process or network actions can use valid memory and ordinary API contracts.
Report evidenced effects separately from defect detection and environmental limits.

## Source basis

Reviewed 2026-10-02. Investigative synthesis; the six local references retain
mechanism-specific primary sources and offline facts. This playbook interprets
diagnostic evidence; it is not an instruction to enable diagnostics on a shared host.

- [Clang sanitizer documentation](https://clang.llvm.org/docs/AddressSanitizer.html): compiler/runtime distinction and report scope.
- [Microsoft ASan limitations](https://learn.microsoft.com/en-us/cpp/sanitizers/asan-known-issues?view=msvc-170): partial instrumentation and debugger-visible runtime events.
- [Application Verifier](https://learn.microsoft.com/en-us/windows-hardware/drivers/devtest/application-verifier): selected layers and introduced conditions.
