---
id: vulnerability-kernel-iommu-guest-memory-mapping-scope-failure
title: IOMMU or guest-memory translation scope and lifetime failure
kind: vulnerability
topics: [virtualization, iommu, guest-memory, dma, mapping, isolation]
platforms: [cross-platform, virtualization]
architectures: [any]
---

# IOMMU or guest-memory translation scope and lifetime failure

## Definition and violated invariant

This vulnerability occurs when device or guest-memory translation maps the wrong physical backing, permissions, owner or lifetime, allowing access outside the intended guest, process or device domain. The invariant is that every device-visible address resolves through the correct translation context to authorized live pages with the required read/write scope until completion and no longer.

An IOMMU limits device access according to configured mappings; it does not validate command semantics, prevent all side channels or make a mutable buffer immutable.

## Conditions that establish the issue

Identify requester/device identity, IOMMU domain or guest-memory context, input address and length, page mappings, permissions, ownership, pinning, invalidation, device completion and reuse. Prove an access resolves to unauthorized backing, survives unmap/reassignment, exceeds the mapped extent or uses stale translation state.

For shared or mediated devices, recover which context selects the domain on each submission. Include address-space identifiers, process address-space bindings and reset paths where supported by the target.

## Evidence that is not sufficient

An IOMMU API, identity mapping, shared device, translation fault or guest physical address is not sufficient. The mapping may be deliberate and restricted by another layer, or the fault may prevent access. Equal numeric addresses in different domains do not identify equal backing.

Do not infer a bypass from stale-looking page-table memory without proving hardware can still use it after required invalidation and ordering.

## Investigation sequence

Trace `device-visible address -> translation domain -> page-table entry -> physical backing -> owner`. Compare the full range and permissions, including page rounding and aliases. Mark map, publish, invalidate, completion, unmap and page reuse in order.

At binary level, follow domain selection, map/unmap helpers and invalidation waits rather than assuming private table layouts. Determine whether errors are propagated before descriptors become visible and whether reset drains outstanding transactions.

## Constructed timeline

A hypothetical mediated device maps tenant A's pages into a device domain, submits DMA and unmaps immediately after queueing. The host reallocates those pages to tenant B before the device completes, while stale translation remains usable. A later write crosses tenants.

The finding requires that unmap does not itself wait for or cancel the outstanding access and that translation invalidation and page reuse can overlap. A retained pin and completion fence refute it.

## Primitive and impact limits

Direct effects include device read/write outside the intended domain, cross-tenant disclosure, corruption or denial of service. Host code execution requires address/value control and a viable target; a mapping fault alone supports no such claim.

## Related knowledge and primary sources

DMA and ring profiles provide publication and completion contracts. This profile owns translation domain, backing identity and invalidation lifetime.

Reviewed 2026-10-09 against Linux kernel [IOMMU subsystem documentation](https://docs.kernel.org/driver-api/iommu.html), Linux [VFIO documentation](https://docs.kernel.org/driver-api/vfio.html) and the [Virtio IOMMU specification](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html#x1-3150006). The timeline is constructed; hardware invalidation guarantees are target-specific.
