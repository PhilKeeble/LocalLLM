---
id: pe-static-triage
title: PE static triage for vulnerability identification and malware analysis
kind: playbook
topics: [pe, reverse-engineering, static-analysis, triage, vulnerability-analysis, malware-analysis]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# PE reversing workflow
This playbook describes HOW to investigate. Technical encodings live in the pe-headers-sections reference.

Reviewed 2026-10-02. This is an investigation method, not a malware classifier
or a claim that static analysis resolves every runtime-dependent behavior.

## Scope and specimen
Record the input path, length, hash, tool version and whether the artifact is a disk image or memory dump. Preserve original bytes. Do not execute a specimen in a static-only investigation; request a permitted isolated dynamic workflow if runtime evidence is necessary.

## Evidence ledger
Validate headers and collect the complete section table before interpreting it. Retain raw fields and coordinates with every finding. Distinguish file offsets, RVAs and runtime VAs. Separate observation, inference and unknowns; names and entropy alone do not establish behavior or maliciousness.

## Follow the question
For permissions, identify the field/API, full value and whether bits were masked before decoding. For address mapping, prove byte-range bounds. For import/export questions inspect descriptors, thunks, forwarders and callers. For initialization inspect entry-point and TLS evidence. Choose a small sequence of evidence-producing operations rather than dumping every report.

## Vulnerability triage: controlled input, check and sensitive operation

Identify what an external actor controls, the entry point accepting it and the
operation whose contract may be violated. A sink is that consuming operation:
for example, a copy, allocation, file access or privileged request. Record the
same value's width, units, checks and use; do not connect unrelated size fields
just because a decompiler gives them similar names.

Establish the violated condition, such as buffer capacity, object lifetime or
caller authorization, and the feasible path to it. A suspicious API or missing
mitigation is not the defect itself. Continue with playbook-re-sensitive-data-flow.

## Malware triage: entry, configuration, dispatch and effects

Trace a candidate behavior from an entry or callback through its enabling
conditions to the actual operation and arguments. For a network indicator,
separate an embedded string, a decoded destination and a destination passed to a
communication routine. For process, file or configuration changes, identify the
affected object, requested action and caller context.

Record evidence of capability separately from observed execution and malicious
intent. Unused code, error paths and benign administrative uses can explain
powerful APIs. An unexplained high-entropy region or unusual section name is a
lead, not proof of packing or maliciousness. Do not execute an unknown specimen
to fill an evidence gap in a static-only task.

## Route a malware behavior question to its focused evidence workflow

After identifying a supported lead in the specimen, use the workflow for the
missing relation rather than treating its mechanism as a verdict:

- Retained configuration to later activation: playbook-malware-persistence-evidence.
- Suspicious memory to code provenance and execution: playbook-malware-code-provenance.
- Configuration or received command to communication/data transfer: playbook-malware-communication-data-flow.
- Packed content, obscured dispatch or environmental selection: playbook-malware-obscured-behavior.
- Behavior and indicator claims with local qualifications: playbook-malware-behavior-reporting.

These routes do not establish that the lead is malicious or authorize specimen
execution. Keep static capability, observed effect and interpretation separate.

## Resolve disk versus memory discrepancies before claiming concealment

Keep image declarations, mapped bytes, current permissions and executed control
flow separate. When a dump differs from disk, account for the relevant loader
transformations and known instrumentation before classifying a change. A missing
capture range is unknown, not proof that bytes were erased.

Use format-disk-versus-loaded-image for comparison rules and
format-debug-information-build-matching for symbol identity. Do not let a guessed
function name or mismatched PDB determine a behavior or vulnerability conclusion.

## Handoff and reporting
Answer with supporting coordinates, uncertainty and one next verification step. Separate declared disk properties from observed runtime state. Use this local format for numeric findings: Permission audit: domain | raw value | flags | access | evidence/caveat. Do not turn an ambiguous number into a confident access claim.
