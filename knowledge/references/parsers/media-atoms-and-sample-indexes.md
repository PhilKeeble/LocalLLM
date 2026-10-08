---
id: reference-parser-media-atoms-sample-indexes
title: QuickTime atom sizes, sample tables and scoped fragmented-media rules
kind: reference
topics: [parsers, media, quicktime, mp4, iso-bmff, atoms, sample-tables, mse]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Media-container indexing and selected payloads

## QuickTime atom size includes the header and nested content

Apple's QuickTime format gives ordinary atoms an eight-byte size/type header.
Size includes the complete atom. Size 1 selects an additional 64-bit size field;
size 0 extends a top-level atom to EOF and is not the rule for arbitrary nested
atoms. Numeric data is generally big-endian unless otherwise specified. [1]

Investigation model: after identifying the header variant, require its complete
extent, size at least the header length and containment within the enclosing
extent. Use checked subtraction before advancing. Retain parent context when
interpreting a type code. Skipping an unknown atom still requires a trustworthy
extent. These are QuickTime rules; confirm the selected ISO BMFF/MP4 profile
before transferring every exception to another format.

## QuickTime chunk offsets are file-relative, not mdat-relative

QuickTime stco entries hold 32-bit chunk offsets; co64 supplies the 64-bit
alternative. The offsets are relative to the containing media-data file, not
to an mdat atom. Media can refer to files without atom structure; moving a
self-contained file's front metadata changes data offsets that follow it. [2]

Investigative inference: recover the selected data source as well as the offset.
Do not add an mdat base merely because the bytes happen to lie there. Validate
offset plus the required payload extent in that source using a sufficiently wide
domain. Rewriting metadata without preserving/remapping source identity and
offsets can invalidate an analyst's extraction or comparison.

## QuickTime sample location joins several tables

QuickTime's sample-to-chunk table records first chunk, samples per chunk and
sample-description ID. Where present, the sample-size table supplies byte sizes
for individual samples. Sample descriptions provide decoding information; the sample table
connects media time, sample number and sample location. [2][3][4]

Investigation model: reconstruct the selected sample's chunk, size and description
together before decoding. Check table extents, index domains, counts and accumulated
sizes; a bounds check on the stco array alone does not prove a complete sample is
available. Keep samples, chunks, bytes and time units separate. A plausible codec
signature in mdat is not enough to establish the track, sample boundary or codec
configuration used by the player. Table storage and logical expanded counts can
have different sizes.

## QuickTime sample descriptions select format and data reference

A QuickTime stsd sample description has its own byte size, format and data-reference
index, followed by media-type-specific data. More than one description can exist;
stsc identifies which description applies. Entries need not share a fixed size.
[6]

Investigative inference: validate each description's extent before interpreting
codec-specific fields, and join its data-reference index to the actual source.
A single track need not use one invariant decoder configuration or one data file.
Keep the selected description with a recovered sample; a global codec label can
hide a change in layout or in the authority used to fetch its bytes.

## W3C MSE media segments require initialization context

The W3C Media Source Extensions ISO BMFF byte-stream profile describes an
initialization segment as ftyp followed by moov. A media segment consists of an
optional styp, a moof and one or more mdat boxes. These are MSE profile rules, not
a complete grammar for every MP4/QuickTime file. [5]

Investigative inference: preserve the applicable initialization segment when
analyzing a captured media fragment. Do not assume one network buffer is one
segment or that a detached mdat has enough information for interpretation.
Track configuration changes and buffer assembly independently from individual
box parsing. Route packet/frame and signed-stride contracts to
`reference-parser-media-packets-frames`.

## MSE fragment acceptance differs from generic file-reader acceptance

The W3C MSE ISO BMFF profile requires movie-fragment-relative addressing, a tfdt
in each traf and enough mdat data for referenced trun samples; external data
references are an append-error condition. Codec configuration may depend on
in-band parameters or the last initialization segment. [5]

Investigative inference: identify whether the target consumes MSE segments or
ordinary files before declaring an input valid or malformed. A file reader and
browser append path can legitimately enforce different restrictions. For either
path, connect the selected sample range to the actual decoder and destination
buffer; container rejection alone does not demonstrate a decoder vulnerability.

## Sources and scope

Reviewed 2026-10-02. Apple's QuickTime File Format documentation supplies the
selected atom/sample rules. The W3C MSE ISO BMFF document is a work-in-progress
Group Note and is used only for its explicitly named profile, not as the complete
ISO base media specification. This is indexing guidance, not every codec's grammar.

1. [QuickTime atoms](https://developer.apple.com/documentation/quicktime-file-format/atoms): header size, extended size, EOF scope and byte order.
2. [Chunk offset atom](https://developer.apple.com/documentation/quicktime-file-format/chunk_offset_atom): stco/co64, file coordinates and sample-table context.
3. [Sample-to-chunk table](https://developer.apple.com/documentation/quicktime-file-format/sample-to-chunk_atom/sample-to-chunk_table): table entry fields.
4. [Sample-size table](https://developer.apple.com/documentation/quicktime-file-format/sample_size_atom/sample_size_table): sample byte sizes.
5. [MSE ISO BMFF byte-stream format](https://www.w3.org/TR/mse-byte-stream-format-isobmff/): initialization/media segments and append-error conditions.
6. [QuickTime sample description](https://developer.apple.com/documentation/quicktime-file-format/sample_description_atom): variable entry sizes, format and data-reference selection.
