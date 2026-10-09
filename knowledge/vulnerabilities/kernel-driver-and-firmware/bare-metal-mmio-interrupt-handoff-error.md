---
id: vulnerability-kernel-bare-metal-mmio-interrupt-handoff-error
title: Bare-metal MMIO width, ordering, side-effect or interrupt-handoff error
kind: vulnerability
topics: [firmware, embedded, mmio, interrupts, memory-ordering, device-registers]
platforms: [embedded, firmware]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---

# Bare-metal MMIO width, ordering, side-effect or interrupt-handoff error

## Definition and violated invariant

This vulnerability occurs when firmware accesses a memory-mapped device register with an unsupported width, offset, order or repetition, misunderstands read/write side effects, or hands interrupt-produced state to another context without the required ownership and ordering. The invariant is defined by the processor, bus and peripheral contract, not ordinary RAM semantics.

Some device writes are posted, reads can clear status and register widths can select different transactions. `volatile` affects compiler access behavior but is not a universal hardware memory barrier or atomic handoff.

## Conditions that establish the issue

Identify mapped peripheral and register, bus address, supported widths/alignment, access direction and side effects, required ordering/barriers, interrupt source/acknowledgment, shared buffer and consumer. Prove attacker-influenced device/input state reaches an invalid transaction or the consumer observes incomplete, stale or multiply processed state.

Include DMA and multicore actors; disabling local interrupts does not serialize another core or device.

## Evidence that is not sufficient

A load/store to a fixed address, `volatile` pointer, polling loop, barrier or interrupt handler is not sufficient. The access may be exactly required by the device, mapping attributes may supply ordering, and repeated reads may intentionally poll. A handler symbol does not prove the interrupt is enabled or routed.

Do not assign register meaning from a similar device revision without target documentation.

## Investigation sequence

Map each fixed address to the target memory map and register definition. Annotate width, alignment, read/write effect and required sequence. Follow CPU ordering primitives, posted-write flushes and acknowledgment. Draw the interrupt-to-task handoff with buffer ownership, sequence counters and barriers.

At binary level, preserve load/store width and barrier instructions. Determine whether a readback is a flush, status observation or destructive read. Check every reset and power transition because register state and mapping can change.

## Constructed sequence

A hypothetical peripheral requires payload stores to a shared buffer, a release barrier, then a doorbell write. Firmware writes the doorbell first and fills the buffer afterward. A device may fetch stale payload if the interconnect observes the notification before data publication.

The sequence is vulnerable only under the target's ordering and device-fetch contract; a strongly ordered mapping or implicit device rule can change the conclusion.

## Primitive and impact limits

Direct effects include wrong device operation, stale/corrupted data, repeated interrupt, lost event or denial of service. Arbitrary memory access requires device capabilities and controlled address/data beyond the ordering defect.

## Related knowledge and primary sources

`reference-bare-metal-address-vector-mmio` provides mapping and interrupt scope. This profile keeps target register semantics and handoff ordering together.

Reviewed 2026-10-09 against Linux kernel [device I/O documentation](https://docs.kernel.org/driver-api/device-io.html), Arm [CMSIS-Core register access guidance](https://arm-software.github.io/CMSIS_6/latest/Core/index.html) and RISC-V [I/O ordering discussion](https://docs.riscv.org/reference/isa/unpriv/mm-eplan.html). The sequence is hypothetical; target manuals remain authoritative.
