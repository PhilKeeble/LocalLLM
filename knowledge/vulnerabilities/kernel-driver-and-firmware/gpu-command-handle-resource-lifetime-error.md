---
id: vulnerability-kernel-gpu-command-handle-resource-lifetime-error
title: GPU command, handle, device-address or pending-resource lifetime error
kind: vulnerability
topics: [kernel, drivers, gpu, command-buffer, handles, device-address, lifetime]
platforms: [cross-platform, linux, windows, android, macos]
architectures: [any]
---

# GPU command, handle, device-address or pending-resource lifetime error

## Definition and violated invariant

This vulnerability occurs when GPU software validates or resolves a command, handle, device address or referenced resource against the wrong context, range, type or lifetime. The invariant is that every command-visible object must belong to the submitting context, match the expected type and permitted range, and remain live and correctly synchronized until all device use finishes.

API handles, driver handles, device virtual addresses and CPU pointers are distinct representations. Queue submission makes work pending; returning from submission is not completion.

## Conditions that establish the issue

Identify submitter and device context, command format, validation path, handle namespace and generation, device-address mapping, buffer extent, permissions, referenced resources, synchronization and final completion. Prove attacker-controlled commands reach an incorrect object, escape a range, or use a resource after destruction/reassignment.

Include imported or shared resources, sparse mappings and reset/recovery. Validation in a user-mode component is not enough if a lower privileged boundary consumes mutable or incompletely checked commands.

## Evidence that is not sufficient

A GPU command buffer, numeric handle, device address, validation error or hang is not sufficient. Public API validation may reject the request, kernel validation may repeat checks and device fault containment may prevent memory access. Equal handle values across contexts do not imply the same object.

A fence proves only the work and visibility scope defined by that API; it is not a universal device drain.

## Investigation sequence

Trace application/API representation through runtime, user driver, kernel driver and device packets. At each boundary, record object namespace, type, generation, extent and mutability. Follow references into pending lists and determine what completion releases each resource.

At binary level, map command opcodes, handle lookup, address translation and bounds checks. Inspect integer units and sparse-page edges. Correlate reset and timeout paths with resource cleanup and stale completions.

## Constructed flow

A hypothetical kernel driver validates a command buffer containing handle H, resolves H to buffer P, then queues the still-writable command buffer. Before execution, the client replaces H in the command with another value and the device-side parser refetches it without repeating context and range validation.

The example is a mutable-command double fetch. It is refuted if the kernel captures an immutable validated command stream or the later consumer uses only the resolved object P.

## Primitive and impact limits

Direct effects include cross-context buffer access, stale resource use, GPU fault, memory corruption or denial of service. Kernel execution, host escape or elevation requires control over the resulting access and effective containment/mitigations.

## Related knowledge and primary sources

`reference-gpu-media-buffer-lifetime`, DMA and double-fetch profiles provide supporting contracts. This profile keeps GPU context, representation and pending lifetime together.

Reviewed 2026-10-09 against Vulkan [object lifetime](https://docs.vulkan.org/spec/latest/chapters/fundamentals.html#fundamentals-objectmodel-lifetime), [command-buffer lifecycle](https://docs.vulkan.org/spec/latest/chapters/cmdbuffers.html) and Linux DRM [GPU virtual memory](https://docs.kernel.org/gpu/drm-mm.html). The flow is hypothetical; private GPU packet formats require vendor-specific evidence.
