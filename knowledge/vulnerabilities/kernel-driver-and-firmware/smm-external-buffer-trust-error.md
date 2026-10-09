---
id: vulnerability-kernel-smm-external-buffer-trust-error
title: SMM or MM external-buffer, nested-pointer and SMRAM-boundary error
kind: vulnerability
topics: [firmware, smm, management-mode, shared-memory, nested-pointer, smram]
platforms: [uefi]
architectures: [x86, x64, arm, arm64]
---

# SMM or MM external-buffer, nested-pointer and SMRAM-boundary error

## Definition and violated invariant

This vulnerability occurs when a management-mode handler trusts an external communication buffer, nested address, extent or mutable value without binding validation and use to one authorized captured representation, or permits the operation to overlap protected management storage. The invariant is that every external range must be outside protected storage, fully contained, authorized for the selected handler and stable for the values consumed.

UEFI MM communication is a generic management-mode interface; x86 SMM and SMRAM are one platform realization. A message GUID selects a route and schema, not caller trust.

## Conditions that establish the issue

Identify trigger and caller reachability, communication protocol variant, route GUID, outer buffer representation and extent, protected regions, nested pointers or offsets, copy, validation, handler operation, caller authorization and output. Prove an external value reaches a protected access or privileged effect outside the validated snapshot or permitted range.

For double fetch, identify both loads and the external writer's mutation window. Copying only the outer header does not capture nested pointees.

## Evidence that is not sufficient

An SMI, communication GUID, shared buffer, pointer field, SMRAM reference or privileged handler is not sufficient. Platform routing may restrict callers, the handler may copy and validate complete input, or hardware/firmware protections may reject overlap. A protected SMM image does not imply external buffers are trusted, and an external buffer does not imply it overlaps SMRAM.

## Investigation sequence

Resolve the handler route and request schema. Map every range in physical or virtual coordinates appropriate to that protocol, then compare it with protected memory and the declared outer extent using checked arithmetic. Trace capture, validation and later use for each nested object.

At binary level, identify dispatch tables, GUID comparisons, copy helpers and range/overflow checks. Follow mutable values into allocation, copy, MMIO and variable/update operations. Record management-mode reentrancy and nested SMI behavior where supported.

## Constructed flow

A hypothetical handler checks that external header H lies outside SMRAM, then reads `H->payload` and `H->length` twice from shared memory: once for validation and again for a privileged copy. A lower-trust caller changes them between reads to select an unchecked range.

The finding requires writable shared memory during the interval and absence of a complete captured copy or second validation. The outer non-SMRAM check alone neither proves nor refutes it.

## Primitive and impact limits

Direct effects include management-mode out-of-bounds access, arbitrary or constrained privileged read/write, state change or denial of service. SMM code execution or persistence requires controllable memory/control effects and actual execution/activation.

## Related knowledge and primary sources

`reference-smm-communication-buffer-trust` provides protocol and SMRAM distinctions. This profile retains caller, route, range and mutable-copy evidence locally.

Reviewed 2026-10-09 against PI 1.9 [MM communication protocols](https://uefi.org/specs/PI/1.9/V4_UEFI_Protocols.html), the [EDK II Secure Coding Guide](https://tianocore-docs.github.io/EDK_II_Secure_Coding_Guide/draft/secure_coding_guidelines_general.html) and TianoCore [SMM memory protection](https://tianocore-docs.github.io/ATBB-Memory_Protection_in_UEFI_BIOS/draft/memory-protection-in-SMM.html). The flow is hypothetical; target SMRAM maps and routes require platform evidence.
