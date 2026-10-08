---
id: reference-parser-compound-file-streams-sectors
title: OLE compound file storage names, FAT chains, mini streams and logical extents
kind: reference
topics: [parsers, documents, ole, cfb, fat, mini-streams, stream-bounds]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Compound-file stream reconstruction

## CFB storages and streams are different objects

Microsoft Compound File Binary (CFB) represents a hierarchy of storages and
streams. A storage contains children; a stream represents a logical sequence of
bytes and has no children. Names are unique within a parent storage, not across
the whole file. A storage can carry a CLSID identifying an associated application.
[1]

Investigative inference: retain the full storage path and directory-entry identity
when extracting a stream. A basename alone can select the wrong object. A CLSID
is classification evidence, not proof that the application was instantiated.
Successful CFB enumeration does not establish that an inner Office, VBA or other
application-specific stream was parsed or activated.

## CFB sector sizes depend on the major version

The CFB signature bytes are D0 CF 11 E0 A1 B1 1A E1. Header integer fields are
little-endian. Version 3 uses 512-byte sectors; version 4 uses 4096-byte sectors.
Mini sectors are 64 bytes. The mini-stream cutoff is 4096 bytes: nonempty smaller
user streams use the mini FAT; user streams at least that size use the regular FAT.
[2]

Investigative inference: establish header version, declared stream size and sector
namespace before calculating addresses. An integer that names a mini sector is
not a regular sector number or byte offset. Reject unsupported/inconsistent
header geometry explicitly rather than silently interpreting it as the common
version. Container magic alone does not establish a particular Office document
type or guarantee that its directory is intact.

## CFB FAT traversal follows links, not consecutive file sectors

The CFB file allocation table (FAT) maps a sector to the next sector in its chain;
0xFFFFFFFE denotes end of chain. A user stream's directory entry supplies its
name and byte size. Its chain can be fragmented; allocated chain capacity must
cover the logical stream length. Unused capacity in the last sector is not part
of that logical stream. [3][5]

Investigation model: validate each sector reference against the correct table
and available file extent, recognizing special markers before address arithmetic.
Bound traversal and track visited sectors to detect loops. Retain any mismatch
between declared size, reachable capacity and actual bytes read. A carved trailing
byte sequence should not be attributed to the logical stream merely because it
occupies the same final allocated sector.

## CFB mini-sector offsets are relative to the reconstructed mini stream

The mini FAT itself is stored in a regular FAT chain. The mini stream is also
stored through the regular FAT; the root directory entry identifies its starting
sector. Mini-sector number m identifies byte offset m*64 within that mini stream,
not within the original file. The mini stream may be absent if no small streams
require it. [4]

Investigative inference: reconstruct the regular-sector-backed mini stream before
mapping a small user stream's mini-sector chain. Keep physical file offsets,
mini-stream offsets and final user-stream offsets distinct. Check multiplication,
each mini-sector range and the user stream's declared length independently. A
contiguous logical user stream can originate from multiple noncontiguous physical
regions; record that mapping when attributing malformed bytes to an operation.

## Inner stream bounds remain separate from container validity

For a CFB-consuming binary, trace the reconstructed stream and its actual byte
length into the application parser. Identify record lengths, allocation counts,
seeks and callbacks in that parser; outer sector-chain validity does not prove
those operations stay within their own objects.

For malware analysis, distinguish recovered embedded bytes from the host action
that loads, links, interprets or executes them. Preserve unsupported/encrypted
streams and extraction failures as coverage limits. Use
`reference-parser-office-relationships-vba-source` for package relationships and
VBA source boundaries; neither document specifies every Office binary record.

## Sources and scope

Reviewed 2026-10-02 against Microsoft's MS-CFB web specification, selected sections
1.3, 2.2, 2.3, 2.4 and 2.6. These are container contracts, not assumptions about
any particular Office application's recovery or activation behavior.

1. [CFB overview](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/bc33425a-fbb9-4f73-911f-2662c7a14060): storage/stream hierarchy and names.
2. [CFB header](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/05060311-bfce-4b12-874d-71fd4ce63aea): signature, versions, sector sizes and cutoff.
3. [FAT sectors](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/30e1013a-a0ff-4404-9ccf-d75d835ff404): chain links and special entries.
4. [Mini FAT sectors](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/c5d235f7-b73c-4ec5-bf8d-5c08306cd023): mini-stream backing and offset base.
5. [User-defined data](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb/b089deda-be20-4b4a-aad5-fbe68bb19672): stream length, chains and final-sector capacity.
