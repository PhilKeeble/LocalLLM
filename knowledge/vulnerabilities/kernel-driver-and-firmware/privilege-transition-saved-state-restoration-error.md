---
id: vulnerability-kernel-privilege-transition-saved-state-restoration-error
title: Privilege-transition saved-state validation or restoration error
kind: vulnerability
topics: [kernel, privilege-transition, exception-return, saved-context, hypervisor, signal]
platforms: [cross-platform, kernel, virtualization, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# Privilege-transition saved-state validation or restoration error

## Definition and violated invariant

This vulnerability occurs when a syscall, interrupt, exception, signal, hypercall or return path restores a program counter, stack, processor mode, flags, segments, address-space state or register context influenced by a less-trusted actor without the checks required for the destination privilege. The invariant is that the saved frame and return instruction must produce only a permitted execution context for that caller and transition.

Architectural return instructions apply specific transformations and checks, but software can still construct or select the wrong saved state. User signal frames, guest virtual-CPU state and secure-world contexts have distinct trust and ABI rules.

## Conditions that establish the issue

Identify entry and origin privilege, saved-frame storage and owner, fields externally controllable, copy/parse path, return instruction, architectural masks and checks, destination privilege/address space and restored interrupt or extension state. Prove lower-trust input survives to an unauthorized return target, mode, permission or context.

Include nested exceptions, error paths and partial restores. For guest state, distinguish guest privilege from host privilege and determine which fields hardware virtualizes or validates.

## Evidence that is not sufficient

An `iret`, `eret`, `sret`, `mret`, signal return, context-copy loop or user-writable frame is not sufficient. The architecture or kernel may mask flags, constrain selectors, canonicalize addresses and force the destination privilege. A crash on return does not prove elevation.

Do not infer register preservation from a generic calling convention when the transition uses an exception or hypervisor ABI.

## Investigation sequence

Build a field table for the saved context: source, validation, transformation, architectural consumption and resulting authority. Trace frame pointers and lengths across address spaces. Recover current control registers and return mode that determine how the instruction interprets each field.

At binary level, locate the final frame loads and return instruction, then work backward through masks, range checks and selectors. Follow all alternate fast/slow and compat return paths. Check ordering of address-space switch, stack switch and interrupt enable relative to validation.

## Constructed flow

A hypothetical hypervisor copies a guest-provided virtual-CPU frame into a host exception frame and validates only the return address, not the saved privilege/mode field. If the final architectural return can consume that field as host privilege state, a guest may select an unauthorized mode.

The example is intentionally generic. It is refuted when hardware ignores or constrains the field, the frame is actually guest-only state, or another path masks it before return.

## Primitive and impact limits

Direct effects include control-flow redirection, restored execution under wrong privilege, interrupt-state corruption, cross-context leakage or denial of service. Elevation requires an actual higher-authority destination; restoring attacker-controlled state within the same constrained guest or process is not automatically an escape.

## Related knowledge and primary sources

Calling-convention and architecture references determine frame fields and return checks. This profile keeps less-trusted influence and resulting privilege together.

Reviewed 2026-10-09 against RISC-V privileged [trap-return semantics](https://docs.riscv.org/reference/isa/priv/machine.html#machine-trap-return-instructions), RISC-V [hypervisor trap return](https://docs.riscv.org/reference/isa/priv/hypervisor.html#_trap_return), Arm [exception model guidance](https://developer.arm.com/documentation/102412/latest/) and the [Intel Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html). The flow is hypothetical; exact checks are architecture- and mode-specific.
