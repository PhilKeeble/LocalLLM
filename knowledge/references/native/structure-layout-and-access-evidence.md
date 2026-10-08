---
id: reference-native-structure-layout-access
title: Structure offsets, interior bases, array stride, packing, unions and partial layouts
kind: reference
topics: [structures, layout, packing, unions, embedding, array-stride, data-types]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover layout from byte ranges and object identity

## Observed accesses constrain a layout without completing it
Reviewed 2026-10-02. Reads and writes in one function constrain only the portions
of an object that function accesses. Unobserved bytes remain unknown, not padding
by default. Ghidra's structure-recovery exercise explicitly obtains only
fields used by the examined function, then extends the type using another. [1]
An automatically created structure is not a complete object declaration.

Constructed accesses from the same established base: two bytes at +0, four at
+4 and eight at +16. These constrain [0,2), [4,8) and [16,24); gaps [2,4) and
[8,16) remain unknown. Assuming all are valid accesses within one object gives
an extent of at least 24 bytes, not proof of sizeof=24. If the suspected bug is
an overread, do not assume that access valid to prove the object's capacity.
One eight-byte instruction can cover multiple source fields; access width alone
does not establish a field type. Retain validity assumptions with the layout.

## Interior pointers change the coordinate origin
Microsoft CONTAINING_RECORD recovers a containing structure from a known field
address and its declared type/field. [2] It is address arithmetic under a layout
contract, not validation that an arbitrary pointer belongs to a live object.

Constructed P=B+0x10: a load at P+8 accesses B+0x18, and P-0x10 recovers B.
Labeling that subtraction an underflow without identifying P's interior origin
can be wrong. Conversely, subtracting the expected offset from an attacker
pointer does not authenticate the resulting owner. Track base adjustments,
allocation identity and lifetime across helper calls. An embedded list node or
base subobject can be the passed pointer while its containing object owns the
allocation; do not merge their offset-zero field maps unchanged.

## Array stride, accessed span and allocation size need separate evidence
Microsoft's ordinary x64 aggregate layout pads structure size to its alignment;
array elements preserve that layout. [3] Compiler, packing and object-kind
evidence are required before extending this to a particular specimen.

Constructed loop accesses B+i*32+20 with width 4. Within each record, the observed
access ends at byte 24; stride is 32. This does not show what bytes 24..31 contain.
If independently established as a contiguous array of T with every element
visited, stride supports sizeof(T)=32. Without that fact, the loop might visit
every second 16-byte element or records embedded in larger slots. Allocation
capacity can additionally include headers or multiple objects. Preserve stride,
highest accessed byte and capacity as distinct constraints, not one guessed size.
For decoded media, row/plane strides are a different contract from sizeof(T)
array stride; `reference-parser-media-packets-frames` covers signed and padded
FFmpeg frame layouts without inferring a native record type.

## Ordinary x64 layout and packing produce different offsets
For ordinary Microsoft x64 aggregate layout, members follow their alignment and
the final size is a multiple of aggregate alignment. Packing can lower member
alignment; it is a compiler contract, not portable C++ layout. [3][4]

Constructed plain record {char a; uint32_t b; uint16_t c;} with sizes/alignment
1/1, 4/4 and 2/2, no explicit over-alignment: ordinary offsets are 0,4,8 and
size is 12. Under one-byte packing they are 0,1,5 and size is 7. Importing the
ordinary layout into the packed consumer reads the wrong bytes even if the
buffer is long enough. Verify target packing and declaration scope; do not infer
pack(1) from one unaligned access. Packing does not specify wire byte order,
pointer validity or a universal safe hardware access width.

## Packing an outer record need not repack a nested type
GCC 15.1 documents that packed on an outer record does not change the internal
layout of an independently defined unpacked member type. [5]

Constructed ABI assumptions: char size/alignment 1, int size/alignment 4. An
unpacked Inner {char c; int i;} has offsets 0/4 and size 8. A GCC packed Outer
{char tag; Inner inner;} places inner at +1, so inner.i is at Outer+5 and the
outer size is 9, absent other alignment attributes. Recursively removing the
inner padding would incorrectly place that integer at +2. Recover each type's
layout separately. Nested packed structures can also hold ordinary native-endian
fields; neither the packed spelling nor outer byte order rewrites every member.

## Overlapping accesses need variant and lifetime evidence
C++ union nonstatic members share an address, but at most one member is active
at a time. The common-initial-sequence guarantee is a specific exception for
eligible standard-layout struct members, not unrestricted cross-member access.
[6] These language rules do not prove that overlapping machine accesses came
from a source union.

Constructed offset +8 is read as a pointer under tag 1 and as a count under tag 2.
Keep variant-specific layouts and trace tag/payload writers. Modeling both as
simultaneously valid fields can hide type confusion; declaring a bug from the
overlap alone can also be wrong. Wide initialization, byte inspection, bitfield
containers and reused lifetimes are alternatives to test. Preserve load width,
conversion, tag condition and object phase; use
`reference-native-type-confusion-object-validity` for the violated-contract test.

## Complete-object size is not every C++ subobject's occupied data span
The Itanium C++ ABI distinguishes sizeof, alignment, dsize excluding tail padding,
and nvsize excluding virtual bases. [7] This terminology does not make MSVC layout
identical, or imply every base occupies an independent sizeof-sized interval.

Investigation inference: do not tile a derived object by blindly adding guessed
base sizes or call every byte beyond a base's last field unused storage. Confirm
the applicable layout and adjusted this/base pointers. For unknown types, keep
base-subobject extent and complete-object allocation as separate hypotheses.
The absence of writes to a region in one constructor does not establish padding
across other constructors, subclasses or lifetime phases. Full C++ dispatch and
construction rules require their own ABI evidence, not a generic struct model.

## Sources and limits
Reviewed 2026-10-02. Constructed offsets assume the stated widths/alignments;
they were not compiled. Native layout is distinct from serialized field layout.

1. [Ghidra advanced analysis](https://ghidra.re/ghidra_docs/GhidraClass/Advanced/improvingDisassemblyAndDecompilation.pdf): PDF pp. 20-21, combining partial structure observations.
2. [Microsoft CONTAINING_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/nf-ntdef-containing_record): known field-to-containing-instance contract.
3. [Microsoft x64 ABI conventions](https://learn.microsoft.com/en-us/cpp/build/x64-software-conventions?view=msvc-170): aggregate alignment and tail padding.
4. [Microsoft pack](https://learn.microsoft.com/en-us/cpp/preprocessor/pack?view=msvc-170): packing control; no inferred universal default or alignment-fault policy.
5. [GCC 15.1 type attributes](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Common-Type-Attributes.html): packed nested-member example.
6. [C++ unions](https://eel.is/c++draft/class.union): active member, shared address and common-initial-sequence conditions; living draft.
7. [Itanium C++ ABI data layout](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#data-layout): section 2.1, size/data-size/nonvirtual-size definitions; living ABI document.
