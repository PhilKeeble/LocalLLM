---
id: playbook-specialist-device-work
title: Recover virtual-device, GPU and media request ownership and completion
kind: playbook
topics: [device-models, command-parsing, rings, buffers, dma, synchronization, lifetime]
platforms: [linux, android, windows, macos, freebsd, embedded]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Device request evidence order

## Identify the parser and representation at each boundary

Map caller/API request, driver or device-model translation and final device/parser
input. Establish device/context, transport/queue format, features and command
schema. Bind lengths, offsets, counts and selectors to their actual units and
containing extents. Keep shared mutable input separate from a captured snapshot.

Facts: reference-virtual-device-ring-dma and reference-gpu-media-buffer-lifetime.
A public graphics API is not the vendor's private command format, and one valid
descriptor does not prove the operation's semantic validity or authorization.

## Separate addresses, handles, mappings and underlying storage

For each resource, record identity, context, representation, extent, rights and
retaining owner. Distinguish host/guest/device addresses and imported/exported
resources. Follow translation results and mapping failures without treating a
numeric value as a universally dereferenceable pointer.

Use the target's DMA, graphics or media contract. A readable local mapping is not
proof the application owns a buffer while queued device work accesses it.

## Match publication and completion to the exact work

Recover initialized request, availability publication, notification, consumer,
output extent and completion identity. Bind synchronization to its actual queue,
generation, stages and access scope. Account for reset/cancellation, index reuse
and external users before matching old requests to current state.

A notification, submission return or one signaled fence does not prove unrelated
work ended or every write is visible to the CPU. Preserve the applicable
protocol's ordering and completion exceptions in the report.

## Review reuse and effects with remaining uncertainty stated

Follow each retained resource until its final consumer has finished and the
contract permits unmapping, freeing or requeueing. Separate decoded data, produced
output, device state and a crash report. Identify which input violated which
range, authority, ordering or lifetime condition before alleging a defect.

An emulated failure is not automatically a hardware or host compromise. This
workflow interprets available evidence; it supplies no malformed command recipe,
target execution requirement or device configuration change.

## Review basis

Reviewed 2026-10-08 against reference-virtual-device-ring-dma and
reference-gpu-media-buffer-lifetime, plus reference-concurrency-mutable-validation-double-fetch
and reference-concurrency-cancellation-completion-shutdown. Primary source scope
remains in those factual references; no universal queue or fence behavior assumed.
