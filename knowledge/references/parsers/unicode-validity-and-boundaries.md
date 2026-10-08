---
id: reference-parser-unicode-validity-boundaries
title: UTF-8 validity, UTF-16 surrogate boundaries and grapheme-count limits
kind: reference
topics: [parsers, unicode, utf-8, utf-16, surrogates, grapheme-clusters, text-bounds]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Unicode validity and text boundaries

## Valid UTF-8 is not just a sequence of continuation-byte shapes

RFC 3629 UTF-8 uses one to four bytes per scalar value. Surrogate values
U+D800..U+DFFF and values above U+10FFFF are excluded; overlong representations
are invalid. Encoding each half of a UTF-16 supplementary pair separately does
not produce valid UTF-8. [1]

Investigative inference: recover the full decoder constraints, including lead-byte
and second-byte restrictions, not merely a loop recognizing 10xxxxxx continuation
bytes. Compare rejection, replacement and skipped-input behavior at each stage.
A replacement-decoded log cannot establish the original byte sequence. Custom
encodings such as modified UTF-8 need their own contract rather than a false
finding based only on disagreement with RFC 3629.

## UTF-16 slicing can split one scalar value into invalid halves

UTF-16 encodes supplementary characters with a surrogate pair. Conversion to
standard UTF-8 encodes the pair's scalar value as one four-byte sequence, not
two independent three-byte sequences. [2]

Constructed example: U+1F600 is UTF-16 D83D DE00 and UTF-8 F0 9F 98 80. It occupies
two UTF-16 units, one scalar value and four UTF-8 bytes. Truncating to the first
UTF-16 unit splits the pair. Recover whether a substring length counts bytes,
units or scalars, and whether the next converter rejects or replaces the result.
An API capable of storing unpaired code units does not make that data valid
Unicode scalar text.

## Grapheme-cluster limits do not bound text storage

UAX #29 grapheme clusters approximate user-perceived characters and can contain
multiple code points. The defined cluster size has no fixed upper bound;
a cluster-count limit is not a byte-size limit. [3]

Investigative inference: keep UI length checks separate from allocation and
processing budgets. A validator counting displayed characters cannot justify
a buffer with one byte or one UTF-16 unit per character. For normalization,
rendering and segmentation, inspect both input bytes and accumulated work.
Multiple combining marks are not intrinsically malicious; a resource finding
requires reachable excessive work or storage under the application's limits.

## Incremental UTF decoding needs state across transport fragments

A multibyte encoding's character boundary need not coincide with a receive-buffer
boundary. For UTF-8, a valid scalar can require up to four bytes. [1]

Investigative model: distinguish incomplete-at-buffer-end from invalid-at-stream-end.
Recover retained bytes, decoder state, consumed counts and finalization. Resetting
at every read can replace or reject a valid split sequence; reprocessing retained
bytes can duplicate output. Do not assume all formats permit arbitrary text
fragmentation: `reference-parser-incremental-input-buffer-state` and the format's
own chunk rules determine whether validation is per chunk or per logical value.

## Sources and scope

Reviewed 2026-10-02. RFC 3629 (2003), Unicode UTF FAQ and current UAX #29 supply
encoding/segmentation facts. Examples and fragment models are constructed, not
specimen observations. Windows buffer/count contracts remain in
`reference-native-text-encoding-size-units`.

1. [RFC 3629 §§3-4, 10](https://www.rfc-editor.org/rfc/rfc3629.html): UTF-8 validity and decoding security.
2. [Unicode UTF FAQ](https://www.unicode.org/faq/utf_bom.html): surrogate pairs and UTF conversion.
3. [UAX #29, grapheme-cluster boundaries](https://www.unicode.org/reports/tr29/): user-perceived units and unbounded cluster size.
