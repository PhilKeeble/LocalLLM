---
id: format-macho-mapping-dyld
title: Mach-O slices, load commands, ASLR slides, dyld fixups and shared-cache coordinates
kind: reference
topics: [mach-o, macho, dyld, slices, load-commands, slide, chained-fixups, shared-cache]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Mach-O and dyld evidence

## Mach-O container and slice coordinates

A universal/fat container records architecture-specific members with container
offsets and sizes. Its fat metadata is big-endian; each Mach-O member has its
own magic and encoding. Select CPU type/subtype and validate the entire member
range before parsing that slice. Preserve both container offset and slice
offset in findings. [1]

Constructed example: if the selected slice begins at container offset 0x4000,
a slice file offset 0x1180 refers to container offset 0x5180. Do not add the
slice base again after extracting that member into a separate file.

## Mach-O header and load-command bounds

Mach-O headers specify CPU type/subtype, file type, ncmds and sizeofcmds.
Load commands follow the header; each cmdsize includes associated payload.
LC_SEGMENT/LC_SEGMENT_64 describe VM and file extents and initial/maximum
protection fields. LC_UUID carries identity metadata; LC_SYMTAB locates symbols.
LC_CODE_SIGNATURE locates signature data, not a verdict of trust. [2]

Validate command minimum size, alignment, progress, total count and the complete
command region against the slice. Validate each embedded string/table within
its specified owner extent. Unknown required commands or unsupported formats
must be reported, not guessed. A parser accepting a malformed command does not
prove that the target OS loader accepts it.

## Mach-O file, preferred address and runtime slide

The preferred VM (virtual-memory) address is the linked address. The slide is
the displacement from that address to the corresponding loaded address.
For a file-backed segment without SG_HIGHVM, preferred v maps to slice file offset
`fileoff + (v - vmaddr)` only when the full range fits filesize and the slice.
Runtime VA is the preferred VM address plus the image's observed slide. Memory
beyond a segment's file extent is not automatically readable from the file.
LC_MAIN entryoff is a file/__TEXT coordinate, not a runtime VA. [2,3]

Constructed segment: fileoff=0x1000, vmaddr=0x100001000, filesize=0x400.
Preferred address 0x100001180 maps to slice offset 0x1180. With observed slide
0x200000 it executes at 0x100201180. A range starting at preferred 0x1000013f0
with length 0x20 crosses the file extent. Preserve the exact image and slide;
a process-wide guessed slide cannot substitute for the relevant image mapping.

## Mach-O SG_HIGHVM and nondefault mapping

SG_HIGHVM describes file content occupying the high portion of a segment's
virtual extent, with the low portion zero-filled; the header identifies stacks
in core files as its use case. [2] Do not use the ordinary vmaddr-to-fileoff
formula for this flagged layout. If vmsize >= filesize, the file-backed virtual
start is vmaddr + (vmsize - filesize), with checked additions.

Constructed example: vmaddr=0x1000, vmsize=0x3000, filesize=0x1000 and fileoff=0x800
places the first file-backed byte at preferred VA 0x3000, not 0x1000. VA 0x3100
maps to file offset 0x900; low virtual storage has no backing via this segment.
This is a format-derived mapping example, not evidence of a live core-file load.

## Mach-O nlist symbols and section ordinals

Mach-O nlist entries separate string-table index, type flags, section ordinal,
description and value. Check N_STAB before decoding ordinary N_TYPE bits.
N_SECT uses section ordinals starting at one across the file's load-command
section order; the same ordinal in another image can identify another section.
N_INDR's value is another symbol-name string index, not a code address. [6]

Constructed case: treating every n_value as a function pointer invents code at
an indirect symbol's string-table offset. Undefined/common/absolute entries
also need their own type interpretation. Preserve original mangled names and
the selected slice. An ordinary symbol table is not necessarily a complete
export list; compare dyld export metadata before concluding a name is unavailable.

## Mach-O entry paths, UUID and section roles

LC_MAIN's entryoff is not a live pointer; older LC_UNIXTHREAD uses CPU-specific
thread-state records. Initialization function-pointer sections add paths beyond
the named entry. LC_UUID supplies a 16-byte image identifier, not a signature.
Section types and attributes distinguish such roles as stubs, pointer tables,
zero fill and initialization; names alone do not establish them. [2]

For a stripped image, use load commands and typed metadata to find candidate
entries, then check instructions and references. A stub may transfer control
elsewhere rather than contain application logic. For UUID/dSYM matching use
`format-debug-information-build-matching`; a same-named framework or same display
version does not supply another slice's identity, slide or signing verdict.

## dyld rebasing, import binding and indirect call targets

dyld is Apple's dynamic linker. Rebasing adjusts image-relative address state;
binding resolves references to symbols. Mach-O dyld metadata describes these
operations and exports; modern
images may use dedicated export tries and chained-fixup commands. Names and
symbol-table labels alone do not establish the live destination. [2]

Chained fixups have an explicit pointer_format. Different encodings represent
targets, import ordinals, addends, next-chain steps and authentication fields
differently. A chain word on disk is not necessarily a plain address; decode
the selected format before interpreting its bits. Bound chain traversal and
import indexes and retain raw values. [4]

For an indirect call, compare the decoded binding with the observed pointer
and loaded image. Pointer-authentication metadata is not itself evidence that
authentication failed or that a target is attacker-controlled.

## dyld classic binding state and library identity

Classic Mach-O dyld bind opcodes describe a changing state: segment/offset,
binding type, library ordinal, symbol name and addend. Repeated bind operations
reuse prior state; a byte is not an independent complete import record. Regular,
weak and lazy binding streams have distinct roles. [2]

In two-level nlist metadata, library ordinals refer to dependent-library load
commands; special ordinals carry other lookup meanings. [6] Preserve ordinal
and namespace, not just spelling. Constructed case: two dylibs export the same
name, but the encoded dependency constrains the reference. Conversely, a lazy
slot pointing at a helper before resolution does not establish that the helper
is the final implementation. Confirm the loaded target rather than inferring it
from a disassembler's generated label.

## dyld path tokens and run-path context

Apple's dyld manual defines @executable_path relative to the main executable
and @loader_path relative to the image containing the referring load command.
@rpath substitutes entries from a run-path stack built from LC_RPATH commands
along the dependency chain. [10] These tokens are not interchangeable with
the shell's current directory or Linux $ORIGIN.

Constructed case: a plugin refers to @loader_path/../Frameworks/Helper. Resolve
from the plugin image, not the host executable's directory. Preserve each
candidate and the actual selected file; writable-path plausibility is not a
successful load. Environment overrides, shared caches, library validation and
platform restrictions require the target OS policy. The path-token contract
does not promise that DYLD_* variables are honored in every protected process.

## Mach-O export trie nodes and terminal payloads

A dyld export trie is a prefix-sharing tree of exported symbol names.
Nodes begin with a ULEB128 (unsigned variable-length integer)
terminal-payload size, followed by that payload and a child count; edges contain
terminated name suffixes and child offsets relative to the trie start. A zero
terminal size means no export at that prefix, not no descendants. Apple's
ExportsTrie implementation uses these separate terminal and child views. [7]

Bound ULEB128 decoding, payload size, strings, child targets and traversal depth;
detect cycles instead of following arbitrary offsets indefinitely. Record the
complete path spelling plus terminal flags. A prefix node's existence does not
prove an exported function. The blob's file offset and a child offset inside the
blob are different coordinates; add the blob base exactly once.

## Mach-O re-exports and nonordinary export values

Export terminal flags distinguish ordinary, absolute, thread-local, re-export,
and stub/resolver forms. A re-export supplies a library ordinal identifying the
dependency and an alternate name; an empty alternate name keeps the exported
spelling. Stub/resolver forms
carry two offsets, not one ordinary function address. [2][7]

Constructed case: export foo forwards to dependency 2's bar. Disassembling the
ordinal 2 as a code offset manufactures a false function. Follow the dependency
and imported name, and preserve resolver indirection if present. Do not add an
image slide indiscriminately to absolute values or treat a thread-local export
as a single process-global variable. The final selected target remains separate
runtime evidence, especially with weak definitions or interposition.

## Chained-fixup bases, pages and stride

The chained-fixups header gives starts/imports/symbol offsets relative to its
payload. Segment-info offsets are relative to the starts-in-image structure;
page starts locate chains within pages. NONE and MULTI page-start encodings
are not ordinary offsets. pointer_format controls both interpretation and
stride: inspected headers specify four-byte stride for DYLD_CHAINED_PTR_64,
but eight for ARM64E_USERLAND. [4]

Constructed case: next=3 advances twelve bytes in the former encoding and
twenty-four in the latter, not universally three pointer widths. Validate the
selected format, imports count, page/range and termination before each dereference.
Keep encoded next/bind/auth bits distinct from reconstructed pointer targets.
Unsupported pointer formats remain unknown, not a reason to decode with the
nearest familiar layout.

## Mach-O signature structures versus accepted identity

LC_CODE_SIGNATURE locates a blob; XNU's signature definitions include a SuperBlob
index of typed offsets and versioned CodeDirectory fields for hash slots,
identifier, code coverage and algorithm. The CodeDirectory pageSize field is
an exponent, not a literal byte count; zero has special meaning. [8]

Bounds-check each container, index and version-dependent field before reading.
A parseable CodeDirectory or identifier is not proof of integrity, trusted
signer, entitlement acceptance or runtime identity. Apple's TN2206 distinguishes
signature validity from satisfying a particular requirement/policy. [9] Preserve
which check was performed on which bytes and under which OS policy. Its archived
examples are not a current universal Gatekeeper/notarization policy. Do not
equate UUID matching with signature validation or successful validation with
authorization for a sensitive operation.

## dyld shared caches and runtime identity

Apple's shared-cache implementation exposes mappings, subcache file indexes,
file offsets, VM ranges and UUIDs. A cache image is not necessarily a standalone
dylib whose offsets can be applied to one file. Preserve OS build, cache UUID,
subcache identity and extraction method. Resolve through cache mappings before
converting addresses to file positions. [5]

dyld image enumeration can race with loading/unloading; the archived API
documentation explicitly warns about count-based iteration. Collect a stable
debugger snapshot or account for loader changes. A pathname, UUID or header is
identity evidence, not proof of signed origin or equivalent runtime bytes. [3]

## Sources and review scope

Reviewed 2026-10-02. Source headers describe encodings, not guaranteed acceptance
by every Apple OS build. Current main-branch source is a moving reference;
match a target's released source/build before asserting version-specific behavior.

1. [Apple fat.h](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/fat.h): container member offsets, sizes and byte order.
2. [Apple loader.h](https://github.com/apple-oss-distributions/xnu/blob/main/EXTERNAL_HEADERS/mach-o/loader.h): Mach-O commands, segments, entry point and dyld metadata.
3. [Apple dyld(3), archived](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man3/dyld.3.html): image header/slide and enumeration caveat; archive is not a current security-policy source.
4. [Apple fixup-chains.h](https://github.com/apple-oss-distributions/dyld/blob/main/include/mach-o/fixup-chains.h): header, per-segment chain starts and pointer formats.
5. [Apple DyldSharedCache.h](https://github.com/apple-oss-distributions/dyld/blob/main/common/DyldSharedCache.h): mapping/subcache APIs and identity fields.

## Additional symbol, export and signature sources

Reviewed 2026-10-02. These Apple main-branch definitions were inspected for
format distinctions; target-build acceptance still requires matching release
evidence. No target image or code signature was executed/verified in this review.

6. [Apple nlist.h](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/EXTERNAL_HEADERS/mach-o/nlist.h): symbol kinds, section indexes and library ordinals.
7. [Apple ExportsTrie.cpp](https://raw.githubusercontent.com/apple-oss-distributions/dyld/main/mach_o/ExportsTrie.cpp): trie structure, traversal and terminal forms.
8. [Apple cs_blobs.h](https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/kern/cs_blobs.h): SuperBlob and CodeDirectory versioned fields.
9. [Apple TN2206, archived](https://developer.apple.com/library/archive/technotes/tn2206/_index.html): validity, requirements and subsystem policy distinctions.
10. [Apple dyld manual source](https://raw.githubusercontent.com/apple-oss-distributions/dyld/main/doc/man/man1/dyld.1): path tokens and dependency-chain run paths; reviewed as dated source, not a universal current policy for every Apple platform.
