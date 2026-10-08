---
id: playbook-specialist-side-channel-review
title: Review side-channel claims against hardware scope and observation limits
kind: playbook
topics: [side-channels, microarchitecture, timing, threat-models, evidence, uncertainty]
platforms: [linux, windows, macos, freebsd, android, embedded]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Side-channel claim review

## State the protected information and observer boundary

Identify the claimed protected value, operation and observer's actual access.
Record processor, environment, resource sharing and scheduling assumptions. Keep
architectural behavior, possible internal effects and observed information
separate. A proposed mechanism is not a demonstrated disclosure.

Facts: reference-microarchitecture-side-channel-evidence. Use a hardware-specific
contract for applicability; architectural correctness alone does not describe
every internal effect or establish that an observer can distinguish it.

## Evaluate existing measurements with their collection scope

For supplied measurements, record event, units, clock/observer, input classes,
sample scope, uncertainty and changed conditions. Assess public-input variation,
scheduling, I/O and measurement overhead as alternative explanations where
relevant. Do not manufacture missing samples or convert a static pattern into
measured reliability.

Determine whether the evidence relates to protected information across the
claimed boundary, rather than merely showing different workloads take different
time. This review does not prescribe attack execution or data-recovery techniques.

## Match mitigations to the actual mechanism and deployment

Recover hardware support, firmware/OS policy, transitions and application behavior
for the claimed channel. Separate a mitigation present in code from its deployment
and coverage. reference-crypto-timing-comparison-evidence supplies comparison-
specific limits; it is not a complete system-side-channel assurance.

Report supported observations, inference, competing explanations and unknown
coverage. A named instruction or configuration does not prove all processors or
all unrelated channels are protected.

## Review basis

Reviewed 2026-10-08 against reference-microarchitecture-side-channel-evidence
and reference-crypto-timing-comparison-evidence. Hardware prerequisites remain
local to their sources. This is a conceptual evidence-review workflow, not a
benchmark, exploit procedure or claim of reproduced information leakage.
