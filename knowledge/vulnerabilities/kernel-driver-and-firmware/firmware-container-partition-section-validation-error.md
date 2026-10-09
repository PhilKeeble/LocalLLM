---
id: vulnerability-kernel-firmware-container-partition-section-validation-error
title: Firmware container, partition, section or decompression validation error
kind: vulnerability
topics: [firmware, containers, partitions, sections, decompression, bounds]
platforms: [embedded, uefi]
architectures: [any]
---

# Firmware container, partition, section or decompression validation error

## Definition and violated invariant

This vulnerability occurs when firmware parsing accepts a component, partition, file, section or decoded payload whose extent, nesting, type or coordinate system is inconsistent with its containing object and eventual consumer. The invariant is that every stored and decoded range must fit its parent with checked arithmetic, preserve its unit and identity, and produce bounded output before selection or execution.

Storage offsets, logical block addresses, load addresses and run addresses are distinct. Compressed input extent, declared decoded size and actual cumulative output are also separate values.

## Conditions that establish the issue

Identify the exact container format and consumer, parent extent, header variant, offset and length units, nesting, compression method, output budget, component identity and selected configuration. Prove attacker-controlled firmware bytes reach an out-of-range access, underallocation, excessive expansion or wrong component selection before rejection.

For partition tables, include medium block size and whether ending coordinates are inclusive. For nested firmware sections, validate every ancestor rather than only the innermost object.

## Evidence that is not sufficient

A compression signature, GUID, executable header, large length, overlapping partition or parser rejection is not sufficient. The object may be unused, recovery-only, outside the selected configuration or safely rejected. A plausible extracted component does not prove installed or executed identity.

Do not transfer UEFI PI, FIT, GPT or vendor-package rules between formats merely because field names resemble one another.

## Investigation sequence

Build a containment tree with stored offset, stored length, decoded length, type and parent for every object. Preserve bytes versus blocks and inclusive versus exclusive ends. Trace selection from manifest/configuration to the parser and loader that consumes the component.

At binary level, annotate arithmetic width, endianness and comparisons before pointer formation or allocation. Follow decompressor progress and aggregate output across nested sections. Join the parsed load/entry address to the target memory map and later control transfer.

## Constructed extent example

A hypothetical partition entry stores `start_lba=100`, `end_lba=199` inclusive on a medium with 4096-byte logical blocks. Its byte extent is 100 blocks, or 409600 bytes, starting at byte 409600. Treating `end_lba` as exclusive yields 99 blocks and can misplace the following validation boundary.

The arithmetic is illustrative; the format must actually define inclusive LBAs and the medium's logical block size must be established.

## Primitive and impact limits

Direct effects include out-of-bounds read/write, excessive resource use, wrong component extraction or loading and denial of service. Persistent firmware execution requires successful authentication/authorization, installation, selection and control transfer or a demonstrated bypass of those stages.

## Related knowledge and primary sources

`reference-firmware-container-component-evidence` and decompression profiles supply detailed format and output contracts. This profile keeps containment and selected-consumer evidence together.

Reviewed 2026-10-09 against UEFI PI [firmware storage design](https://uefi.org/specs/PI/1.8/V3_Design_Discussion.html), UEFI [GPT partition entries](https://uefi.org/specs/UEFI/2.10/05_GUID_Partition_Table_Format.html), U-Boot [FIT format](https://docs.u-boot.org/en/latest/usage/fit/source_file_format.html) and [RFC 8878](https://www.rfc-editor.org/rfc/rfc8878.html). The extent example is constructed.
