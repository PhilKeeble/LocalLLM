---
id: reference-parser-archive-member-identity
title: Archive member identity, ZIP headers and duplicate-name selection
kind: reference
topics: [parsers, archives, zip, tar, duplicate-names, member-selection]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Archive member identity

## ZIP central-directory entries and local headers are separate evidence

ZIP has local file headers and central-directory records. Both carry names and
size-related fields; central records identify local-header locations. External
attributes depend on the originating host-system identifier. [1]

Investigative inference: preserve the record index, raw name, decoded name,
header location and selected payload, not just a displayed filename. When a
scanner and extractor disagree, recover which record each trusts and whether
it checks consistency. A listing is not proof that the eventual consumer
selects the same bytes. An attribute value alone does not establish that the
extractor creates a link, executable file or other particular filesystem object.

## ZIP data descriptors: zero local size need not mean empty content

For ordinary ZIP entries without central-directory encryption, general-purpose
flag bit 3 indicates a data descriptor; ordinary local size fields are zero,
with final sizes in the descriptor and central record. It follows compressed data;
its signature is optional. ZIP64 uses eight-byte descriptor sizes. [1]

Investigative inference: a local zero is not sufficient to classify a member as
empty. Do not find a descriptor merely by scanning compressed bytes for a magic
value. Bind its location to the selected compression/framing path. Encrypted or
masked headers need their specific rules; this section is not that decoder.

## ZIP64 size and offset sentinels change field interpretation

ZIP64 extended information supplies wider values when corresponding legacy
fields contain their specified sentinel (0xFFFFFFFF for 32-bit sizes/offsets).
The local-header offset is relative
to its starting disk, not universally the beginning of a concatenated file. [1]

Investigative inference: record whether a value is a sentinel, byte count or
offset before widening it. A recovered 32-bit cast can truncate a valid wide
value; prove the subsequent allocation, seek or range check uses that result.
For split archives, missing disks mean incomplete evidence, not absent members.

## Duplicate archive filenames: lookup and iteration need not select alike

Python tarfile.getmember(name) selects the last occurrence when a name repeats.
Python zipfile permits passing a ZipInfo object to open/read/extract to identify
an individual duplicate entry. [2][3] Neither establishes another API's policy.

Investigative inference: distinguish iteration order, name lookup, overwrite
order and the final file read. Constructed case: a verifier checks the first
member named config while extraction publishes a later config. A vulnerability
requires evidence that this disagreement bypasses the intended check; duplicate
names alone are not malicious. Record both selected members and their hashes.

## ZIP extraction name rewriting can collapse distinct names

APPNOTE requires relative ZIP member paths without drive letters or leading
slashes. [1] Python ZipFile.extract transforms names, including removing dot-dot
components; zipfile.Path does not sanitize names. [3]

Investigative inference: format conformance and filesystem containment are
different questions. Compare names after the target's decoding and rewriting,
including the destination filesystem's comparison rules. If code takes a name
from zipfile.Path and later writes to disk, inspect that separate write path;
Path's existence alone does not show an out-of-directory write. See
`reference-parser-archive-extraction-effects` for links and overwrite behavior.

## Sources and scope

Reviewed 2026-10-02. Selected format/API facts, not a complete ZIP validator.
Python documentation inspected as 3.14.8; verify the target API and configuration.

1. [PKWARE APPNOTE 6.3.10](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT): §§4.3.7, 4.3.9, 4.3.12, 4.4.8–4.4.9, 4.4.15–4.4.17, 4.5.3.
2. [Python tarfile](https://docs.python.org/3/library/tarfile.html): getmember duplicate selection.
3. [Python zipfile](https://docs.python.org/3/library/zipfile.html): ZipInfo arguments, extract and Path name handling.
