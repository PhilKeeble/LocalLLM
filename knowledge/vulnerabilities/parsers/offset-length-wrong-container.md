---
id: vulnerability-parser-offset-length-wrong-container
title: Offset and length validation against the wrong containing object
kind: vulnerability
topics: [parsers, offsets, lengths, containment, integer-arithmetic]
platforms: [cross-platform]
architectures: [any]
---

# Offset and length validation against the wrong containing object

## Definition and violated invariant

An offset/length containment vulnerability occurs when a parser validates a range using an extent or origin different from the one used to form or authorize the resulting access. Offsets must be interpreted relative to the format-defined base and bounded by the specific parent object whose contents they may reference.

A range can fit the complete file or allocation while escaping its record, section, message, plane, table or privilege domain. Some formats deliberately use file-relative or message-relative references, so the grammar determines the correct container.

## Conditions that establish the issue

Recover the encoded offset and length, their widths and signedness, alignment, the base used by the consumer, the extent used by each check, the format-defined reference domain, and the full accessed range. Prove a feasible value passes validation against one domain but the computed access escapes the required parent or backing allocation and reaches a meaningful consumer.

For nonnegative values in one representable domain, containment requires `offset <= parent_extent` before checking `length <= parent_extent - offset`. This proves only byte containment, not object validity, lifetime or semantic authorization.

## Evidence that is not sufficient

Pointer addition, a file-relative offset, subtraction-based check, or reference outside the immediate child is not sufficient. The format may permit references to a shared root, string table or other nonlocal object, and a separately validated target may be correct.

Do not infer the offset base from field proximity or decompiler naming. Follow the actual addition and the format contract.

## Investigation sequence

Record every coordinate as `(base identity, offset, extent, unit)` and keep file offsets, virtual addresses, record-relative offsets and decoded pointers separate. For each validation, note which tuple it constrains; for each access, recompute the final interval from the base actually used.

Walk nested parents outward to the backing allocation. A range must satisfy every boundary required by the grammar and trust model, even if it remains mapped.

## Constructed interior-base example

```c
if (offset <= file_length && length <= file_length - offset)
    parse(record_base + offset, length);
```

Assume `record_base = file_base + 0x800`, `file_length = 0x1000`, and the format defines `offset` relative to a record of length `0x200`. Values `offset=0x900` and `length=0x10` pass the shown file-length check, but `record_base + offset` is `file_base + 0x1100`, beyond the file allocation and far outside the record. The flaw is the disagreement between the checked origin/extent and the address calculation, not offset arithmetic in isolation.

## Primitive and impact limits

The direct result can be out-of-bounds access, sibling-object confusion, unauthorized cross-section reference, wrong relocation, or parser desynchronization. Impact depends on whether the escaped range is read, written, executed or used for allocation and dispatch.

## Related knowledge and primary sources

`reference-parser-container-boundaries-integrity`, `reference-parser-offset-based-serialization`, and native integer/range references define coordinate and containment evidence. This profile repeats exact-base and exact-parent binding locally.

Reviewed 2026-10-09 against FlatBuffers [encoded layout and offsets](https://flatbuffers.dev/internals/), ELF [object-file structures](https://refspecs.linuxfoundation.org/elf/gabi4+/contents.html), and [MITRE CWE-823](https://cwe.mitre.org/data/definitions/823.html). The source and numeric example are constructed and do not claim FlatBuffers uses the shown base.
