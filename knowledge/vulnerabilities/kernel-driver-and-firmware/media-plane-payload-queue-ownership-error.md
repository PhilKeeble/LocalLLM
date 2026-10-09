---
id: vulnerability-kernel-media-plane-payload-queue-ownership-error
title: Media plane, payload or queued-buffer ownership error
kind: vulnerability
topics: [kernel, drivers, media, codec, planes, payload, buffer-ownership]
platforms: [cross-platform, linux, windows, android, macos]
architectures: [any]
---

# Media plane, payload or queued-buffer ownership error

## Definition and violated invariant

This vulnerability occurs when a media pipeline confuses plane count, allocation length, payload length, stride, sample count or queue ownership, causing a codec or device to access the wrong range or a producer to reuse storage still owned by another stage. The invariant is that every plane and payload must have format-correct geometry within its allocation and remain exclusively owned until the defined dequeue or completion transition.

Samples, pixels, rows, planes and bytes are different units. A buffer allocation can be large enough while an active payload or individual plane is too short.

## Conditions that establish the issue

Identify selected format and dimensions, plane model, count, per-plane base/allocation/payload/stride, crop, queue state, producer/consumer and completion. Prove attacker-controlled media or metadata makes a reached codec/device access exceed a plane's live payload or allocation, or allows concurrent/reused access while queued.

For compressed input, keep packet extent separate from decoded frame capacity. For multi-planar APIs, establish whether a length field counts plane entries or bytes under that operation.

## Evidence that is not sufficient

A large dimension, negative stride, multiple planes, short packet, queued buffer or decoder error is not sufficient. Format rules, driver validation, padding, cropping or a larger backing allocation may make the access valid. Queuing commonly transfers temporary ownership by design.

Do not infer one packet produces one frame or one frame uses one allocation; recover the actual codec and API contract.

## Investigation sequence

Trace container metadata into codec configuration and final plane geometry. Build per-plane intervals for every row or sample access with signed strides preserved. Follow queue, DMA and fence ownership from fill through submit, device/codec use, dequeue and reuse.

At binary level, annotate units on multiplication and fields. Identify whether the code checks aggregate bytes but later indexes individual planes, or trusts returned payload length after an error. Include delayed frames, draining and reconfiguration.

## Constructed layout

A hypothetical YUV420 frame has a full-resolution luma plane and two chroma planes with implementation-defined stride and subsampling. Code allocates only `width * height` bytes but then derives chroma pointers after the luma plane and writes them. The luma allocation is insufficient unless the selected format or external allocation supplies the additional planes.

The arithmetic is illustrative; odd dimensions, alignment and actual pixel format determine the exact chroma geometry.

## Primitive and impact limits

Direct effects include out-of-bounds read/write, cross-frame disclosure, stale DMA or denial of service. Exploitability depends on affected address, controlled values, allocator/device isolation and process or kernel authority.

## Related knowledge and primary sources

`reference-gpu-media-buffer-lifetime` and media parser references provide API and geometry facts. This profile retains plane units and queue ownership locally.

Reviewed 2026-10-09 against Linux V4L2 [`VIDIOC_QBUF` and `VIDIOC_DQBUF`](https://docs.kernel.org/userspace-api/media/v4l/vidioc-qbuf.html), FFmpeg [`AVFrame`](https://ffmpeg.org/doxygen/trunk/structAVFrame.html) and Microsoft [uncompressed video buffers](https://learn.microsoft.com/en-us/windows/win32/medfound/uncompressed-video-buffers). The layout is constructed and format-specific values require target evidence.
