---
id: vulnerability-parser-decompression-output-accounting-failure
title: Decompression output-size, ratio, dictionary, or accounting failure
kind: vulnerability
topics: [parsers, decompression, resource-exhaustion, dictionaries, accounting]
platforms: [cross-platform]
architectures: [any]
---

# Decompression output-size, ratio, dictionary, or accounting failure

## Definition and violated invariant

A decompression-accounting vulnerability occurs when compressed input can cause output, retained state, window memory, CPU or nested work to exceed the authorized budget, or when dictionary and stream state are bound to the wrong input or lifetime. The application must account for actual cumulative production and retained resources across frames, members, nested decoders, retries and downstream parsing.

Declared content size, window size, output capacity, produced bytes and expansion ratio are different values. A limit on one does not automatically bound the others, and unknown-size sentinels are not zero.

## Conditions that establish the issue

Recover format and decoder API, frame/member policy, declared size and sentinel handling, window/dictionary requirements, input and output cursors, actual produced deltas, cumulative and nested budget owner, arithmetic widths, retained outputs, completion result, trailing input and error cleanup. Prove attacker-controlled input exceeds a required memory, disk, CPU or output bound or causes use of an invalid dictionary/prefix.

For borrowed dictionaries or prefixes, establish owner lifetime and immutability through the documented completion boundary. For ratios, include a nonzero absolute ceiling because small compressed inputs can still expand to an unacceptable total.

## Evidence that is not sufficient

A high compression ratio, large declared size, unknown size, concatenated members, decoder memory request or decompression error is not sufficient. The application may stream output into a bounded sink, enforce aggregate quotas, reject excessive windows, or safely discard data.

Successful cleanup does not prove complete or integrity-verified output, and frame completion does not prove all outer input was consumed.

## Investigation sequence

Build an accounting ledger for compressed bytes consumed, output bytes produced, retained bytes, decoder/window memory, dictionary identity, frame/member number and downstream objects. Preserve API-specific meanings for return values and cursor fields. Check limits before arithmetic and charge actual output before counters are reset.

Follow nested and concurrent jobs to the principal or service-wide budget. Trace partial output if a later checksum, trailer or completion error occurs.

## Constructed per-frame reset example

```c
for each compressed_frame in request {
    size_t produced_this_frame = 0;
    while (!frame_complete)
        produced_this_frame += decode_and_append(frame, retained_output);
    if (produced_this_frame > per_frame_limit)
        reject();
}
```

Every frame can stay below `per_frame_limit` while the retained output from many frames exceeds the request or service budget. The finding requires that concatenated frames are accepted, retained output accumulates, and no aggregate limit constrains it. A streaming consumer that releases each bounded frame can change the conclusion.

## Primitive and impact limits

The direct result can be memory, disk, CPU or address-space exhaustion, integer-driven underallocation, stale dictionary access, incomplete-output use or cross-request data confusion. Memory corruption requires an additional bounds or lifetime failure.

## Related knowledge and primary sources

`reference-parser-decompression-size-memory-limits`, `reference-parser-decompression-stream-results`, and `reference-parser-compression-framing-history` define decoder and format distinctions. This profile repeats aggregate budget and completion binding locally.

Reviewed 2026-10-09 against the [zlib manual](https://zlib.net/manual.html), Zstandard [public API contract](https://raw.githubusercontent.com/facebook/zstd/dev/lib/zstd.h), the Zstandard [format specification](https://www.rfc-editor.org/rfc/rfc8878.html), and liblzma [container API](https://tukaani.org/xz/liblzma-api/container_8h.html). The source is constructed.
