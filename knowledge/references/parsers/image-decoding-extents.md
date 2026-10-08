---
id: reference-parser-image-decoding-extents
title: Image decoding dimensions, packed samples, scanlines and animation bounds
kind: reference
topics: [parsers, images, png, apng, tiff, pixel-formats, scanlines, buffer-sizing]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Image decoding extents

## PNG bit depth is not bytes per pixel

PNG IHDR bit depth counts bits per sample or palette index, not per pixel.
Color type determines sample composition and permitted depths. Sub-byte grayscale
samples and palette indices are packed; 16-bit samples are most-significant-byte
first. [1]

Investigative inference: retain width, height, color type, depth, decoded output
format and row stride as separate values. A palette index is not an RGB triple;
conversion may increase storage. Recover the decoder's requested output format
before interpreting allocation arithmetic. A file-header depth does not establish
the number of bytes a conversion helper writes for each output pixel.

## Noninterlaced PNG filtered rows include a filter byte

PNG filtering adds one filter-type byte to each serialized scanline before
compression. Interlacing uses reduced-image passes. [1]

Constructed size model for a valid noninterlaced image: with W pixels per row,
C encoded samples per pixel and B bits per sample, row payload is
ceil(W*C*B/8) bytes and the filtered stream uses H*(1+row_payload) bytes.
For indexed color, use C=1 and B=index bit depth. Prove every multiplication,
round-up and addition representable before allocating. This is the filtered
image-data size, not a file length, decoded RGB allocation or interlaced formula.
An interlaced decoder needs each pass's own dimensions and row state.

## PNG IDAT boundaries do not reset the decompressor

Consecutive IDAT data fields concatenate into one zlib datastream. Chunk
boundaries may split any part of that stream, including its final check value.
[1]

Investigative inference: retain decompression and row-reconstruction state across
chunks. A chunk-sized input buffer need not contain a whole row or DEFLATE block.
Track compressed bytes, filtered rows and converted pixels separately; do not
apply one coordinate to all three. See `reference-parser-decompression-stream-results`.
CRC coverage and unknown-chunk rules remain in
`reference-parser-container-boundaries-integrity`.

## Palette index bounds use the actual PLTE entry count

An indexed PNG may contain fewer palette entries than its bit depth can represent;
an index beyond the actual palette is an error. [1]

Investigative inference: a bitmask limiting indices to the encoded bit width does
not establish a valid palette access. Recover actual entries, entry stride and
the checked value used by the lookup. Conversely, an unused representable index
does not invalidate every pixel; establish whether the input actually supplies
it and how the decoder handles it.

## APNG frame rectangles and saved-frame state need independent bounds

APNG fcTL supplies frame width/height and x/y offsets. The rectangle must fit
within IHDR dimensions. Disposal controls the output region after display. [1]

Investigative model: for nonnegative representable pixel counts, check x<=W
before frame_width<=W-x, and likewise for y/H. Convert pixels to byte/plane
coordinates separately. Recover blend/disposal branches and saved-region
allocation, not only the initial canvas allocation. Repeated frames also need
aggregate work/retention limits; one bounded rectangle does not bound animation
cost. A frame distinct from the static preview is not itself malicious.

## LibTIFF scanline output is decoded but not necessarily expanded pixels

TIFFReadScanline returns decompressed, native-order data that otherwise remains
packed. Its buffer must hold TIFFScanlineSize bytes; sample selects a plane only
for separate-planar data. It returns 1 on success, -1 on error. The documented
subsampled-YCbCr limitations require strip/tile interfaces instead. [2]

Investigative inference: do not interpret success as a byte count or assume the
buffer contains four bytes per pixel. Match the chosen API, planar arrangement
and format to the subsequent copy/conversion. A library call cannot protect a
caller that supplies a smaller allocation than the API requires. Preserve file
versus native byte order when correlating offsets with decoded sample values.

## Sources and scope

Reviewed 2026-10-02. These are selected PNG/APNG and LibTIFF contracts, not a
complete image-format catalogue. Equations and review consequences are analytical.
Workflow: `playbook-re-media-font-decoding`. Signed/padded frame strides:
`reference-parser-media-packets-frames`.

1. [PNG third edition, 24 June 2025](https://www.w3.org/TR/2025/REC-png-3-20250624/): §§7.2–7.3, 8, 10.2, 11.2.1–11.2.3 and 11.3.6.2, samples, filtering, passes, palette and fcTL.
2. [LibTIFF TIFFReadScanline](https://libtiff.gitlab.io/libtiff/functions/TIFFReadScanline.html): 4.7.2 documentation, packed/native output, capacity, planar selection and YCbCr caveat.
