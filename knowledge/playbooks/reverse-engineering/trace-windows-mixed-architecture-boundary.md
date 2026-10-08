---
id: playbook-re-windows-mixed-architecture
title: Trace Windows WOW64 and ARM64EC representation, namespace and call boundaries
kind: playbook
topics: [wow64, arm64ec, arm64x, thunking, structure-layout, reverse-engineering]
platforms: [windows]
architectures: [x86, x64, arm, arm64]
---
# Recover a Windows mixed-architecture boundary

## Record separate identities before choosing a decoder

Record OS/build, native machine, target process, module identity, object-versus-PE
artifact type and current code range. Save architecture-query success and output
separately. For a dump, record captured memory and context types; for a live
target use only an authorized coherent stop. Do not infer the target's widths
from the analysis process or its filesystem view.

Use reference-windows-wow64-layouts-views for WOW64, and
reference-windows-arm-hybrid-images for EC/X loader views. Determine whether
the transition changes pointer width, instruction set, calling convention,
address space, trust level or only namespace view. These are independent axes:
an EC/x64 transition is not a 32-to-64-bit buffer conversion or privilege change.

## Recover both sides of every data representation

For IPC or an IOCTL, recover caller layout, receiver layout, packing, length
units, version/tag fields and pointer/handle/offset meanings. Mark which layer
converts each field. Inspect the original request's architecture before selecting
native sizeof checks. Capture/conversion must precede use of the converted data.

Constructed review: a 32-bit caller submits a 16-byte pointer-bearing record;
a 64-bit receiver assumes its 32-byte native record. Show the exact out-of-range
load or incorrect field binding, not merely the existence of different sizes.
Conversely, separately validated fixed-width serialized records can be correct
without matching host struct layouts. No architecture conversion itself validates
embedded addresses, authorizes an operation or pins asynchronous storage.

## Reconstruct the call across adapters before assigning a prototype

For EC/x64 calls, annotate the body, entry thunk, exit thunk, checker, facade
and final destination separately. Track the target register before and after
checker execution. Recover the actual signature, aggregate eligibility, hidden
return storage and variadic status using abi-windows-arm64ec-boundaries.

Do not propagate the saved-context register overlay as a universal argument
map. Check whether an apparent extra argument is a thunk destination or varargs
descriptor. A shared adapter or duplicate export alias is not necessarily a
second semantic function. Verify the loaded view before diagnosing a pointer
as targeting the wrong ISA or a return register as corrupted.

## Trace the resolved namespace and lifetime of temporary state

Record path/root, caller architecture, registry-view flags, filesystem redirection
state and resolved object. Compare validation and consumption using those full
identities. Do not assume the same path spelling or registry key text selects
the same object for a helper of another architecture.

For temporary redirection changes, trace restoration on each successful-disable
path and any callbacks/delay loads within the scope. Registry view flags are a
different mechanism. Prefer inspecting recorded state rather than modifying
system configuration. The facts and limitations are in
reference-windows-wow64-layouts-views.

## Report a falsifiable mismatch, not just unusual assembly

Deliver both representation/ABI contracts, the conversion or missing conversion,
the exact consumer, a feasible sequence and target/build limits. Classify the
result as demonstrated mismatch, compatible adaptation or unresolved evidence.
An emulator helper, fast-forward export, unknown process-machine result or
transformed ARM64X header is not independently a vulnerability.

Sufficiency question: can another investigator reconstruct the failing field,
call argument or object binding without guessing architecture from a filename?
If the answer depends on missing range metadata or an unavailable context,
retain that gap rather than asserting a defect. Evidence from one execution
mode does not establish behavior in another mode.

## Primary-source basis and scope

Reviewed 2026-10-02. Constructed investigation method, not a target reproduction.

- [32-bit I/O in 64-bit drivers](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/supporting-32-bit-i-o-in-your-64-bit-driver): payload conversion boundary.
- [ARM64EC ABI](https://learn.microsoft.com/en-us/windows/arm/arm64ec-abi): signature-dependent adapters and checkers.
- [ARM64X PE](https://learn.microsoft.com/en-us/windows/arm/arm64x-pe): loader-dependent image views.
- [Filesystem redirector](https://learn.microsoft.com/en-us/windows/win32/winprog64/file-system-redirector) and [alternate registry views](https://learn.microsoft.com/en-us/windows/win32/winprog64/accessing-an-alternate-registry-view): namespace selection, not authorization.
