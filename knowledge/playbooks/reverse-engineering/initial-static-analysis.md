---
id: pe-static-triage
title: PE reversing workflow and evidence standards
kind: playbook
topics: [pe, reverse-engineering, static-analysis, triage]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# PE reversing workflow
This playbook describes HOW to investigate. Technical encodings live in the pe-headers-sections reference.

## Scope and specimen
Record the input path, length, hash, tool version and whether the artifact is a disk image or memory dump. Preserve original bytes. Do not execute a specimen in a static-only investigation; request a permitted isolated dynamic workflow if runtime evidence is necessary.

## Evidence ledger
Validate headers and collect the complete section table before interpreting it. Retain raw fields and coordinates with every finding. Distinguish file offsets, RVAs and runtime VAs. Separate observation, inference and unknowns; names and entropy alone do not establish behavior or maliciousness.

## Follow the question
For permissions, identify the field/API, full value and whether bits were masked before decoding. For address mapping, prove byte-range bounds. For import/export questions inspect descriptors, thunks, forwarders and callers. For initialization inspect entry-point and TLS evidence. Choose a small sequence of evidence-producing operations rather than dumping every report.

## Handoff and reporting
Answer with supporting coordinates, uncertainty and one next verification step. Separate declared disk properties from observed runtime state. Use this local format for numeric findings: Permission audit: domain | raw value | flags | access | evidence/caveat. Do not turn an ambiguous number into a confident access claim.

Reusable lessons are reviewed outside Pi. A session record is evidence for that review, not authority to update the library.
