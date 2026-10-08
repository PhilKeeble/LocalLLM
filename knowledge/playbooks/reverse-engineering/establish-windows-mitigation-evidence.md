---
id: playbook-re-windows-mitigation-evidence
title: Establish Windows mitigation declarations, runtime enforcement and defect impact
kind: playbook
topics: [windows, reverse-engineering, mitigations, dep, aslr, cfg, cet]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Establish which mitigation applies to the actual failing operation

Do not replace a defect investigation with a mitigation checklist. Preserve
image identity, architecture, process policy and the actual operation separately.
State whether evidence shows a declaration, measured setting, observed enforcement
or only a hypothesis. CET details below are scoped by the x64 reference.

## Identify every relevant module and the target process instance
Reviewed 2026-10-02. Record hashes, machine types, loaded bases, OS/build,
process generation and compiler/runtime clues. Recover image declarations and
bounded tables from the relevant headers and load configuration. Parse debug-entry
extended characteristics separately from optional-header DllCharacteristics.

Map the suspect instruction to the exact loaded module. Account for mixed
instrumented/uninstrumented libraries, plugins and generated code. A trusted
main EXE's flags do not establish another module's call-site coverage. Retain
file and live coordinates using the format/loader references.

## Distinguish measured policy from stored configuration
Runtime-policy evidence needs a target process instance, observation time,
successful acquisition and the meaning of every relevant field. For Windows
GetProcessMitigationPolicy results, preserve the selector, structure, byte size
and success/error; unsupported or failed queries leave the policy unknown.
A helper's self-query does not measure the target. Interpreting available policy
evidence requires no policy mutation; see reference-windows-dep-aslr-policy.

For DEP, compare the fault's access type with page permissions. For ASLR,
separate preferred base, observed placement, force-relocation and randomization
settings. For CFG, retain strict/export-suppression and dynamic-target evidence.
For shadow stacks, distinguish compatibility, strict, audit and image-admission
policy. Current configuration alone may describe a future process launch.

## Connect the mitigation to the exact control or data operation
For an indirect call, identify its instrumentation and destination state using
reference-windows-cfg-instrumentation-targets. For returns/context restoration,
use reference-windows-cet-shadow-stack with hardware/platform scope. For dynamic
code distinguish requested memory protection from a successful policy-permitted
transition and actual CFG registration.

Constructed evidence table for a report: a bounds-violating write is established;
DEP is enabled; the later execute attempt faults. The write is still a defect,
and the observed execute path was blocked. Neither fact establishes arbitrary
code execution. Similarly, no mitigation event is expected merely because an
authorized-code path used a corrupted authorization field.

## A blocked operation does not establish that all harmful effects were blocked

For Windows malware analysis, separate the operation stopped by a mitigation from
earlier or alternative effects established by evidence. Memory-corruption defenses
do not by themselves establish whether a program used ordinary permitted APIs to
read data, modify files or communicate. Recover the actual authority, targets,
results and continuation; mitigation flags and powerful imports alone establish
neither benign behavior nor malicious execution.

For vulnerability analysis, preserve the defect even if one consequence was
prevented. A fail-fast record identifies termination and its reported reason,
not automatically the initiating bug. Use reference-windows-seh-vectored-handlers
and playbook-validation-first-fault-cause before classifying the causal chain.

## Resolve uncertainty with scoped observations, not weakened protection
Keep failed queries, missing dumps, unsupported hardware and unknown deployment
settings explicit. If further execution is necessary, use an authorized isolated
test environment and reproduce the relevant policy. Do not disable host
mitigations, alter application IFEO settings or restart another running service
just to obtain a desired result.

Report defect evidence separately from constraints on impact. An enabled flag
does not prove an unexploitable program; an absent flag does not prove an
exploitable bug. Label a policy snapshot, debugger trace or arithmetic model
according to what it actually demonstrates, not as a mitigation-bypass test.

## Source basis
Workflow synthesis reviewed 2026-10-02.

- [Policy query contract](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocessmitigationpolicy).
- [Compiler and linker CFG stages](https://learn.microsoft.com/en-us/cpp/build/reference/guard-enable-control-flow-guard?view=msvc-170).
- [Shadow-stack policy distinctions](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_user_shadow_stack_policy).
