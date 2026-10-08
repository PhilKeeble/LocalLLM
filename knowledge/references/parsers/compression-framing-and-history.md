---
id: reference-parser-compression-framing-history
title: Compression wrappers, DEFLATE history references and gzip size fields
kind: reference
topics: [parsers, decompression, deflate, gzip, zlib, dictionaries, back-references]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Compression framing and history references

## Raw DEFLATE, zlib and gzip are different input grammars

DEFLATE defines compressed blocks. The zlib wrapper adds CMF/FLG, an optional
preset-dictionary identifier and an Adler-32 trailer. Gzip members have their
own header, optional fields and CRC32/ISIZE trailer. [1][2][3]

Investigative inference: identify the wrapper and payload boundary before
assigning meaning to an apparent magic value or checksum. A valid DEFLATE body
does not establish validity of a missing wrapper. Recover any fallback from
wrapped to raw decoding and whether it bypasses a required integrity or format
check. An intentional embedded raw stream is not itself a downgrade or anomaly.

## DEFLATE block end is not necessarily stream end

DEFLATE block headers carry BFINAL and BTYPE. BTYPE selects stored, fixed-Huffman
or dynamic-Huffman coding; its reserved value is invalid. Blocks need not start
on byte boundaries. BFINAL identifies the final block. [1]

Investigative inference: track bit position as well as byte cursor when recovering
an inlined/custom decoder. A Huffman end-of-block symbol does not alone establish
that the stream is finished. Do not align every block to a byte or reset all
history merely because control reaches a block-dispatch loop. Tables and shift
operations suggest a codec, but require corroborating input/output behavior.

## DEFLATE backward matches can cross blocks and overlap new output

DEFLATE matches use lengths 3–258 and backward distances 1–32768. They can
reference earlier blocks. References must reach available output history,
including the applicable preset dictionary where used. Overlap with output
being generated is allowed. [1]

Constructed example: with a preceding byte A, a length-four, distance-one match
emits four A bytes by repeatedly using newly produced history. Investigative
inference: an overlapping match is not automatically an invalid copy. A bulk
copy implementation must reproduce that expansion semantics and still enforce
destination capacity. A zero or unavailable distance is a different issue.
Recover ring-buffer wrap and valid-history length independently of output size.

## zlib preset dictionary identity is required decoding context

In a zlib stream, FDICT signals DICTID, an Adler-32 identifier for a preset
dictionary. ADLER32 covers uncompressed data excluding that dictionary. A
decoder must reject an unknown required dictionary. [2]

Investigative inference: compressed bytes alone may be insufficient to recover
content. Trace dictionary acquisition, selection and lifetime rather than
silently trying an unrelated dictionary and treating output as established fact.
The identifier is not an authentication token; neither it nor a matching output
checksum establishes trusted origin. Record the dictionary alongside the
compressed specimen when explaining a reproducible decoding result.

## gzip ISIZE is modulo 2^32, not a full allocation length

A gzip member's ISIZE stores uncompressed size modulo 2^32. Gzip files can
contain successive members. [3]

Constructed arithmetic: lengths 1 and 2^32+1 both have ISIZE=1. Therefore ISIZE
alone cannot bound full output or justify allocating exactly that many bytes
for an arbitrary member. Count actual production in an adequate checked domain,
and separate per-member size from cumulative file output. A small ISIZE paired
with large valid output is not necessarily a format inconsistency.

## Compression checksums do not authenticate recovered payloads

zlib's ADLER32 and gzip's CRC32 concern uncompressed data, not sender identity.
[2][3] Investigative inference: a producer controlling content can recompute an
unkeyed check value. Separate detection of accidental corruption from a verified
signature or authenticated channel, and recover exactly which representation
the latter protects. A successful decompression is not proof of benign content,
valid executable layout or execution by the original program.

## Sources and scope

Reviewed 2026-10-02. Selected decoding facts, not complete codec implementations.
API progress/results: `reference-parser-decompression-stream-results`.
Resource accounting: `reference-parser-decompression-size-memory-limits`.

1. [RFC 1951](https://www.rfc-editor.org/rfc/rfc1951.html): §§3.2.3–3.2.5, blocks and backward matches.
2. [RFC 1950](https://www.rfc-editor.org/rfc/rfc1950.html): §2.2, wrapper, dictionary and checksum.
3. [RFC 1952](https://www.rfc-editor.org/rfc/rfc1952.html): §§2.2–2.3.1, members, optional fields and trailer.
