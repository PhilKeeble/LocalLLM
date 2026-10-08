---
id: reference-virtual-device-ring-dma
title: Virtual device requests, virtqueues, address spaces and DMA ownership
kind: reference
topics: [virtualization, hypervisors, device-models, virtio, rings, descriptors, dma]
platforms: [linux, windows, freebsd, embedded]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Guest and device-model evidence

## A guest device address is not a host pointer

QEMU's memory API models RAM, MMIO and routed regions in address spaces. MMIO
reads/writes invoke device callbacks; address-space transactions can fail, including
for rejected accesses or IOMMU faults. [1]

Recover guest virtual, guest physical/device and host representation separately.
Bind a request to its selected device, address space, translation and accessible
extent. One successful mapping does not prove another address or later mapping
valid. Emulation, accelerated virtualization and device assignment use different
paths; these QEMU concepts do not establish every hypervisor's implementation or
prove that an apparent guest failure affected host memory.

## Virtio descriptor direction is defined from the device's perspective

Virtio descriptor chains describe device-readable and device-writable buffers.
Split queues have descriptor, available and used areas; packed queues have a
different ownership/availability representation. Negotiated features affect
permitted queue behavior. [2]

Identify format/features before labeling indices, ownership bits or direction.
Recover each buffer's translated extent and request schema; the descriptor's
direction does not authorize arbitrary guest-selected operations. A valid ring
entry is not semantic validation of its payload. Do not apply split-ring layout
or completion fields to packed or unrelated proprietary rings.

## Virtqueue publication, notification and consumption are separate events

Virtio specifies ordering between descriptor data and publishing availability,
and between output data and publishing use. For a modern split queue, used len
limits the device-written bytes the driver may assume valid. Device consumption
need not follow submission order unless the relevant ordering feature applies. [2]

Correlate queue generation, entry, publication and returned completion. A doorbell
or notification is not proof every request finished. Reset and reused indices
need their actual protocol before being matched to old work. Preserve legacy/
device-specific exceptions; no universal used-length rule for every transport.

## DMA coherency does not prove ordering or buffer lifetime

Linux's DMA guide distinguishes CPU addresses from device DMA addresses and
coherent from streaming mappings. Coherent storage still requires appropriate
ordering; streaming mappings have synchronization/ownership requirements. [3]

Recover translation, mapping extent/direction, retained storage, device use and
completion before unmapping or reuse. An IOMMU mapping constrains a device's
address access according to its configuration; it does not parse a command or
freeze mutable request bytes. Keep mapping success, operation completion and
host/guest trust conclusions separate. Workflow: playbook-specialist-device-work.

## Sources and scope

Reviewed 2026-10-08. No guest escape procedure, device-specific opcode layout or
assumed hypervisor isolation policy is imported.

1. [QEMU memory API](https://www.qemu.org/docs/master/devel/memory.html): rolling master, region types, MMIO Operations and address_space_rw results.
2. [Virtio 1.2](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html): sections 2.7-2.8, buffer direction, split/packed queues, publication and used-buffer semantics.
3. [Linux DMA guide](https://kernel.org/doc/html/next/core-api/dma-api-howto.html): rolling next, CPU/DMA addresses, mapping types and memory-barrier caveat.
