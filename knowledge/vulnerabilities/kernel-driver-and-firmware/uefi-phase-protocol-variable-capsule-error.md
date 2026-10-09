---
id: vulnerability-kernel-uefi-phase-protocol-variable-capsule-error
title: UEFI service-phase, protocol, variable or capsule validation error
kind: vulnerability
topics: [firmware, uefi, boot-services, protocols, variables, capsules]
platforms: [uefi]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# UEFI service-phase, protocol, variable or capsule validation error

## Definition and violated invariant

This vulnerability occurs when UEFI code uses a service or protocol outside its valid phase or lifetime, resolves the wrong GUID/interface instance, misbinds a variable's name/GUID/attributes/policy, or accepts a capsule with invalid extent, format or update authority. The invariant is that interface identity, phase, object extent and authorization must remain valid through the operation and any deferred activation.

Successful `ExitBootServices` terminates boot services; runtime services have a separate contract. A protocol GUID identifies an interface type, not caller trust, and capsule submission is not proof of installation or execution.

## Conditions that establish the issue

Identify current UEFI phase, exact service table or protocol instance, handle and agent, interface lifetime, variable name/vendor GUID/attributes, capsule GUID/header and complete size, caller authority, selected consumer and result. Prove attacker-controlled input reaches an invalid interface use, protected variable change, out-of-range parse or unauthorized update transition.

Include a failed first `ExitBootServices` attempt, because firmware may already begin shutdown and the specification restricts subsequent boot-service use. For deferred capsules, follow reset, processing and reported status.

## Evidence that is not sufficient

A GUID constant, retained function pointer, variable name, capsule header, boot-service import or submission success is not sufficient. The interface may remain valid in phase, the variable may be read-only to that caller, the capsule may be rejected later or the stored object may never activate.

Do not assume familiar variable names under different vendor GUIDs identify the same object or policy.

## Investigation sequence

Build a phase timeline from image entry through boot-service exit and runtime. Resolve each indirect call to its table or protocol layout and handle instance. Track protocol open/close/uninstall lifetime. For variables and capsules, parse every identity, attribute and length and follow policy through the final consumer.

At binary level, recover EFI status handling and `UINTN` widths for the target architecture. A successful lookup must still be joined to a non-null interface and correct function slot. Trace capsule `HeaderSize` and `CapsuleImageSize` with checked containment.

## Constructed phase example

A hypothetical loader saves a boot-service protocol pointer, successfully calls `ExitBootServices`, then invokes the saved method during runtime. The pointer value may still reference mapped bytes, but the boot-service interface contract has ended. The finding requires actual post-transition execution and no separate runtime protocol guarantee.

## Primitive and impact limits

Direct effects include stale code/data access, firmware memory corruption, unauthorized variable or update state and boot failure. Persistent firmware execution requires controlled installed bytes and later activation; a malformed capsule rejected without effect supports no such conclusion.

## Related knowledge and primary sources

`reference-uefi-image-service-variable-capsule` provides interface facts. This profile keeps phase, object identity and consumer result together.

Reviewed 2026-10-09 against UEFI 2.10 [boot services](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html), [runtime services](https://uefi.org/specs/UEFI/2.10/08_Services_Runtime_Services.html) and PI [protocol definitions](https://uefi.org/specs/PI/1.9/V4_UEFI_Protocols.html). The example is hypothetical.
