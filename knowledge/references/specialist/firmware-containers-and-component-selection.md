---
id: reference-firmware-container-component-evidence
title: Firmware containers, compressed payloads, partitions and selected components
kind: reference
topics: [firmware, containers, compression, partitions, filesystems, component-selection]
platforms: [embedded, uefi, linux]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---
# Firmware storage and selection evidence

## FIT component metadata distinguishes storage, loading and selection

U-Boot FIT describes image components and configurations selecting components.
Image data can be inline or external; load and entry properties describe loading
and execution addresses rather than offsets into the containing file. Compression
metadata describes the loader's treatment of that component; already compressed
content can be marked none when the loader must not decompress it. [1]

Bind every extracted component to its parent, storage extent, transformation and
selected configuration. A plausible executable or compression signature is a
candidate, not proof of boot selection. These are FIT concepts, not a schema for
every vendor update package; validate the actual container and consumer.

## PI firmware volumes contain typed files and nested sections

UEFI PI firmware volumes identify their filesystem format by GUID. PI FFS is a
flat filesystem of GUID-named files, not a directory tree; file data can contain
typed sections, including compression encapsulation of other sections. [2]

Preserve volume, file and section ancestry and distinguish compressed storage
extent from decoded extent. GUID matches help identify a format or file but do
not certify its contents, authentication or dispatch. Volume boundaries and
section lengths must fit their containing objects. Other firmware filesystems
need their own contract; an FFS interpretation is not universal.

## Raw flash, managed volumes and filesystems are different layers

Linux UBIFS operates on UBI volumes. UBI supplies volume management and wear
leveling above MTD flash; JFFS2 instead operates on MTD devices. UBIFS and JFFS2
are different on-media formats. [3]

Identify which layer a capture contains before interpreting filesystem offsets
or declaring missing files. Preserve partition/volume origin, eraseblock or
logical-block coordinates, filesystem and component role. A logical volume is
not automatically a byte-for-byte raw-chip image. This layered interpretation
does not imply every firmware uses UBI, a partition table or a filesystem.

## GPT partition extents use logical blocks, not byte offsets

UEFI GPT entries define a partition from StartingLBA through EndingLBA inclusive;
their type GUID describes the partition's intended type. LBA means logical block
address, and conversion to a byte extent needs the medium's logical block size. [4]

Bind table origin, block size, containing image extent and partition identity
before locating a component. Do not assume every block is 512 bytes or interpret
the end address as an exclusive bound. A partition type/name is not evidence of
the actual filesystem, trusted publisher or selected boot path. Vendor partition
maps and raw-flash layouts require their own coordinate contract.

## Component presence does not establish installed or running identity

An update container can describe components whose eventual selection and address
depend on its consumer, as FIT configurations illustrate. [1] Record whether
evidence is a distribution package, stored slot, decoded image or execution
capture. Connect selected slot/configuration to the executable and data consumed.
Recovery copies, unused alternatives and stale storage must remain separate.

Hashes can preserve artifact identity without proving publisher trust or that
the device ran those bytes. Workflow: playbook-specialist-firmware-evidence;
shared containment facts: format-packages-archives-contained-images.

## Sources and scope

Reviewed 2026-10-08. Editions below establish provenance, not required target
releases. No vendor-private offsets or assumed boot policy are imported.

1. [FIT source format](https://docs.u-boot.org/en/v2023.10/usage/fit/source_file_format.html): image/configuration nodes, external data, load/entry and compression properties.
2. [PI storage design](https://uefi.org/specs/PI/1.8/V3_Design_Discussion.html): sections 2.1-2.2, FFS and section types; primary indexed text inspected.
3. [UBIFS introduction](https://docs.kernel.org/filesystems/ubifs.html): MTD/UBI/UBIFS layering and JFFS2 distinction, rolling upstream.
4. [UEFI 2.10 GPT](https://uefi.org/specs/UEFI/2.10/05_GUID_Partition_Table_Format.html): section 5.3.3 partition extents and type identity.
