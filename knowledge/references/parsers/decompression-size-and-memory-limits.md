---
id: reference-parser-decompression-size-memory-limits
title: Decompression size sentinels, window memory and cumulative output limits
kind: reference
topics: [parsers, decompression, zstd, liblzma, resource-exhaustion, integer-overflow, output-limits]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Decompression size and memory limits

## ZSTD_getFrameContentSize distinguishes unknown, error and empty

ZSTD_getFrameContentSize returns the first frame's declared size, or
ZSTD_CONTENTSIZE_UNKNOWN / ZSTD_CONTENTSIZE_ERROR; these sentinels are not
ZSTD_isError results. Zero can describe an empty or skippable frame. A declared
size may exceed application/address-space limits and is untrusted. [1]

Investigative inference: classify the result before conversion, allocation or
arithmetic. Unknown is not zero, and a representable size is not authorization
to allocate it. Checking only the first frame's declaration cannot establish a
whole-input budget when the consumer processes multiple frames. Follow actual
production and the policy for inconsistent declarations and unfinished input.

## Zstandard window memory and frame content size are different quantities

RFC 8878 defines an optional Frame_Content_Size and a decoding Window_Size.
For single-segment frames, Window_Size equals Frame_Content_Size; otherwise the
window descriptor determines it. Decoders may reject excessive window requests.
[2] ZSTD_d_windowLogMax limits streaming window-buffer allocation, not the
single-pass API's output buffer. [1]

Investigative inference: a window cap does not establish a total-output cap,
nor does an output-length check establish affordable internal state. Recover
both limits, their units and whether the selected API applies them. Streaming
can bound retained output only if the application drains/discards it instead
of appending indefinitely to another allocation.

## liblzma memory limits do not replace caller output accounting

lzma_stream_decoder takes a decoder memory limit in bytes; UINT64_MAX effectively
disables it. The single-call lzma_stream_buffer_decode separately receives the
output-buffer extent and reports required decoder memory through memlimit on
LZMA_MEMLIMIT_ERROR. [3]

Investigative inference: inspect whether a caller blindly raises that limit and
retries, or applies an authorized ceiling. Decoder state, caller output storage,
queued decoded objects and CPU are different resources. A memory-limit error
does not establish corrupt input; it may indicate valid input exceeding policy.
Report the rejected scope rather than treating unavailable output as empty.

## Output accounting needs checked cumulative bytes and actual production

Constructed model: all values are nonnegative byte counts in one representable
unsigned domain. With limit L and already produced P, establish P <= L before
computing remaining=L-P. A proposed next output allowance N must satisfy
N <= remaining and also fit the actual destination capacity and API count type.
After decoding, charge the actual produced delta before resetting its counter
or reusing the output buffer. Do not charge output capacity as if all of it were
initialized payload.

This is an accounting model, not a universal decompressor API recipe. Reaching
the byte limit is distinct from stream completion: trailer processing may still
be needed. Recover how the wrapper finishes validation without permitting more
output, or rejects incomplete input. Arithmetic prerequisites are in
`reference-native-integer-size-buffer-arithmetic`.

## Frame resets and nested decoding must not silently reset task budgets

Constructed investigation: each frame resets its local output counter while the
caller retains every decoded frame. Local checks pass but aggregate retained
bytes exceed the promised request limit. The analogous problem occurs when an
inner decompressor starts with a fresh budget for every nested payload.

Keep stream state, allocation lifetime and task-level budget ownership separate.
Recover cancellation, error cleanup, concurrent jobs and downstream parsing cost.
An expansion ratio alone cannot bound total output or work. See
`reference-parser-archive-expansion-partial-evidence` for nesting and sparse-file
units, and `reference-logic-configuration-quotas-fallbacks` for reservations.

## Sources and scope

Reviewed 2026-10-02. Current upstream API documentation supplies scoped examples;
equations and nested-state cases are constructed investigative models. No claim
is made that these libraries themselves impose an application-wide output budget.

1. [Zstandard public header](https://raw.githubusercontent.com/facebook/zstd/dev/lib/zstd.h): ZSTD_getFrameContentSize and ZSTD_d_windowLogMax.
2. [RFC 8878](https://www.rfc-editor.org/rfc/rfc8878.html): §§3.1.1.1.1.2, 3.1.1.1.2 and 3.1.1.1.4, single-segment, window and content-size fields.
3. [liblzma container API](https://tukaani.org/xz/liblzma-api/container_8h.html): lzma_stream_decoder and lzma_stream_buffer_decode.
