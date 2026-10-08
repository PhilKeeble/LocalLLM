---
id: reference-gpu-media-buffer-lifetime
title: GPU and media command interpretation, buffer extents and asynchronous lifetime
kind: reference
topics: [gpu, media, command-buffers, handles, synchronization, dma, lifetime]
platforms: [linux, android, windows, macos, embedded]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Device command and media-buffer evidence

## GPU API handles and device addresses are different representations

Vulkan represents objects through handles. Objects allocated from a logical
device are private to it; external-handle import/export has a separate contract.
The API assigns lifetime responsibility to the application. [1]

Recover handle type, owning device/context, underlying resource and any imported
storage. A numeric value that looks like a pointer is not proof of a host address,
and equal values across contexts do not prove one object. Vendor command packets,
kernel handles and Vulkan API handles need their respective contracts; the public
API does not document every driver's private command parser.

## Recording or submitting GPU commands does not complete their accesses

Vulkan command buffers can enter a pending state while device work executes;
pending buffers must not be modified. Object references can remain accessible
through pending work, so returning from a recording/submission call is not the
end of all resource use. [1][2]

Recover command state, referenced storage, completion scope and final destruction.
For command parsing, distinguish the API request, translated driver/device command
and the parser actually consuming lengths, offsets and resource selectors. An API
validation error is not automatically a kernel defect, and a driver crash does
not establish which command violated which boundary.

## GPU execution completion and memory visibility need the right dependency

Vulkan has explicit execution and memory dependencies, with some defined implicit
guarantees. A host fence wait alone does not automatically make all device writes
visible to host access; the required memory dependency must also exist. [3]

Bind a signal/wait to the queues, stages, accesses and resource in question. One
completed batch does not prove unrelated work or external consumers finished.
GPU, CPU and imported-buffer users need separately established synchronization.
This is Vulkan's dependency model, not a universal meaning for every fence named
by an OS, media API or vendor driver.

## V4L2 buffer fields depend on the selected I/O and plane representation

In Linux V4L2 multi-planar requests, v4l2_buffer.length counts plane-array entries;
a USERPTR plane's length describes buffer bytes. For queued DMABUF buffers, QBUF
hands the buffer to hardware access, and application access while locked has
undefined results. DQBUF returns a buffer or error; returned error flags can
indicate corrupted data. [4]

Recover type, memory method, plane extents, payload lengths, queue ownership and
result. Do not interpret an array count as bytes or a mapped view as permission
to reuse queued storage. Media parser input and decoded-output capacity remain
different boundaries. Workflow: playbook-specialist-device-work.

## Sources and scope

Reviewed 2026-10-08. Rolling Khronos and Linux documentation; target API features,
backend and hardware must be identified. No vendor packet encoding or driver default.

1. [Vulkan fundamentals](https://docs.vulkan.org/spec/latest/chapters/fundamentals.html): Object Model, Object Lifetime and External Object Handles.
2. [Vulkan command buffers](https://docs.vulkan.org/spec/latest/chapters/cmdbuffers.html): lifecycle/pending state.
3. [Vulkan synchronization](https://docs.vulkan.org/spec/latest/chapters/synchronization.html): dependencies and host fence visibility caveat.
4. [V4L2 QBUF/DQBUF](https://docs.kernel.org/userspace-api/media/v4l/vidioc-qbuf.html): plane arrays, USERPTR/DMABUF ownership, dequeue and errors.
