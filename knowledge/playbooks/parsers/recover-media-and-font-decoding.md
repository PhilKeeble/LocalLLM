---
id: playbook-re-media-font-decoding
title: Recover image, font and audio/video decoding boundaries
kind: playbook
topics: [reverse-engineering, parsers, images, fonts, media, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover media and font decoding boundaries

## Identify the selected decoder and each representation

Preserve the original object and any containing document/member identity. Recover
format detection, codec/table dispatch, selected frame/track/font, configuration
and transformations. Identify container bytes, decoded samples/points and final
rendered buffers separately. A thumbnail or preview may exercise a different
path from full rendering; successful preview does not establish full coverage.

Use `reference-parser-image-decoding-extents`,
`reference-parser-font-tables-glyph-decoding` and
`reference-parser-media-packets-frames` for concrete scoped contracts. Use
`reference-parser-media-atoms-sample-indexes` for atom extents and track/sample
selection before handing bytes to a codec. Imports
and magic values are leads; confirm the input-dependent path before attributing
behavior to a particular library or decoder.

## Trace untrusted counts into actual allocation and use

For image/video, retain dimensions, crop/frame rectangle, sample depth, pixel
format, planes, signed strides, padding and actual output count. For audio,
separate samples per channel, channels, storage width, encoded blocks and bytes.
For fonts, separate character codes, glyph IDs, table offsets, contours, expanded
points and component references.

Follow validation, conversion, allocation and consuming loops. Check the exact
range and ownership of each destination, not just the enclosing file or mapped
page. A mathematically valid size does not establish an affordable allocation;
resource limits and arithmetic safety are independent. Treat decompiler types
as hypotheses until instruction widths and consumers corroborate them.

## Recover state across fragments, frames and nested objects

Track decompressor history, row/pass reconstruction, delayed codec output,
animation blend/disposal state and glyph-component expansion. Record which
boundary resets each state. Distinguish an encoded chunk from a complete image,
packet from frame, and a glyph-table entry from its recursively expanded shape.

Inspect termination and aggregate work as well as per-object bounds. A shallow
graph can repeat large subobjects; bounded frames can accumulate in a queue.
Use `reference-parser-decompression-size-memory-limits` for analogous accounting
and `reference-parser-container-boundaries-integrity` for parent/child extents.

## Separate malformed content, vulnerable decoding and malicious behavior

A format violation is evidence about input; a vulnerability additionally needs
a reachable decoder operation that violates memory, resource or authority policy.
Record the controlling bytes, surviving checks, affected operation and effect.
Legal overlapping glyph shapes, shared font tables or negative frame strides
must not become findings merely because they look unusual.

For malware analysis, identify whether decoded content is rendered, interpreted
as configuration, written elsewhere or passed into an execution path. Embedded
payload presence differs from actual selection/use. Preserve unexamined layers,
unsupported features and recovery warnings; do not turn a successful display
or lack of script into a general safety verdict. No sample execution is required
merely to recover these static contracts.

## Evidence and source basis

Retain original/decoded identities, decisive fields/call sites, widths and units,
selected variants, buffer ownership, error paths and limits on conclusions.
Label constructed layout models and static hypotheses separately from observed
runtime effects.

Reviewed 2026-10-02. This workflow uses the primary-source facts in the four
format/API references named above. It is an investigation aid, not a complete
validator for every image, font or media codec.
