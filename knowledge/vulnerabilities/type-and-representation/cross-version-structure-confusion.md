---
id: vulnerability-type-cross-version-structure-confusion
title: Cross-version structure size, revision, and feature confusion
kind: vulnerability
topics: [structures, versioning, abi, type-confusion, compatibility]
platforms: [cross-platform]
architectures: [any]
---

# Cross-version structure size, revision, and feature confusion

## Definition and violated invariant

Cross-version structure confusion occurs when a producer and consumer disagree about which fields and layout an object supplies, often because a size, revision, command, feature bitmap, architecture mode, or negotiated capability is missing, trusted incorrectly, or checked against the wrong operation. Every field access must be authorized by the selected revision and contained in the actual supplied object extent.

A larger or smaller structure is not inherently unsafe. Extensible interfaces can deliberately accept compatible prefixes, reserved zero fields, or separately numbered commands when their contracts define how each extent is handled.

## Conditions that establish the issue

Recover the producer's actual allocation or transferred byte count, layout and packing for each supported revision, selector fields, validation path, and every consumer access. Prove a reachable combination selects a field or meaning that the supplied object does not contain or does not define, and trace the resulting value into a memory access, operation, authority decision, or disclosure.

Treat a self-reported size as untrusted metadata until bounded by the transport or allocation extent. A revision check does not validate size, and a size check does not establish field meanings. Include 32-bit compatibility translations, pointer-width changes, optional tails, nested records, and output initialization.

## Evidence that is not sufficient

Multiple structure sizes, a `size` or `version` field, compatibility code, reserved bytes, or an access beyond the oldest layout is not sufficient. The path may require a newer revision and a sufficiently large buffer, or it may copy a safe common prefix.

Different symbolic definitions across SDKs do not prove the shipped peers disagree. Recover the definitions and bytes used by the actual producer and consumer.

## Investigation sequence

Create a revision matrix containing selector values, minimum and maximum accepted extent, field offsets and widths, required feature bits, pointer model, and unknown-field behavior. For the suspect path, bind every check and access to one immutable snapshot or show how a mutable object can change between them.

Compare the claimed extent with the independent allocation or transfer extent, then follow the first revision-specific field into its consumer. On output paths, establish which revision's bytes are initialized and actually returned.

## Constructed Windows x64 example

```c
struct request_v0 { uint32_t size; uint32_t flags; };
struct request_v1 { uint32_t size; uint32_t flags; uint64_t buffer; };

void consume(const struct request_v1 *request)
{
    if (request->size < sizeof(struct request_v0))
        return;
    use_buffer((void *)(uintptr_t)request->buffer);
}
```

```asm
cmp  dword ptr [rcx], 8       ; accepts the v0 prefix size
jb   reject
mov  rax, qword ptr [rcx+8]   ; reads a v1-only field ending at byte 16
```

Under the stated layout and Windows x64 argument placement, `RCX` holds `request`; the check permits a caller that supplied only the eight-byte v0 object while the load requires sixteen accessible bytes. The finding also needs the independent supplied extent; setting the `size` field to eight inside a sixteen-byte allocation would not establish this overread, though it could still select the wrong semantic revision.

## Primitive and impact limits

The direct result can be out-of-bounds access, stale or uninitialized-field use, pointer-width confusion, wrong operation selection, information disclosure, or an authorization error. Exploitability depends on boundary reachability, control of adjacent bytes, later consumers, and active memory and control-flow defenses.

## Related knowledge and primary sources

`reference-native-structure-layout-access`, `reference-native-type-confusion-object-validity`, and `reference-windows-response-structures-initialization` cover layout, discriminator, and outbound-byte evidence. This profile repeats actual-extent and revision binding locally.

Reviewed 2026-10-09 against Linux kernel [ioctl interface guidance](https://docs.kernel.org/driver-api/ioctl.html), including version and 32-bit compatibility concerns, and the C++ [object representation rules](https://eel.is/c++draft/basic.types). The source and assembly are constructed.
