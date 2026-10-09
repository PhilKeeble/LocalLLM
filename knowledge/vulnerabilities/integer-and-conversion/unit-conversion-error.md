---
id: vulnerability-integer-unit-conversion-error
title: Unit conversion error in security-relevant quantities
kind: vulnerability
topics: [integers, units, sizes, time, blocks, characters]
platforms: [cross-platform]
architectures: [any]
---

# Unit conversion error in security-relevant quantities

## Definition and violated invariant

A unit-conversion vulnerability occurs when validation, arithmetic, allocation, or use treats a quantity as a different unit without an exact, representable conversion. Common domains include bits and bytes, elements and bytes, characters and code units, blocks and sectors, pages and bytes, samples and channels, and ticks and wall-clock units.

The numeric value alone is insufficient. Every security-relevant edge must preserve both magnitude and unit, including rounding direction and whether headers, padding, or sentinels are included.

## Conditions that establish the issue

Identify the producer's unit, conversion factor or formula, numeric domain, rounding, destination unit, and consumer. Prove a feasible value passes a check expressed in the wrong unit or yields a smaller resource than the operation requires, then reaches a concrete unsafe or policy-relevant effect.

For variable-width encodings and calendars, a constant multiplier may not define the conversion. Use the selected encoding, format, clock, or API contract rather than a convenient maximum or average.

## Evidence that is not sufficient

A scale instruction, unit-suffixed field, or differing parameter names is not sufficient. A wrapper may already convert the value, bounds may be conservative in the safe direction, or the quantities may intentionally describe different layers.

Correct conversion does not prove arithmetic representability or object capacity; those remain separate checks.

## Investigation sequence

Annotate every relevant value with unit, width, signedness, inclusion rules, and represented object. Follow scale, division, rounding, narrowing, and API calls. Compare the exact checked quantity with the exact consumer parameter.

At machine level, associate shifts and multiply constants with corroborated format or API semantics. Do not infer sector size, page size, character width, or timer frequency from one familiar constant when the target can negotiate or configure it.

## Constructed source and assembly example

```c
int read_blocks(void *destination, size_t destination_bytes,
                uint32_t block_count)
{
    if (block_count > destination_bytes)
        return -1;
    return device_read(destination, block_count * 512u);
}
```

With `destination_bytes == 4096` and `block_count == 16`, the check accepts but requests 8192 bytes. A binary can show `cmp block_count,destination_bytes` followed by `shl byte_count,9` before the consumer. The example assumes fixed 512-byte blocks and a representable product; recover both facts from the real interface.

## Primitive and impact limits

The direct primitive is a mismatched quantity. Consequences can include out-of-bounds I/O, underallocation, excessive timeout, quota bypass, or incorrect object selection.

Severity depends on the final consumer and whether the incorrectly scaled value is rejected, clipped, or used. Unit disagreement alone does not establish corruption.

## Related knowledge and primary sources

`reference-native-text-encoding-size-units` covers text conversions, while `reference-native-integer-size-buffer-arithmetic` covers scaling. This profile repeats the unit ledger requirement locally.

Reviewed 2026-10-09 against [MITRE CWE-681](https://cwe.mitre.org/data/definitions/681.html), C integer rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and Microsoft [`WideCharToMultiByte`](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte) as a primary example of input code-unit and output-byte distinctions. The source and instruction pattern are constructed.
