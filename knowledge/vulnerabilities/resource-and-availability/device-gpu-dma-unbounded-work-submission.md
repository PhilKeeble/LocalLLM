---
id: vulnerability-resource-device-gpu-dma-unbounded-work-submission
title: Device, GPU or DMA work submitted without bounded completion
kind: vulnerability
topics: [resource-exhaustion, device, gpu, dma, work-queue, cancellation]
platforms: [cross-platform, kernel, firmware]
architectures: [any]
---

# Device, GPU or DMA work submitted without bounded completion

## Definition and violated invariant

This vulnerability lets an actor submit device, GPU or DMA work without effective quotas, completion deadlines, cancellation or recovery, exhausting queue slots, pinned memory, descriptors, device time or global reset capacity. The violated invariant is that asynchronous hardware work and every resource it retains must be bounded and attributable until terminal completion.

Submission success is not completion. Host-visible request objects, mappings and fences can remain live while hardware is pending, hung or reset.

## Conditions that establish the issue

Identify the submitter and authority, command source, validation, queue and scheduler, outstanding-job and byte quotas, pinned or mapped resources, completion signal, timeout, cancellation and reset scope. Show an attacker can keep enough valid or malformed work pending to deny other authorized users or repeatedly trigger disruptive recovery.

Include per-context and device-wide limits. A job isolated to one queue may still consume global engines, memory or reset machinery.

## Evidence that is not sufficient

A queue submission, long-running command, timeout handler or device reset is not sufficient. Schedulers may enforce fairness and hardware-queue limits; commands may be preemptible; resources may be charged and reclaimed; resets may isolate the guilty context. One device-loss result does not identify an attacker-controlled exhaustion path.

Do not infer arbitrary DMA or memory access from high work volume. Address and permission validation is a separate kernel/device safety issue.

## Investigation sequence

Trace command creation, validation, resource pinning or mapping, scheduler admission, hardware publication, fence/completion, timeout, cancellation, reset and cleanup. Account for jobs and retained bytes per context and device. Recover whether a client can submit faster than completion or create work that never signals.

At binary level, map ioctl or API selectors to command buffers, queue counters, pending lists and cleanup callbacks. Check whether timeout removes work, retries it or performs a global reset, and whether all referenced resources remain owned until the final fence.

## Constructed timeline

A hypothetical driver accepts unlimited command buffers from an unprivileged client, pins each buffer before scheduling, and releases it only when a completion fence signals. A command that waits forever on an unsignaled dependency retains its pinned pages, while the client submits more such jobs.

The finding requires missing or ineffective outstanding-work and pinned-memory quotas plus a supported noncompletion path. A bounded per-context queue or cancellation that signals every terminal fence can refute it.

## Primitive and impact limits

Report outstanding jobs, pinned bytes, device time, scheduler scope, timeout and recovery blast radius. Direct effects include process, device or system denial of service. Memory corruption, cross-context reads or kernel execution require separate validation or lifetime defects.

## Related knowledge and primary sources

Kernel queue and DMA profiles cover address, ownership and descriptor correctness. This profile owns admission, completion and availability accounting for hardware work.

Reviewed 2026-10-09 against the Vulkan [queue submission model](https://registry.khronos.org/vulkan/specs/latest/html/vkspec.html#devsandqueues-submission), Linux DRM [GPU scheduler documentation](https://docs.kernel.org/gpu/drm-mm.html#gpu-scheduler) and [MITRE CWE-770](https://cwe.mitre.org/data/definitions/770.html). The timeline is constructed; scheduler and reset behavior are driver- and device-specific.
