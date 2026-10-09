---
id: vulnerability-kernel-windows-mdl-pinned-page-lifetime-misuse
title: Windows MDL, pinned-page or system-mapping lifetime misuse
kind: vulnerability
topics: [kernel, windows, drivers, mdl, pinned-pages, mapping, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows MDL, pinned-page or system-mapping lifetime misuse

## Definition and violated invariant

This vulnerability occurs when a driver confuses an MDL's descriptor, page-lock, virtual mapping, byte range, permissions or ownership lifetime. The invariant is that the MDL must describe the intended range, pages and required mapping must remain valid for every CPU or device use, and release must match how each resource was acquired.

Allocating an MDL does not lock pages or create a system mapping. Locked physical pages do not freeze contents or preserve the original user virtual address; another writable alias can still mutate them.

## Conditions that establish the issue

Identify MDL construction path, original address space, byte offset/count, successful probe/lock, access direction, system or user mapping, caller process, asynchronous users, DMA completion and each unlock/unmap/free. Prove a use occurs without required locking/mapping, outside the described range, under wrong permissions or after a dependent resource is released.

For content races, show validation uses one snapshot and later device or CPU access can observe attacker mutation. The MDL alone is not an immutability mechanism.

## Evidence that is not sufficient

An `MdlAddress`, call to `MmGetMdlVirtualAddress`, missing `MmUnlockPages` or mapping call is not sufficient. The MDL may describe nonpaged pool, inherit a mapping, be a partial MDL with different cleanup, or be released by an owning request. API choice determines duties.

Do not infer physical contiguity from an MDL or treat internal MDL offsets as a cross-version serialized ABI.

## Investigation sequence

Create separate ledger entries for descriptor storage, backing pages, page lock, system mapping, user mapping and request/device ownership. Mark acquisition success because probe/lock and user mapping can raise while system mapping can return null. Track process context for original and user virtual addresses.

At binary level, trace calls rather than private MDL fields where possible. Recover byte count and offset into every mapped access. Follow request completion, cancellation and DMA fence so cleanup cannot precede last use.

## Constructed timeline

A hypothetical driver locks user pages, maps them for the device and completes the request immediately, unlocking and freeing the MDL while DMA remains pending. The device later writes through the stale mapping. The finding requires that request completion owns cleanup and that no independent device reference or completion fence retains the pages.

## Primitive and impact limits

The direct result can be stale DMA, access to reassigned pages, invalid mapping use, user-visible kernel-page disclosure or denial of service. Arbitrary kernel read/write requires control of address, extent, direction and timing; elevation requires a reachable authority gain.

## Related knowledge and primary sources

`reference-windows-driver-mdl-lifetimes` provides construction-specific cleanup rules, and request-rundown references provide completion ordering. This profile repeats the descriptor/page/mapping separation locally.

Reviewed 2026-10-09 against Microsoft [Using MDLs](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/using-mdls), [`MmProbeAndLockPages`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmprobeandlockpages), [`MmGetSystemAddressForMdlSafe`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmgetsystemaddressformdlsafe) and [`MmMapLockedPagesSpecifyCache`](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmmaplockedpagesspecifycache). The timeline is constructed.
