---
id: vulnerability-memory-row-stride-plane-miscalculation
title: Row stride, pitch, and plane extent miscalculation
kind: vulnerability
topics: [memory-safety, stride, pitch, images, media, planes]
platforms: [cross-platform]
architectures: [any]
---

# Row stride, pitch, and plane extent miscalculation

## Definition and violated invariant

A stride or plane vulnerability occurs when row, slice, channel, or plane addressing uses geometry that does not fit the backing storage. For positive stride `S`, `H > 0` rows, and `R` accessed bytes per row, the highest relative end is `(H-1)*S + R`, subject to representable arithmetic. Packed width, active row bytes, padded stride, plane dimensions, and total allocation are distinct values.

Signed stride can traverse toward lower addresses, so the supplied row-zero pointer need not be the allocation's lowest address. Prove the minimum and maximum accessed addresses against the owning plane rather than converting a negative stride to unsigned.

## Conditions that establish the issue

Recover pixel or element format, dimensions, subsampling, plane count, row bytes, signed stride, starting pointer, and allocation for every plane. Prove that at least one reachable scalar, vector, or row-copy range falls outside its corresponding object. Include padding and the final access width.

For conversions, source and destination can have different formats and strides; validate both independently. A total pixel count does not prove a planar or padded layout fits.

## Evidence that is not sufficient

Stride larger than active row bytes, negative stride, padding, or distinct plane pointers is not sufficient. These are ordinary representations when their start pointers and allocations support the complete visited span.

A `width * height * bytes_per_pixel` allocation is suspicious only after establishing that the consumer also uses padding, a different output format, subsampled dimensions, or another layout contribution.

## Investigation sequence

Create a plane table containing base object, row-zero pointer, width, height, row bytes, signed stride, element format, and allocation extent. Calculate first and last accessed rows without assuming top-down order, then include the complete per-row access. Check arithmetic before address formation.

In assembly, locate the outer-row increment separately from the inner-element scale. Confirm which value advances source and destination and whether a signed stride was sign-extended. Vectorized tails may access a wider range than the decompiler's element loop suggests.

## Constructed source example

This hypothetical copier validates only tightly packed bytes but advances destination rows by a larger stride:

```c
int copy_rows(uint8_t *destination, size_t destination_bytes,
              const uint8_t *source, size_t row_bytes,
              size_t rows, size_t destination_stride)
{
    if (row_bytes * rows > destination_bytes)
        return -1;
    for (size_t y = 0; y < rows; ++y)
        memcpy(destination + y * destination_stride,
               source + y * row_bytes, row_bytes);
    return 0;
}
```

Assuming representable products, `row_bytes == 8`, `rows == 3`, `destination_stride == 16`, and a 24-byte destination pass the check, but the last copy writes destination offsets 32 through 39. Source readability and multiplication overflow require separate proof.

## Constructed address representation

The essential constructed loop can appear as the following architecture-neutral address calculations:

```asm
destination_row = destination_base + row_index * destination_stride
source_row      = source_base      + row_index * row_bytes
copy(destination_row, source_row, row_bytes)
```

The destination's maximum end is based on stride, while the guard in the source example used `row_bytes * rows`. Recover actual multiplication widths and loop bounds; a larger backing allocation or a smaller accepted row count can refute the overrun.

## Primitive and impact limits

The direct primitive is an out-of-bounds read or write in a specific row or plane. Record the first violating row, direction, access width, padding state, and whether attacker-controlled decoded values reach the write.

Impact depends on adjacent plane or object layout and subsequent use. A bad stride may produce visual corruption or a fault without controlled memory corruption; negative stride alone has no adverse implication.

## Related knowledge and primary sources

`reference-parser-media-packets-frames` defines signed frame-line behavior, and `reference-parser-image-decoding-extents` distinguishes packed input from converted output. This profile repeats the complete-span formula required for isolated assessment.

Reviewed 2026-10-09 against Microsoft [Image Stride](https://learn.microsoft.com/en-us/windows/win32/medfound/image-stride), FFmpeg [`AVFrame` data and linesize](https://ffmpeg.org/doxygen/trunk/structAVFrame.html), and [MITRE CWE-131](https://cwe.mitre.org/data/definitions/131.html). The source, values, and address representation are constructed.
