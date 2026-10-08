---
id: playbook-validation-debugger-evidence
title: Recover execution context, memory access and crash-dump evidence
kind: playbook
topics: [reverse-engineering, gdb, lldb, windbg, debugging, crash-dumps, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Debugger evidence for vulnerability and malware investigation

## Choose the observation question and the available artifact

State the missing fact: consumed count, object lifetime, resolved destination,
dispatch condition, failing access or effective identity. Use an existing core,
dump or trace when it answers that question. A debugger's ability to launch or
attach does not authorize doing so; prerequisites are in
playbook-validation-controlled-observation.

Determine whether this is a live stop, postmortem snapshot or replay session.
Record target architecture, debugger/backend, artifact identity and capture scope.
Do not attempt to discover historical writes by setting a watchpoint in a static
dump. Do not treat a core or minidump as a complete recording of prior execution.

## Bind every inspection to process, thread, frame and stop

Establish the selected process/address space, OS thread identity, stack frame and
register-context origin before interpreting a value. A tool's displayed index
need not equal an OS identifier. Preserve the selected identity and stop reason
with output. Distinguish saved fault registers from the currently selected thread
and from registers reconstructed while unwinding a caller frame.

Use the exposed tool's context-inspection capabilities; this workflow does not
require a particular debugger or command spelling. Platform-specific distinctions
remain important: Windows saved exception context is not simply current-thread
selection, and kernel contexts need separate address-space interpretation.
Implementation-specific contracts, when relevant, are in
reference-validation-gdb-lldb-context-memory and
reference-validation-windbg-context-memory.

## Match code and symbols before accepting a name or type

Recover loaded-module identities and ranges. Bind the relevant address to its
actual module and load range, then validate the debug artifact using
format-debug-information-build-matching.
Retain raw code bytes and machine coordinates even when symbolication succeeds.

Keep PE RVA, ELF load bias, Mach-O slide and generated-code maps distinct. A forced
symbol load, guessed type or source-line label is not a target contract. If code
was generated, replaced or unpacked, preserve that version and its capture time;
use reference-jit-code-identity and format-disk-versus-loaded-image.

## Recover the actual access rather than a plausible displayed value

Select the stopped instruction context, recover access type, effective address and
width, and preserve the raw operand bytes. Record which register values were saved,
reconstructed or unavailable. Use explicit memory extents and units; the debugger's
word-sized or pointer-sized display is not the input format's byte order or type.

Compare the access with the live object, subobject, initialized range and operation
contract. A readable debugger page does not prove application bounds, and question
marks do not mean zeros. For copy/length findings, correlate source, destination,
count and allocation from the same invocation rather than nearby unrelated stops.
Use playbook-re-sensitive-data-flow for the connecting instruction evidence.

## Verify breakpoint resolution and watchpoint coverage before using no-hit evidence

Record resolved code location or watched byte range, module/object generation,
enabled state, hardware/software mechanism, access type, conditions and filters.
Confirm installation errors as well as creation output. Recheck after module
reload, object replacement or code generation.

A pending breakpoint monitors no resolved instruction. A value-change watch may
miss same-value stores; a read/write watch is not read-only. A watchpoint on pointer
storage is not a watch on the pointee. Keep these scoped contracts separate in
reference-validation-breakpoint-watchpoint-evidence. A hit identifies an event;
it does not establish that the event violated bounds, lifetime or policy.

## Recover dump exception context without inventing missing history

For a Windows user-mode exception dump, preserve the exception record and use the
available saved exception context before attributing operands or stack frames.
Do not confuse an error-reporting thread with the failing context or a debugger
attach stop with an unhandled exception. For other cores retain the supplied stop
reason, per-thread registers and available metadata without imposing Windows rules.

Check whether each needed byte is captured, supplied by a backing image or absent.
Use reference-validation-core-dump-coverage for GDB filtering and Windows minidump
flags. The final crash can be a detector of earlier corruption; when the prior
write/history is missing, report the fault and candidate cause separately.

## Separate vulnerability evidence from malware behavior evidence

For vulnerabilities, connect the observed operand/effect to a violated contract
and the actor-controlled path. A fault alone does not establish controllability,
remote reachability or exploitability; a logic violation need not crash.

For malware, connect decoded configuration or a received selector to handler,
arguments, destination and result. Distinguish API entry, successful return and
asynchronous completion. A debugger-forced call can expose a capability without
showing natural activation. Missing network activity or a non-hit is inconclusive
without prerequisites and collection coverage. Use the Windows-specific workflow
playbook-debugging-windows-native-validation where its contracts apply.

## Deliver a compact evidence packet with explicit unknowns

Retain build/artifact identity, module coordinates, stop/context, inspection request
and raw result, relevant bytes, constraints and interpretation. Include inaccessible ranges,
unresolved symbols, unsupported watches and analyst interventions rather than
silently replacing them with defaults. Cross-check an important stack/type claim
against code and the applicable ABI before promoting it to a finding.

State what was observed, what is inferred, what remains unknown and the next
evidence that could distinguish competing explanations. Do not require another
execution merely to complete the packet. Reporting: playbook-vr-evidence-and-chaining.

## Basis and scope

Reviewed 2026-10-02. This analytical workflow uses the primary debugger contracts
in the reference-validation documents linked above. The workflow specifies
evidence needs, not debugger commands or a required toolstack. GDB, LLDB and
WinDbg have distinct context contracts; none is assumed to be exposed to the agent.
No target session was executed to create this documentation. Windows kernel,
remote, embedded and managed-runtime inspection can require additional context
and support beyond these shared anchors.
