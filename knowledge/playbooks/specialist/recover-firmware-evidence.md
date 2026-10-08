---
id: playbook-specialist-firmware-evidence
title: Recover firmware component selection, execution context and trust evidence
kind: playbook
topics: [firmware, bare-metal, rtos, uefi, smm, boot-chains, evidence]
platforms: [embedded, uefi]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---
# Firmware investigation order

## Preserve image ancestry and candidate execution coordinates

Record acquisition identity, container/partition/volume origin and each derived
component's extent and transformation. Separate stored, decompressed and loaded
coordinates; establish architecture and instruction state before following code.
Require multiple consistent facts for a candidate base/map rather than one
plausible pointer. Keep unselected or unresolved components explicit.

Fact routes: reference-firmware-container-component-evidence and
reference-bare-metal-address-vector-mmio. A component found in a package is not
proof the device installed or executed it.

## Establish startup, task, interrupt and device roles

Connect the supported entry/vector to startup initialization and selected code.
For an RTOS, identify task entries, queues, item representations, ownership and
interrupt-to-task handoffs. For MMIO/DMA, require the target hardware contract
and observable result; an address or write alone does not establish an effect.

Use reference-rtos-task-queue-ownership for its scoped FreeRTOS examples. Preserve
the actual kernel/port and scheduling configuration. A notification or ready task
does not establish input consumption or completion.

## Bind boot and update acceptance to the component consumed

Recover each stage's policy/key authority, verified extent, selected slot/component
and transfer of control. Keep freshness/rollback and recovery policy distinct from
signature validity. Record staging, validation, activation request and boot identity
as separate outcomes. Missing execution evidence remains missing.

Facts: reference-firmware-boot-trust-recovery and
reference-uefi-image-service-variable-capsule. A UEFI capsule/variable alone does
not establish authentication, successful installation or malicious persistence.

## Recover SMM request scope before interpreting privileged effects

Identify the actual communication protocol, route, operation, buffer extent and
pointer representation. Recover validations on nested regions and the bytes
actually consumed, including mutable aliases or trusted copies. Bind operation
authorization, error handling and resulting state to that request.

Facts: reference-smm-communication-buffer-trust. Document a supported violated
condition or confirmed behavior, keeping hardware protection assumptions local.
Do not equate a privileged handler, signature or suspicious name with a verdict.

## Review evidence completeness without changing the target

The output should name artifact/component, map, entry/context, input, relevant
rule, observed result and remaining uncertainty. Source contracts explain what
to look for; they do not substitute for target evidence. This workflow requires
no prescribed tool, firmware execution, flashing or configuration change.

Reviewed 2026-10-08 against the five references named above and
reference-rtos-task-queue-ownership. Scope and primary provenance stay with their
facts. Behavior reporting: reference-malware-indicator-provenance.
