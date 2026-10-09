---
id: vulnerability-parser-nested-object-descriptor-chain-bounds
title: Nested object, table, section, or descriptor-chain bounds failure
kind: vulnerability
topics: [parsers, nesting, tables, sections, descriptors, bounds]
platforms: [cross-platform]
architectures: [any]
---

# Nested object, table, section, or descriptor-chain bounds failure

## Definition and violated invariant

A nested-bounds vulnerability occurs when a parser validates an outer container but fails to validate every child range, table entry, indirect reference or descriptor edge before following it. Each hop must use the base, extent, alignment, type and cycle rules defined for that edge, and the complete traversal must remain within its permitted graph and resource bounds.

One valid descriptor does not validate the object it names. A target in the overall allocation can still overlap metadata, another tenant's region, a sibling record or a forbidden section.

## Conditions that establish the issue

Recover the root boundary, descriptor count and stride, every offset/length pair, reference base, type or tag, alignment, target extent, next-link semantics, termination rule, and visited-node or depth accounting. Prove a feasible chain reaches an invalid or unauthorized range or continues without a required bound and that the parser reads, writes or dispatches through it.

Validate arithmetic before pointer formation at every level. Include tables whose entries select other tables, section-to-file coordinate conversions, scatter/gather descriptors and device-owned rings.

## Evidence that is not sufficient

Multiple indirections, a linked list in input, a target outside its immediate descriptor, a repeated node, or one missing nearby comparison is not sufficient. The format may permit root-relative references, cycles may be legal under bounded semantics, and a common verifier may dominate all accesses.

Successful validation of the root or descriptor array does not prove the pointed-to payloads are valid.

## Investigation sequence

Draw the parsed object graph with each edge labeled by encoded field, base, unit, width, permitted target domain and check. Follow both parser cursor movement and nonlocal references. Record visited identity, depth and total work separately from byte containment.

At each terminal consumer, trace the exact bytes and type reached. Check overlaps and aliasing because two individually in-range children may violate non-overlap or ownership rules.

## Constructed descriptor-table example

```c
struct descriptor { uint32_t offset; uint32_t length; };

for (uint32_t i = 0; i < header->descriptor_count; ++i) {
    const struct descriptor *entry = &table[i];
    if (entry->offset <= file_length && entry->length <= file_length - entry->offset)
        parse_child(section_base + entry->offset, entry->length);
}
```

The code can validate each target against `file_length` while adding the offset to `section_base`, repeating the wrong-container error for every edge. It also needs an independent proof that `table[i]` itself lies within the descriptor table before reading the entry. Establish the format's actual bases and array extent before calling either access invalid.

## Primitive and impact limits

The direct result can be out-of-bounds or cross-object access, cycle-driven denial of service, arbitrary device or guest memory reference, overlapping writes, or type confusion. Impact depends on the terminal operation and boundary crossed.

## Related knowledge and primary sources

`reference-parser-container-boundaries-integrity`, `reference-parser-offset-based-serialization`, and specialist ring/DMA references cover nested references. This profile repeats per-edge validation and traversal bounds locally.

Reviewed 2026-10-09 against CBOR [nested-container rules](https://www.rfc-editor.org/rfc/rfc8949.html), FlatBuffers [internals](https://flatbuffers.dev/internals/), and Linux kernel [DMA API guidance](https://docs.kernel.org/core-api/dma-api-howto.html). The source is constructed.
