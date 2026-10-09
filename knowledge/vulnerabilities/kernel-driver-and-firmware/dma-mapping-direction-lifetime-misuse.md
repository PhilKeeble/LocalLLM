---
id: vulnerability-kernel-dma-mapping-direction-lifetime-misuse
title: DMA address, extent, direction, coherency or completion misuse
kind: vulnerability
topics: [kernel, drivers, dma, iommu, coherency, lifetime]
platforms: [cross-platform, linux, windows, embedded]
architectures: [any]
---

# DMA address, extent, direction, coherency or completion misuse

## Definition and violated invariant

This vulnerability occurs when software gives a device the wrong DMA address, range, access direction or synchronization state, or releases/reuses the mapping before device completion. The invariant is that the device-visible mapping must cover only the intended live buffer with permissions and ownership matching every device access until a proven terminal completion.

A CPU virtual address, physical address and device DMA address are different coordinate systems. Coherent allocation means CPU/device visibility follows that API's coherency contract; it does not eliminate command ordering or lifetime requirements.

## Conditions that establish the issue

Identify the allocating owner, CPU buffer, mapped device address, byte extent, direction, device/domain, synchronization operations, descriptor publication, completion and unmap/free. Show a reachable device access falls outside the mapping, violates direction/ownership, observes stale data, or continues after reuse.

For streaming mappings, recover every CPU-to-device and device-to-CPU ownership transition. For scatter/gather, use mapped segments returned by the mapping API rather than assuming the original entries or count remain device-ready.

## Evidence that is not sufficient

A DMA API, physical-looking address, missing cache operation or early request completion is not sufficient. The platform may provide coherent memory, an owning object may retain the mapping, or another fence may prove completion. A valid IOMMU mapping does not validate the device command or freeze buffer contents.

Do not infer arbitrary memory access without showing device control over address, extent, direction and reachable submission.

## Investigation sequence

Track addresses in separate CPU-virtual, physical and device domains. Annotate map result, returned segment count, direction and size. Follow stores to descriptors, publication barriers, doorbells, device reads/writes, completion barriers and cleanup. Include reset, timeout and error paths.

At binary level, identify mapping and synchronization helpers and the values written to device descriptors. Recover whether the driver uses the mapped address or accidentally publishes the CPU/physical input. Compare every offset and length with the mapped segment.

## Constructed timeline

A hypothetical driver maps a 4096-byte transmit buffer, publishes the DMA address and completes the caller's request, unmapping and returning the buffer to a pool before the device signals descriptor consumption. A later allocation reuses the pages while the device can still read them.

The finding is refuted if the request transfers ownership to a device reference that retains the mapping and buffer until a valid completion fence.

## Primitive and impact limits

Direct effects include stale or unauthorized device reads/writes, cross-request disclosure, corruption and device or system denial of service. Arbitrary kernel write requires sufficient address/extent control and device capability; code execution or elevation requires a complete target and mitigation chain.

## Related knowledge and primary sources

`reference-virtual-device-ring-dma` owns shared address and mapping facts. This profile keeps direction, publication, completion and cleanup in one evidence chain.

Reviewed 2026-10-09 against Linux kernel [DMA API HOWTO](https://docs.kernel.org/core-api/dma-api-howto.html), [DMA API](https://docs.kernel.org/core-api/dma-api.html) and Microsoft [DMA object and adapter guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-common-buffer-system-dma). The timeline is constructed; device and platform contracts determine actual coherency.
