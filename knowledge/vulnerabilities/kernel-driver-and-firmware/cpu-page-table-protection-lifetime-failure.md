---
id: vulnerability-kernel-cpu-page-table-protection-lifetime-failure
title: CPU page-table permission, alias or translation-lifetime failure
kind: vulnerability
topics: [kernel, virtual-memory, page-table, permissions, tlb, aliasing]
platforms: [cross-platform, kernel, virtualization]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# CPU page-table permission, alias or translation-lifetime failure

## Definition and violated invariant

This vulnerability occurs when virtual-memory translation grants the wrong user/supervisor, read/write/execute or ownership access, points to unauthorized physical backing, retains a stale mapping, or exposes a conflicting alias such as writable and executable views contrary to policy. The invariant is that every effective translation and alias must enforce the intended authority for the complete mapping lifetime, including required TLB synchronization.

A page-table entry in memory is not necessarily the translation currently used by a CPU. Cached translations, multiple levels, address-space identifiers, nested translation and aliases can alter the effective result.

## Conditions that establish the issue

Identify requester privilege and address space, virtual range, every translation stage, page size, effective permission combination, physical backing and owner, copy-on-write state, aliases, update order, TLB invalidation and reuse. Prove a reachable access obtains authority outside policy or continues through stale translation after revocation.

For virtualization, preserve guest and host translation stages. For W^X claims, enumerate all aliases to the physical page; one read-only/executable view does not refute a separate writable alias.

## Evidence that is not sufficient

A suspicious PTE bit, writable page, executable mapping, `invlpg`/TLB flush call or equal physical frame is not sufficient. Higher-level entries and privilege controls may further restrict access, mappings may be temporary and authorized, and the CPU may not use the inspected table or context.

Do not infer exploitability from a writable executable page without showing attacker write and reachable execution in the relevant context.

## Investigation sequence

Walk the effective translation from the actual control register/context and virtual address through every level and nested stage. Combine permissions according to the architecture. Map the physical page to owners and all aliases. Draw map, permission change, invalidation acknowledgment, access and reuse in order across CPUs.

At binary level, recover page-table writes, barriers, TLB invalidation and interprocessor synchronization. Identify whether the update changes a live table and whether another CPU or device can access before completion. Preserve huge-page and copy-on-write boundaries.

## Constructed timeline

CPU A removes user write permission from a page-table entry but publishes a security-sensitive object before invalidating CPU B's cached translation. If CPU B can still write through the stale user mapping during that interval, revocation is incomplete.

The finding requires the target architecture to permit the stale use and absence of a required shootdown acknowledgment before publication. A local PTE store alone is not proof.

## Primitive and impact limits

Direct effects include unauthorized read/write/execute, cross-address-space access, stale-page access or policy bypass. Kernel or hypervisor execution requires control of executable content or a privileged target and active mitigations; a translation fault is not a bypass.

## Related knowledge and primary sources

IOMMU mappings use a different device translation boundary. This profile keeps CPU effective translation, aliases and TLB lifetime together.

Reviewed 2026-10-09 against the [Intel 64 and IA-32 Software Developer Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html), Arm [A-profile memory management guidance](https://developer.arm.com/documentation/101811/latest/) and RISC-V [Supervisor address translation and `SFENCE.VMA`](https://docs.riscv.org/reference/isa/priv/supervisor.html). The timeline is hypothetical and architecture-specific rules must be applied.
