---
id: format-packages-archives-contained-images
title: APKs, Apple bundles, archives and firmware containers versus executable images
kind: reference
topics: [packaging, archives, apk, app-bundles, firmware-volumes, extraction, evidence]
platforms: [windows, linux, android, macos, ios, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Containers and executable evidence

## Container identity is not image identity
Reviewed 2026-10-02. Packaging identifies a collection or transformation, not
necessarily one loadable image. Preserve the original container hash, member
path/identifier, extraction method, output hash and any architecture/slice choice.
Track compressed-member offsets separately from offsets in decompressed bytes;
neither is automatically a runtime address. See `format-disk-versus-loaded-image`.

Constructed case: a ZIP member begins at container offset 0x2000, but its compressed
data expands into an ELF image. Adding 0x2000 to an ELF file offset does not locate
that byte in the compressed stream. Record the transformation instead. A scanner's
embedded magic hit is a candidate boundary, not evidence that the containing
system loads that object or that extraction recovered its entire contents.

## Android AAB versus the installed split set
An Android App Bundle (AAB) organizes modules used to generate APKs. Base, feature
and configuration APKs have different roles; configuration APKs can supply native
libraries for a selected architecture. Features can arrive on demand. On Android
5.0/API 21 and later, installed split APKs can form one application. [1]

Therefore, missing native code in base.apk does not establish its absence from
the installed app. Record the collected split set, device ABI, package version
and acquisition time. Distinguish code available in the submitted bundle from
code installed for that device and from code subsequently loaded. Missing feature
splits are an evidence gap, not proof that a conditional path is unreachable.

## Android member paths and analysis metadata
NDK libraries conventionally occupy lib/<abi>/lib<name>.so within an APK ZIP.
The same basename under arm64-v8a and x86_64 is not the same machine-code image. [2]
Verify the ELF machine/class as well as the member path; record the selected
member hash and do not apply one ABI's offsets to another.

AAB modules place manifests and DEX files under manifest/ and dex/ directories;
these differ from APK layout. BUNDLE-METADATA can contain mappings useful for
analysis but is not packaged into the generated APKs. [1] Missing mappings in an
installed APK therefore do not prove the build never produced them. Obtain
matching artifacts where authorized; do not fabricate names from another build.

## Apple bundles contain distinct code and resource objects
Apple's archived bundle guide describes macOS applications with Contents/Info.plist,
Contents/MacOS and Contents/Resources. CFBundleExecutable names the main
executable; iOS bundles use a different, flatter layout. Bundles can also include
frameworks and plug-ins. [3] Treat the guide as layout evidence, not current
platform signing or installation policy.

Inventory executable helpers, frameworks and resources separately. Preserve
relative paths and link relationships without following links outside the
acquisition boundary. A .app directory is not one Mach-O file, and its display
version does not establish identical builds for all nested images. Match each
image/slice independently; use `format-macho-mapping-dyld` for mapping and path
tokens and `format-debug-information-build-matching` for symbol identity.

## Static library archives: embedded members versus thin external references
GNU ar normal archives contain member files; its thin archives instead retain a
symbol index and references to original member files. The stored paths are
relative to the archive. Adding a thin archive to another thin archive flattens
member references rather than nesting an embedded copy. [4]

A copied thin archive is not a self-contained object-code collection. Missing
referenced files prevent inspection of those members; they do not prove the
library has no implementation. Resolve references only against the authorized
captured build tree, retaining the referenced object's identity. An archive's
symbol index is not proof that every member was linked into the target binary.
See `format-dependency-evidence-symbol-resolution` for selected versus discarded
code and runtime dependency evidence.

## PI firmware volumes and FFS files: nested executable discovery
PI means Platform Initialization; FFS is the firmware file system used within
these volumes. EDK II's PI definitions describe a firmware volume header with
FileSystemGuid, FvLength, HeaderLength and a header checksum. _FVH is a format signature, not a
cryptographic signature. [5] A checksum match does not establish trusted origin.
Check the declared ranges against the acquired bytes before descending.

FFS file headers identify a file by GUID and carry type, size and state. Their
sections can encapsulate compression or GUID-defined data, or hold PE32, TE,
raw data or another firmware volume. [6] Preserve this parent/child chain when
extracting an image. Not every section is code; not every firmware package uses
PI firmware volumes. A recognizable leaf does not establish dispatch, device
acceptance or the trust policy of the containing update mechanism.

## PI section sizes and decoding boundaries
For the inspected EDK II PI section definitions, Size[3] is a little-endian
24-bit total length including the header. The value 0xFFFFFF selects the extended
section header with a 32-bit ExtendedSize. GUID-defined section DataOffset is
relative to the common header; the GUID specifies how its content is interpreted.
Compression sections declare an uncompressed length. [6]

Do not reuse this section escape rule for FFS file headers: those use a distinct
large-file attribute and extended-size layout. [6] Validate the selected header,
minimum size, payload bounds and extraction limits. Unknown GUID processing or
an unavailable decompressor means content is unexamined, not benign or absent.
Declared output size is untrusted input, not permission for unlimited allocation.

## Archive extraction: member identity is not a filesystem destination
A displayed archive name does not establish which member is selected or where
its bytes are written. Preserve member identity and transformation evidence;
do not silently treat partial extraction as a complete specimen. ZIP records,
duplicate selection and rewritten names are covered in
`reference-parser-archive-member-identity`.

Link resolution, overwrite and metadata restoration have separate contracts;
use `reference-parser-archive-extraction-effects` and
`reference-parser-archive-expansion-partial-evidence` for the factual boundaries.
`playbook-re-archive-extraction-boundary` follows them into vulnerability and
malware investigations without assuming that extraction proves execution.

## Primary sources and scope
Reviewed 2026-10-02. Examples are constructed, not target execution observations.
Apple guide is archived; EDK II main-branch sources are dated evidence,
not claims of matching a particular deployed release. UEFI's hosted PI pages were
unavailable during review; PI layout statements above use the inspected headers.

1. [Android App Bundle format](https://developer.android.com/guide/app-bundle/app-bundle-format): modules, metadata and split APK roles.
2. [Android NDK ABIs](https://developer.android.com/ndk/guides/abis): Native code in app packages.
3. [Apple Bundle Structures](https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html): application layouts, nested bundles and executable key.
4. [GNU ar](https://sourceware.org/binutils/docs/binutils/ar.html): normal/thin archives and relative member paths.
5. [EDK II PiFirmwareVolume.h](https://raw.githubusercontent.com/tianocore/edk2/master/MdePkg/Include/Pi/PiFirmwareVolume.h): EFI_FIRMWARE_VOLUME_HEADER.
6. [EDK II PiFirmwareFile.h](https://raw.githubusercontent.com/tianocore/edk2/master/MdePkg/Include/Pi/PiFirmwareFile.h): file, common section, compression and GUID-defined headers.
