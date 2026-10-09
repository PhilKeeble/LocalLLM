---
id: vulnerability-memory-invalid-pointer-dereference
title: Null, wild, noncanonical, or unmapped pointer dereference
kind: vulnerability
topics: [memory-safety, pointers, null-dereference, invalid-address, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Null, wild, noncanonical, or unmapped pointer dereference

## Definition and violated invariant

An invalid-pointer vulnerability occurs when execution reads, writes, or transfers control through a value that does not designate a suitably aligned, live, accessible object or callable target for the operation. Null, uninitialized or wild, out-of-range, noncanonical, unmapped, and permission-incompatible values are different causes and can raise different target exceptions.

A dangling pointer has a lifetime defect and belongs with use-after-free analysis. A pointer into the wrong live object may instead be type confusion or an out-of-bounds access. Preserve the most specific root cause rather than grouping every faulting address as a null dereference.

## Conditions that establish the issue

Identify the pointer's origin, validation, transformations, address space, required object and lifetime, access width, permissions, and consuming instruction. Prove an attacker-reachable or otherwise security-relevant path supplies an invalid value and reaches the dereference before a check, exception, or failure return stops it.

For noncanonical or tagged values, apply the actual architecture and platform rules. Mapping status from one observation is not a timeless object-validity proof, and numerical address zero does not imply a useful mapped null page.

## Evidence that is not sufficient

A nullable return type, a missing comparison in one basic block, a pointer-shaped integer, or a fault near address zero is not sufficient. A dominating check, language runtime trap, fault recovery boundary, valid sentinel, or target-specific address transformation may explain the path.

An invalid dereference usually supports an availability finding. Claims of read, write, privilege escalation, or code execution need evidence that the invalid address is mapped or can be influenced into a usable target with the required permissions.

## Investigation sequence

Trace the pointer from producer through error or sentinel returns, integer conversions, tagging, base adjustments, synchronization, and final use. Inspect all predecessors for validation and all concurrent writers for changes after a check. Recover the exact effective address and access type from instructions.

Correlate the address with the target's mappings and privilege context at the relevant time. For a call or jump, also validate executable permission and target policy; for data, validate full width, alignment where required, and object extent.

## Constructed source example

This hypothetical lookup returns null for an absent attacker-selected identifier, but the caller immediately reads a field:

```c
uint32_t selected_flags(uint32_t identifier)
{
    const struct record *record = find_record(identifier);
    return record->flags;
}
```

The issue requires an identifier that makes `find_record` return null and a path on which the language or generated binary performs the field access. A wrapper that throws, returns a valid sentinel object, or proves every identifier present would change the result.

## Constructed Windows x64 representation

Under Windows x64 the identifier arrives in `ECX`; a pointer result is returned in `RAX`:

```asm
call find_record
mov  eax, dword ptr [rax+8] ; no null check before field load
ret
```

If the call returns zero, the machine attempts a four-byte load at virtual address `0x8`. Whether that faults is a mapping and privilege question; do not infer code execution from the missing test or apply x86-64 canonical-address behavior to another architecture.

## Primitive and impact limits

The direct primitive is an invalid read, write, or indirect transfer. A deterministic unhandled fault can terminate a process or crash privileged code; service-level impact depends on restart, isolation, and request reachability.

Stronger impact requires a controllable mapped target, useful data flow, and any required bypass of memory permissions or control-flow defenses. Near-null access is not automatically exploitable merely because it occurs in a privileged component.

## Related knowledge and primary sources

`architecture-machine-representation` distinguishes pointer-looking integers from usable pointers, while `reference-native-type-confusion-object-validity` covers live-object validity. This profile repeats the mapping, object, and consumer proof needed independently.

Reviewed 2026-10-09 against [MITRE CWE-476](https://cwe.mitre.org/data/definitions/476.html), [MITRE CWE-822](https://cwe.mitre.org/data/definitions/822.html), C pointer and undefined-behavior rules in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention). The source and assembly are constructed.
