---
id: vulnerability-memory-partial-nested-range-validation
title: Partial validation of nested offsets and trailing ranges
kind: vulnerability
topics: [memory-safety, offsets, ranges, parsers, nested-structures]
platforms: [cross-platform]
architectures: [any]
---

# Partial validation of nested offsets and trailing ranges

## Definition and violated invariant

A partial nested-range vulnerability occurs when an outer record, table, pointer, or header is in bounds but a child offset, length, count, terminator, or trailing payload derived from it is consumed without its own proof. Every dereferenced level must fit the same immutable input snapshot or the correctly identified child object after coordinate conversion.

For nonnegative byte values, a child range at offset `O` with length `L` in extent `N` requires `O <= N` and then `L <= N-O`. Validating only the child header does not validate payloads or strings referenced by that header.

## Conditions that establish the issue

Recover each base used by an offset, its numeric width and signedness, the containing extent, and the full access width. Prove a feasible input for which the validated outer object is accepted but a nested access leaves its intended live range. Repeat the proof after alignment, decompression, relative-pointer resolution, or file-to-memory translation.

If validation and use can observe different bytes, establish snapshot binding or analyze the mutable double-fetch separately. A verifier call is relevant only when its result dominates access to the same representation under the correct schema.

## Evidence that is not sufficient

An offset addition, nested pointer, flexible record, or absent local comparison is not sufficient. A dominating verifier may cover the child, the format may constrain a value through a parent invariant, or the consumer may pass the range to a checked accessor that rejects it.

Do not assume offsets are relative to file start. They may be relative to their own field, a section, record, table, virtual base, or another coordinate system.

## Investigation sequence

Draw an offset tree whose edges name the encoded value, base, conversion, target header, and target payload. At every edge, record the check and the exact bytes it covers. Follow the accepted path to the final load, copy, string scan, or callback rather than stopping at an in-range address.

In assembly, identify whether arithmetic uses the original buffer base or an interior pointer and whether loads occur before the guarding branch. Check count-times-stride and offset-plus-length with subtraction-based bounds, preserving operand widths.

## Constructed source example

This hypothetical parser validates a directory and copies its first entry, then trusts the entry's child range:

```c
int parse_blob(const uint8_t *buffer, size_t size)
{
    struct header h;
    struct entry e;
    if (size < sizeof h)
        return -1;
    memcpy(&h, buffer, sizeof h);
    if (h.count == 0 || h.directory_offset > size ||
        h.count > (size - h.directory_offset) / sizeof e)
        return -1;
    memcpy(&e, buffer + h.directory_offset, sizeof e);
    return consume_payload(buffer + e.data_offset, e.data_length);
}
```

The directory proof does not establish `e.data_offset <= size` and `e.data_length <= size - e.data_offset`. The issue requires `consume_payload` to access the supplied range without independently rejecting it; a verified accessor there would refute this path.

## Constructed offset-flow representation

The essential binary flow can be represented without assuming a calling convention:

```asm
directory = buffer + checked_directory_offset
data_offset = load_u32(directory + entry_data_offset_field)
data_length = load_u32(directory + entry_data_length_field)
payload = buffer + data_offset
call consume_payload(payload, data_length)
```

An outer bounds branch does not cover the last addition and range unless its proven invariant explicitly constrains these loaded child fields. Confirm byte order and field widths before assigning the values.

## Primitive and impact limits

The direct primitive depends on the child consumer: out-of-bounds read or write, unterminated scan, invalid callback selection, or resource exhaustion are distinct results. Record the first unchecked child edge and first concrete invalid operation.

A malformed file or rejected child is not a vulnerability. Disclosure or execution requires observable data flow or a control-bearing write beyond the structural parsing defect.

## Related knowledge and primary sources

`format-malformed-files-loader-acceptance` defines table and child-range separation, while `reference-parser-offset-based-serialization` covers relative bases and verifier boundaries. This profile repeats the per-level proof required for isolated use.

Reviewed 2026-10-09 against [MITRE CWE-125](https://cwe.mitre.org/data/definitions/125.html), [MITRE CWE-787](https://cwe.mitre.org/data/definitions/787.html), the [FlatBuffers format internals](https://flatbuffers.dev/internals/), and C object/library rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf). The source structures and pseudodisassembly are constructed and deliberately leave their serialized field encoding target specific.
