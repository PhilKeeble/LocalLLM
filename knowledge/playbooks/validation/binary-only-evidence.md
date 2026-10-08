---
id: playbook-validation-binary-only-evidence
title: Evaluate binary-only instrumentation and emulation findings without inventing target behavior
kind: playbook
topics: [reverse-engineering, binary-fuzzing, emulation, instrumentation, windbg, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, android, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Interpret binary-only execution evidence

## Identify which question the execution model can answer

Record the binary/build, code bytes, architecture/mode, ABI, entry point and
available captures. Distinguish native execution with instrumentation, user-mode
syscall translation, a guest machine with an OS, and a CPU-only emulated fragment.
State whether the question concerns a transformation, memory access, protocol
transition or real OS effect. Use reference-validation-emulation-execution-models.

Inspect existing artifacts first. Additional execution, attachment, resource
sharing or network access requires the relevant authorization and containment;
see playbook-validation-controlled-observation. A tool name is not an isolation
boundary. This workflow does not require a new run to close every uncertainty.

## Recover the modeled entry and the original caller separately

Identify initialized memory, register/stack inputs, runtime/TLS state, loaded
dependencies and assumed CPU features. Recover the natural caller's guards and
ownership rules. Use playbook-validation-faithful-harness for byte extents, ABI,
state reset and dependency contracts; do not substitute a guessed prototype.

For a fragment, label supplied values as captured, derived or constructed. A
decoder producing valid-looking bytes proves neither that its real caller can
reach it with those values nor that decoded code was subsequently executed.
A missing environment component can conceal a reachable bug as well as create
an artificial failure.

## Inventory hooks and substitutions that affect the conclusion

For each relevant API/instruction replacement, record inputs, output bytes,
returned status, ownership, completion timing and external effects. Separate
logging hooks from interventions. Note changed registers, omitted instructions,
fabricated handles, forced branch decisions and automatically supplied mappings.

Constructed example: a stub reports a successful read but initializes no output
buffer. A subsequent parse failure may concern the stub's impossible contract,
not the real read implementation. Conversely, an always-success allocation stub
can hide an unchecked-failure path. Do not call the resulting trace unmodified
behavior. Facts: reference-validation-binary-instrumentation-evidence.

## Bind observations to collection scope and code generation

Recover included modules, threads, event types, capture interval and exclusions.
Determine whether addresses name guest code, original native code, translated
blocks or tool helpers. Preserve address mappings and code bytes for the observed
generation, especially around unpacking, JIT replacement or self-modification.

Coverage indicates recorded control flow, not a memory-safety or authorization
verdict. A hook missed after code translation, an omitted worker thread or an
excluded library can explain absent events. With Windows persistent fuzzing,
also recover target return boundaries and input delivery using
reference-validation-winafl-execution-boundaries.

## Classify the stop before naming a target defect

Separate target exception/signal, tool or adapter failure, unsupported operation,
intentional stop, resource exhaustion and time/instruction budget. Preserve the
raw reason and distinguish a guest fault from a host emulator-process failure.
Do not silently turn missing memory into zeros or unsupported instructions into
no-ops and retain the original interpretation.

For a suspicious access, recover instruction, operands, extent, allocation/object
generation and prior state. Check whether the model omitted a legitimate mapping
or supplied invalid state. A genuine guest access violation still needs the
violated contract and reachable input path; a tool crash may remain unclassified
until target-induced corruption and an instrumentation defect are distinguished.

## Corroborate execution context without equating environments

Use available context, memory and module-inspection capabilities to recover the
selected execution, fault context, code identity and exact access. Preserve the
distinction between a Windows exception record and its saved registers; keep
core/dump coverage and symbol identity separate. The required evidence does not
depend on a particular debugger being exposed. Route through
playbook-validation-debugger-evidence for the conceptual workflow and scoped
Windows/Unix interpretation rules.

Compare the same code generation, input history and relevant state. Disappearance
under a debugger can reflect timing or environment differences; appearance only
under instrumentation does not automatically invalidate a finding. Preserve the
disagreement and the competing explanations. The first detected corruption may
be downstream of the cause: playbook-validation-first-fault-cause.

## State the supported vulnerability or malware conclusion

For a vulnerability, identify the reachable operation and violated bounds,
lifetime, initialization, state or authority rule. State which environment
assumptions are essential. A mapped-page write can still exceed an object;
successful execution does not establish absence of bugs.

For malware, connect the responsible code to input/dispatch, arguments and
observed effects. Keep capability under forced conditions separate from natural
activation and completed behavior. No payload activity in an incomplete model
does not establish benignness. Report unresolved dependency/feature gaps and the
specific evidence needed to resolve them, rather than a blanket tool-confidence
score.

## Basis and limits

Reviewed 2026-10-02. Analytical workflow grounded in the three binary-only
references above and their QEMU, Unicorn, Frida and WinAFL primary sources.
Named implementations substantiate particular mechanisms; they are not required
tools. This supplies interpretation rules, not an instrumentation script, runnable
harness or claim of target execution. Support and fidelity must be scoped to the actual
backend, architecture, OS and modeled path.
