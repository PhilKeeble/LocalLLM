---
id: vulnerability-parser-media-image-font-extent-error
title: Media, image, or font dimension, stride, plane, table, or stream error
kind: vulnerability
topics: [parsers, media, images, fonts, dimensions, strides, tables]
platforms: [cross-platform]
architectures: [any]
---

# Media, image, or font dimension, stride, plane, table, or stream error

## Definition and violated invariant

A media-decoding extent vulnerability occurs when encoded dimensions, sample formats, planes, strides, table indexes, offsets, compressed state or converted output dimensions are combined under inconsistent units or insufficient bounds. Every accessed encoded range and produced plane or row must fit the selected format, parent object and destination layout using checked arithmetic.

Pixels, samples, bits, bytes, rows, planes, frames, chunks, glyphs, points, file offsets and decoded output bytes are distinct coordinates. A valid container does not validate every codec or font subtable it selects.

## Conditions that establish the issue

Recover format/profile and selected decoder, width and height, sample or pixel format, bit depth, channel/plane arrangement, signed stride and origin, row bytes and padding, frame rectangle, table counts and offsets, compressed input state, output conversion and destination allocation. Prove a feasible input makes an access or write escape its exact source or destination range or exceeds the required work bound.

For media containers and fonts, join all tables needed to identify the selected sample, description, glyph or program. An in-range index in one table does not validate the target table or payload.

## Evidence that is not sufficient

Large dimensions, negative stride, packed samples, interlacing, multiple planes, compressed chunks, recursive glyphs or a complex table graph is not sufficient. These are normal representations when their formulas, offsets and limits are applied correctly.

A decoder error or malformed file does not prove memory corruption. Trace the violated range and actual access or effect.

## Investigation sequence

Create separate ledgers for encoded bytes, decoded logical elements and destination storage. Derive row or plane spans from the selected format, including round-up and signed-stride origin, and validate frame rectangles before conversion. For table-driven media/fonts, trace each index and reference to the terminal payload.

At machine level, bind allocation arithmetic to loop scale, access width and row/plane advance. Check state retained across compressed chunks, frames and passes.

## Constructed packed-image example

```c
size_t row_bytes = width * channels;          /* assumes one byte per channel */
uint8_t *pixels = allocate(row_bytes * height);
decode_16bit_samples(input, pixels, width, height, channels);
```

If the selected output format writes two bytes per channel, the allocation is half the required size even though width, height and channel count are individually valid. The finding requires the decoder's actual output contract and checked multiplication for the correct row span; an API that retains packed input or rejects this format changes the conclusion.

## Primitive and impact limits

The direct result can be out-of-bounds read or write, integer-driven underallocation, cross-plane confusion, invalid table traversal, excessive work or stale decoder state. Exploitability depends on attacker control, affected bytes and active memory/control-flow defenses.

## Related knowledge and primary sources

`reference-parser-image-decoding-extents`, `reference-parser-media-atoms-sample-indexes`, `reference-parser-media-packets-frames`, and `reference-parser-font-tables-glyph-decoding` define concrete coordinate systems. This profile repeats unit and terminal-range binding locally.

Reviewed 2026-10-09 against PNG [image layout](https://www.w3.org/TR/png-3/), LibTIFF [scanline output](https://libtiff.gitlab.io/libtiff/functions/TIFFReadScanline.html), Apple [QuickTime atoms and tables](https://developer.apple.com/documentation/quicktime-file-format), and OpenType [font-file structure](https://learn.microsoft.com/en-us/typography/opentype/spec/otff). The source is constructed.
