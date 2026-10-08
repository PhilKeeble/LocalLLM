---
id: reference-parser-font-tables-glyph-decoding
title: OpenType table bases, cmap selection, loca extents and glyph expansion
kind: reference
topics: [parsers, fonts, opentype, truetype, cmap, glyphs, offsets, recursion]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Font table and glyph decoding

## OpenType table offsets and collection offsets use an explicit base

OpenType table records contain a tag, checksum, offset and length. Top-level
offsets are file-relative; in a TTC collection they remain relative to the
collection file, not each font's directory. Fonts in a collection may share tables.
Subtable bases must follow their particular definitions. [1]

Investigative inference: preserve selected font index, containing-file identity
and each offset's origin. Validate the whole table range before reading its
counted arrays. Shared ranges are not automatically overlap corruption; copying
one font's directory without its referenced tables may not yield a standalone
font. A four-letter tag identifies intended interpretation, not a valid body.

## cmap maps character codes to glyph IDs, not byte offsets

OpenType cmap contains encoding-specific subtables. Unicode format 4 covers
the Basic Multilingual Plane; format 12 supports supplementary characters with
32-bit character codes. Selection depends on encoding records; the specification
recommends consistent choice among equivalent Unicode subtables. [2]

Investigative inference: identify platform/encoding IDs and the selected format
before treating a recovered value as Unicode or a glyph index. Preserve the
mapping result separately from later glyph/table offsets. Glyph zero represents
missing-character handling in this context, not automatically a failed parse. [3]
Different mapping paths can reach different glyphs; establish which path the
renderer or text extractor actually uses before interpreting a disagreement.

## TrueType loca indexes glyf with an extra terminal offset

loca contains numGlyphs+1 ascending offsets relative to glyf. Glyph i occupies
the difference between offsets i and i+1; equal offsets can represent an empty
glyph. head.indexToLocFormat selects 16-bit stored offsets multiplied by two
or 32-bit actual offsets. [3]

Investigative inference: validate the selected representation, complete offset
array, glyph index and both endpoints before subtracting. A nonnegative result
alone does not prove the glyph is within glyf. Do not mistake the terminal offset
for another glyph or reject all zero-length glyphs. These rules concern TrueType
glyf outlines, not CFF/CFF2 charstring indexing.

## Simple-glyph flags expand into logical points and coordinate deltas

For simple TrueType glyphs, point flags have packed/repeated representations.
REPEAT_FLAG's following byte counts additional copies of that flag. Flags also
select omitted, one-byte or two-byte coordinate deltas; encoded byte counts
therefore differ from logical point counts. [4]

Investigative inference: track flags consumed, flags expanded, point count and
coordinate bytes independently. A repeat that fits the encoded buffer may
overrun the logical point array. Reconstruct cumulative coordinates in the
correct signed domain; treating deltas as absolute positions changes subsequent
geometry. Checked storage bounds do not establish affordable rasterization work.

## Composite glyphs are references with transforms, not inline simple points

A negative glyf.numberOfContours selects a composite description. Components
reference other glyphs and may apply placement/transforms. Nested composites
must form an acyclic graph; maxp.maxComponentDepth describes maximum nesting. [4]

Investigative inference: do not convert the negative discriminator to a huge
unsigned contour count. Recover component index checks, accumulated points,
transform arithmetic and recursion termination. A header's claimed maximum
is not proof of an enforced budget. Bound total expansion as well as path depth;
repeated references can multiply work without a cycle. A valid composite glyph
is normal font data, not evidence of a malicious object graph.

## TrueType fpgm and prep are interpreter input, not native machine code

The optional fpgm program runs when the font is first used and defines functions
or instructions. prep contains TrueType instructions affecting font-wide state;
it runs before the first glyph after changes such as font, size or global
transform, and is not rerun for each composite component. [5][6]

Investigative inference: identify the bytecode interpreter and its stack,
storage, instruction and point-access checks rather than disassembling these
bytes under the host ISA. Presence of font instructions is a normal rendering
feature, not proof of native code execution. Recover the selected rasterizer's
actual hinting path; parsing an outline does not prove these programs ran.

## Font rendering reaches more than one outline parser

OpenType permits TrueType or CFF outlines and alternate glyph descriptions such
as bitmaps, SVG and color vector compositions. [1]

Investigative inference: follow table dispatch into the actual outline, bitmap,
color or instruction consumer. A valid directory does not validate every nested
format. For malware analysis, distinguish embedded font presence from a reachable
decoder flaw or demonstrated effect. For vulnerability review, identify the
input-dependent call and violated range/state contract; unusual glyph data alone
does not establish exploitation.

## Sources and scope

Reviewed 2026-10-02 against OpenType 1.9.1 pages. Selected directory and TrueType
rules do not constitute a full shaping engine, hinting interpreter or CFF decoder.
Workflow: `playbook-re-media-font-decoding`.

1. [OpenType font file](https://learn.microsoft.com/en-us/typography/opentype/spec/otff): table records, collections and glyph representations.
2. [cmap](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap): encoding records, selection and formats 4/12.
3. [loca](https://learn.microsoft.com/en-us/typography/opentype/spec/loca): count, ordering, bases, widths and empty glyphs.
4. [glyf](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf): simple flags/deltas and composite graph/transform rules.
5. [fpgm](https://learn.microsoft.com/en-us/typography/opentype/spec/fpgm): optional font program and definition role.
6. [prep](https://learn.microsoft.com/en-us/typography/opentype/spec/prep): control-value program and execution triggers.
