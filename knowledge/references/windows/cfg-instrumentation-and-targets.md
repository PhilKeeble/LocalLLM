---
id: reference-windows-cfg-instrumentation-targets
title: Windows CFG instrumentation, target validity and process policy
kind: reference
topics: [windows, mitigations, cfg, indirect-calls, load-config, dynamic-code]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# A valid indirect target is not an authorized operation

Control Flow Guard combines compiled checks, target metadata and OS support.
Investigate the actual transfer site and destination. CFG does not repair the
memory-corruption or logic defect that supplied an unintended value.

## Compiler instrumentation and linker metadata are separate obligations
Reviewed 2026-10-02. MSVC /guard:cf analyzes indirect targets and adds checks;
the compiler and linker options are both required, with /DYNAMICBASE. Separate
compile/link invocations need the appropriate options at both stages. The
optimizer may omit checks it proves unnecessary; VS 2017+ also guards jump-table
switches. [1]

Code compiled without checks can coexist with instrumented objects. A linked
image advertising CFG therefore does not establish that every indirect transfer
is checked. Conversely, an absent nearby helper call is not enough to prove a
gap: inspect the generated transfer, optimizer reasoning where available and
architecture/toolchain-specific dispatch sequence. Do not rename a mitigation
helper into application behavior merely because it dominates an indirect call.

## Headers identify declared CFG data, not runtime coverage
The PE optional-header IMAGE_DLLCHARACTERISTICS_GUARD_CF value is 0x4000. [2]
Load-config GuardFlags separately declare instrumentation and function-ID (FID)
table presence. [1] These are image metadata, not a record of executed checks.

Preserve load-config size, table bounds, pointers, entry encoding and call-site
evidence; primary format rules live in format-pe-directories-loader-metadata.
An absent or malformed table requires interpretation against the actual loader,
not a conclusion from a GUI badge. A present table does not prove that a loaded
copy matches disk or that the OS enforces the check on the path under review.

## CFG enablement, export suppression and strict loading are not one bit
PROCESS_MITIGATION_CONTROL_FLOW_GUARD_POLICY separates EnableControlFlowGuard,
EnableExportSuppression and StrictMode. With export suppression, exports start
as invalid indirect targets and GetProcAddress resolution can make them valid.
StrictMode requires CFG-enabled loaded DLLs. It can be enabled at runtime but
not subsequently disabled; enablement and export suppression cannot be changed
using SetProcessMitigationPolicy. [3]

Investigative consequence: a resolved export is not a policy violation merely
because it was initially suppressed. Check query success and process generation
using reference-windows-dep-aslr-policy. EnableXfg/EnableXfgAuditMode appear in
the current structure, but their names and the page's minimum-OS table alone
do not establish XFG algorithm, deployment or enforcement on an older target.

## Executable dynamic memory has its own CFG target-state transitions
Executable page allocation normally marks locations valid for CFG.
PAGE_TARGETS_INVALID changes that initial state. PAGE_TARGETS_NO_UPDATE preserves
CFG information across a VirtualProtect change to executable protection; the
default transition otherwise marks locations valid. Both constants equal
0x40000000, but PAGE_TARGETS_INVALID is not supported by VirtualProtect. [4]

Decode the callee and transition before naming the bit. A hex constant alone
does not distinguish allocation policy from preservation policy. Executable
permission and CFG target validity are separate properties: an RX mapping is
not evidence that only a narrow list of intended entry points is callable.

## Dynamic target registration uses range-relative offsets
SetProcessValidCallTargets updates target validity within an executable region.
Its entries are offsets relative to the supplied region, not absolute VAs or
PE RVAs; the documentation specifies 16-byte alignment and ascending order.
It returns BOOL and does not succeed when CFG is disabled for the process. [5]

Constructed coordinate example: region base 0x10000000 and offset 0x30 identify
VA 0x10000030. This arithmetic is not API execution or proof of registration.
Inspect the return and per-entry state, region identity/lifetime and later
protection changes. An attempted registration is not a successfully allowed
target, and an allowed address is not proof of the intended function signature.

## CFG compatibility does not mean universal control-flow or data integrity
Microsoft documents mixed CFG/non-CFG code and compatibility on CFG-unaware
Windows, with protection gaps when code is not instrumented. [6]
Investigative inference: being in a permitted target set does not establish
correct object type, call arguments, caller authority or application state.
Separate a valid-target wrong-operation bug from transfer to a disallowed address.

Returns and exceptional context restoration need their own evidence; see
reference-windows-cet-shadow-stack. Do not call every crash a CFG detection,
or every surviving corrupt input a CFG bypass. Preserve the actual fault/check
and the earlier defect independently of exploitability assumptions.


## Sources and limits
Primary contracts reviewed 2026-10-02; no bypass or target policy change claimed.

1. [MSVC guard option](https://learn.microsoft.com/en-us/cpp/build/reference/guard-enable-control-flow-guard?view=msvc-170): build stages, optimization, dump inspection.
2. [PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): DllCharacteristics.
3. [CFG policy](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_control_flow_guard_policy).
4. [Memory protection constants](https://learn.microsoft.com/en-us/windows/win32/memory/memory-protection-constants): PAGE_TARGETS_INVALID/NO_UPDATE.
5. [SetProcessValidCallTargets](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-setprocessvalidcalltargets).
6. [CFG platform guidance](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard): mixed and unaware environments.
