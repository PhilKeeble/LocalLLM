---
id: vulnerability-kernel-hypervisor-device-model-coordinate-validation-error
title: Hypervisor device-model MMIO or PIO coordinate validation error
kind: vulnerability
topics: [virtualization, hypervisor, device-model, mmio, pio, guest-host]
platforms: [cross-platform, virtualization]
architectures: [any]
---

# Hypervisor device-model MMIO or PIO coordinate validation error

## Definition and violated invariant

This vulnerability occurs when a virtual device model decodes a guest MMIO/PIO access, register value or descriptor using the wrong address space, width, extent or device state and reaches host objects outside the modeled operation. The invariant is that guest-controlled coordinates must be translated and validated in the selected virtual device before they influence host memory, I/O or privileged operations.

A guest physical address is not a host pointer. Emulated, paravirtualized, accelerated and passed-through devices can use different paths and trust boundaries.

## Conditions that establish the issue

Identify guest actor, selected device instance, MMIO/PIO region, access width and offset, register semantics, guest or device address, translation result, host backing object and final operation. Prove guest-controlled input escapes the modeled register/buffer extent or selects a host operation the guest should not control.

Include device state, feature negotiation, reset and migration because the same offset can have different meaning by mode. For descriptor-based devices, join register writes to the eventual ring and DMA consumer.

## Evidence that is not sufficient

An MMIO callback, guest crash, host pointer arithmetic, unknown register or failed transaction is not sufficient. The region framework may bound offsets, the callback may reject widths, and a fault returned to the guest may be correct behavior. A host process crash supports availability impact only after reachability and containment are established.

Do not claim guest-to-host escape from corruption confined to guest-assigned memory.

## Investigation sequence

Trace address decoding from guest instruction or request through virtual bus routing to the exact callback. Preserve guest virtual, guest physical/device and host coordinates separately. Recover size, endianness, alignment, device mode and every check before host access.

At binary level, map callback tables, register switches, masks and translations. Follow values into allocation, copy, DMA and host API calls. Determine whether a userspace device-model process, kernel module or hypervisor executes the effect and what authority it holds.

## Constructed flow

A hypothetical virtual device exposes a 256-byte MMIO register window. Its write callback uses guest offset `off` as an index into a 32-entry host array of eight-byte entries but checks only `off < 256`, then accesses `array[off]`. Offsets 32 through 255 pass the byte-range check yet exceed the element index domain.

The example is constructed; real frameworks may supply byte offsets and widths differently. Establish the callback contract before applying the unit mismatch.

## Primitive and impact limits

The direct primitive can be host-process out-of-bounds access, unintended host I/O, wrong virtual-device state or denial of service. Guest-to-host code execution requires a controllable host primitive, device-model authority and mitigation analysis; a guest-visible error is not an escape.

## Related knowledge and primary sources

`reference-virtual-device-ring-dma` provides the address-space distinction. This profile keeps guest reachability, device selection and host effect explicit.

Reviewed 2026-10-09 against QEMU's [memory API](https://www.qemu.org/docs/master/devel/memory.html), [memory-region operations](https://www.qemu.org/docs/master/devel/memory.html#memory-region-operations) and [MITRE CWE-119](https://cwe.mitre.org/data/definitions/119.html). The flow is hypothetical and does not describe a QEMU defect.
