---
id: reference-bare-metal-address-vector-mmio
title: Bare-metal image bases, startup vectors, interrupts and MMIO evidence
kind: reference
topics: [firmware, bare-metal, memory-maps, image-bases, vectors, interrupts, mmio]
platforms: [embedded, linux]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---
# Bare-metal execution coordinates

## Load address and run address can describe different copies

GNU linker terminology distinguishes a section's load memory address (LMA) from
its run address (VMA). ROM-initialized data copied into RAM is one documented
reason they differ. [1]

Recover storage offsets, mapped regions, startup copies and consumer addresses
separately. A raw image has no universal load base, and choosing a base that makes
some pointers plausible does not prove the complete map. Require agreement with
entry/vector evidence, references and the board's documented memory regions.
VMA is linker terminology here; it does not imply an MMU is enabled.

## Cortex-M startup vectors are scoped entry evidence

The CMSIS Cortex-M startup example begins its vector table with the initial stack
pointer and Reset_Handler, followed by exception and device interrupt handlers.
The example uses weak default handlers and calls system initialization before
the application runtime entry. [2]

For a Cortex-M candidate, correlate table, executable handler addresses, stack
region and startup control flow. Shared default handlers are not evidence all
peripherals have equivalent behavior. The table's placement, active mapping and
device interrupt set require target evidence. This Cortex-M pattern must not be
applied to AArch64, x86 or every other bare-metal architecture.

## MMIO addresses name device transactions rather than ordinary RAM

In Linux's device-I/O contract, mapped device accesses have architecture/bus
semantics; some writes are posted, so CPU-side completion can precede arrival
at the device. Non-posted delivery and CPU ordering are distinct properties. [3]

For bare-metal investigation, use the actual processor, board and peripheral
contract to interpret width, register meaning and access effects. A repeated read
may be polling device state rather than traversing memory. An observed store is
not proof the peripheral completed the requested operation. Linux's mapping API
is a scoped illustration, not a bare-metal API requirement or universal timing rule.

## Interrupt handlers need their actual activation and shared-state context

CMSIS startup vectors identify handler entries, including defaults. [2] A handler
candidate does not establish that its interrupt was enabled, routed or delivered.
Recover the target interrupt controller, source acknowledgement, task/main-loop
handoff and storage shared with those consumers.

Keep CPU-local interrupt masking, multicore concurrency and DMA users separate;
the target contract determines what each operation excludes. A flat executable
without process boundaries does not prove absence of interrupts or asynchronous
device activity. Workflow: playbook-specialist-firmware-evidence.

## Sources and scope

Reviewed 2026-10-08. No universal vector base, peripheral addresses or interrupt
priority convention. Target manuals are needed for hardware-specific meanings.

1. [GNU ld basic script concepts](https://www.sourceware.org/binutils/docs/ld/Basic-Script-Concepts.html): VMA/LMA distinction, rolling manual.
2. [CMSIS-Core startup file](https://arm-software.github.io/CMSIS_5/Core/html/startup_c_pg.html): Cortex-M vector and reset examples, CMSIS 5 documentation.
3. [Linux device I/O](https://docs.kernel.org/driver-api/device-io.html): posted/non-posted mappings and ordering, rolling upstream.
