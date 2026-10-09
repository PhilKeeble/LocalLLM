---
id: vulnerability-parser-header-field-extent-before-access
title: Header, record, or field access before extent validation
kind: vulnerability
topics: [parsers, bounds, headers, records, field-access]
platforms: [cross-platform]
architectures: [any]
---

# Header, record, or field access before extent validation

## Definition and violated invariant

An early field-access vulnerability occurs when a parser reads a header, record or field before proving that the complete accessed byte range lies within the available input or containing object. Every access at offset O with width W must be justified by the correct base and extent before the load, including accesses used to obtain a later length or tag.

Recognizing a magic value or nominal structure type does not establish that the input contains the rest of that structure. Fixed-size machine loads can cross the available boundary even when only one decoded byte is later used.

## Conditions that establish the issue

Recover the input base, independently known available extent, cursor, access offset and instruction width, arithmetic domain, and order of checks. Prove a reachable path performs a load whose end exceeds that extent before an effective check or guaranteed capture, and connect the read to an attacker-controlled truncation or boundary.

For streaming parsers, distinguish bytes requested from bytes actually returned and buffered. For mapped files or shared buffers, readable adjacent memory does not enlarge the logical record and can convert a fault into disclosure or cross-record parsing.

## Evidence that is not sufficient

A structure cast, wide load, field access, truncated sample, or bounds check after decompilation is not sufficient. The caller may guarantee a complete fixed header, the OS may have copied a fixed-size request, an earlier dominating check may cover the range, or the load may be speculative in decompiler output but unreachable in machine control flow.

A load remaining inside the allocation can still violate a nested record boundary, but that is a separate containment claim that needs the selected grammar.

## Investigation sequence

Start at the first machine read from each untrusted input and annotate base, offset, width and dominating extent facts. Treat every decoded length, tag or version as unavailable until the bytes containing it are proven present. Follow short-read, end-of-input and error paths separately.

Then determine whether the accessed range crosses only a logical record or the backing allocation and trace the value into parsing, copying, output or dispatch. Preserve integer width when calculating end offsets.

## Constructed Windows x64 example

Assume `RCX` is `buffer` and `RDX` is the available byte count.

```asm
mov  eax, dword ptr [rcx+4]   ; reads bytes 4..7 before proving an 8-byte header exists
cmp  rdx, 8
jb   truncated
```

For an input shorter than eight bytes, the load precedes the check and crosses the supplied extent. Whether it faults, reads adjacent mapped bytes or remains inside a larger transport allocation depends on the boundary, but the field value was not obtained from a complete supplied header. An earlier caller guarantee or fixed-size capture can refute the finding and must be traced.

## Primitive and impact limits

The direct result can be out-of-bounds read, cross-record interpretation, fault, information disclosure, or control decisions based on unrelated bytes. Further corruption or code execution requires a downstream write, allocation, dispatch or lifetime consequence.

## Related knowledge and primary sources

`reference-parser-wire-fields-lengths-tags`, `reference-parser-container-boundaries-integrity`, and native range-arithmetic references cover field and extent recovery. This profile repeats the before-access proof locally.

Reviewed 2026-10-09 against the PNG [chunk layout and length rules](https://www.w3.org/TR/png-3/), CBOR [well-formed input rules](https://www.rfc-editor.org/rfc/rfc8949.html), and [MITRE CWE-125](https://cwe.mitre.org/data/definitions/125.html). The assembly is constructed.
