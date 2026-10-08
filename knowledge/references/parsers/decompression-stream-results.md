---
id: reference-parser-decompression-stream-results
title: Streaming decompression progress, completion and trailing-input contracts
kind: reference
topics: [parsers, decompression, zlib, zstd, liblzma, streaming, error-handling]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Streaming decompression results

## zlib inflate: progress is not completed output

For zlib inflate, next_in/next_out are cursors; avail_in/avail_out are remaining
input/output capacities. The function updates them. [1]

| Result | Meaning for inflate |
| --- | --- |
| Z_OK | Progress, not necessarily completion |
| Z_STREAM_END | Compressed stream ended and output produced |
| Z_NEED_DICT | Preset dictionary required |
| Z_BUF_ERROR | No progress possible, or insufficient output for Z_FINISH; resumable |
| Z_DATA_ERROR | Invalid compressed data/check value |
| Z_MEM_ERROR | Allocation failure |

These are inflate contracts, not a universal numeric error convention. [1]
Investigative inference: follow the precise result branch and cursor changes.
Input exhaustion may require more input; output exhaustion may require draining
or replacing the output buffer. Repeating an unchanged call after no progress
can spin. Z_FINISH is not a promise that the supplied buffers contain a complete
stream or sufficient output space.

## zlib gzip concatenation and gzread acceptance differ

inflate stops at one gzip member; decoding another requires reset. gzread
instead decodes concatenated gzip members, passes through initially non-gzip
input, and ignores non-gzip trailing garbage after a gzip stream. [1]

Investigative inference: do not transfer one API's acceptance policy to another.
Track the remaining input and the application's decision to reject, retain or
decode it. A successful first member does not prove that all supplied bytes were
checked. Conversely, multiple members are not inherently malformed. This can
matter when a scanner and loader select different content, but the mismatch
must be connected to an actual bypass or behavior before assigning significance.

## Decoder cleanup does not prove completion or valid partial output

zlib inflateEnd frees state without flushing pending output. [1]

Investigation rule: distinguish emitted bytes, stream completion, integrity
acceptance and cleanup. A program may expose output before it learns that a
trailer is invalid or missing. Recover whether the next parser, file publisher
or loader consumes those early bytes and how a later error affects them. An
output prefix can be useful forensic evidence, but is not a verified complete
payload. Do not use cleanup success as a substitute for the decoding result.

## ZSTD_decompressStream: return value is not produced byte count

ZSTD_decompressStream updates input.pos and output.pos. Test its return with
ZSTD_isError; otherwise zero means a fully decoded/flushed frame, while positive
means more decoding/flushing remains and provides an input-size hint. Unconsumed
input must be presented again. [2]

Investigative inference: count output from the position delta, not the return
value. If the output buffer fills, pending output may remain even without new
input. A frame-complete result is distinct from consuming all outer input.
Check the wrapper's concatenation policy and reset behavior rather than assuming
one frame is the whole message or file.

## Zstandard error recovery and borrowed prefix lifetime

After a ZSTD_decompressStream error, reset its context before reuse.
ZSTD_DCtx_refPrefix borrows a prefix that must remain alive and unchanged through
frame completion; the reference is discarded at that boundary. [2]

Investigative inference: distinguish a recoverable shortage of input/output
from a decoder error. A pool returning an errored context to another request
needs a valid reset path. For a borrowed prefix, trace the owner and mutation
paths; retaining the context is not proof that the referenced bytes still exist.
These are API lifetime obligations, not evidence that every caller violates them.

## liblzma concatenation changes when stream end is reported

With LZMA_CONCATENATED, supported decoders require LZMA_FINISH before lzma_code
reports LZMA_STREAM_END. The flag supports .xz/.lz concatenation, not legacy
.lzma concatenation. [3]

Investigative inference: identify both the decoder and action argument.
Transport EOF must be propagated according to that contract; a loop that waits
for completion without conveying final input may fail to terminate correctly.
Do not copy zlib's flush semantics into liblzma because names look similar.
Preserve incomplete input separately from unsupported format and memory failure.

## liblzma integrity-check flags qualify what decoding success proves

For .xz decoding, LZMA_IGNORE_CHECK skips payload integrity verification,
not header CRC checks. LZMA_TELL_UNSUPPORTED_CHECK reports an unsupported check
type; that input can be decoded without verifying that check. [3]

Investigative inference: recover flags and handling of informational results
before describing successful output as integrity-checked. Unsupported verification
is not the same as a failed check or an authenticated source. A deliberate forensic
recovery path may retain partial/unverified content, but must label it accordingly.

## Sources and scope

Reviewed 2026-10-02: zlib 1.3.1 manual, current upstream zstd.h and liblzma API
documentation. Recover the target's actual API, flags and library contract.
Workflow: `playbook-re-decompression-boundary`. Format/history facts:
`reference-parser-compression-framing-history`.

1. [zlib manual](https://zlib.net/manual.html): z_stream, inflate/inflateEnd, inflateInit2 and gzread.
2. [Zstandard public header](https://raw.githubusercontent.com/facebook/zstd/dev/lib/zstd.h): ZSTD_decompressStream and ZSTD_DCtx_refPrefix.
3. [liblzma container API](https://tukaani.org/xz/liblzma-api/container_8h.html): LZMA_CONCATENATED, LZMA_IGNORE_CHECK and LZMA_TELL_UNSUPPORTED_CHECK.
