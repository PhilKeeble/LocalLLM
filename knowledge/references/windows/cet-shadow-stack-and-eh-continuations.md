---
id: reference-windows-cet-shadow-stack
title: Windows CET shadow-stack compatibility, audit policy and EH continuations
kind: reference
topics: [windows, mitigations, cet, shadow-stack, ehcont, exceptions]
platforms: [windows]
architectures: [x64]
---
# Shadow-stack compatibility is not proof of enabled enforcement

These references concern documented Windows user-mode x64 shadow-stack and
continuation-policy contracts. They do not describe all Windows kernel HSP,
ARM64 pointer authentication, or another OS's CET enablement policy.

## Shadow stacks and indirect branch tracking are distinct CET facilities
Reviewed 2026-10-02. Intel Control-flow Enforcement Technology (CET) shadow stacks
maintain protected return-address copies and detect disagreement with the ordinary stack. Indirect branch
tracking is a separate facility for indirect CALL/JMP targets. [1]

Investigative consequence: CET-capable hardware does not by itself establish
either feature's use by a particular process. An ENDBR instruction is not proof
of Windows shadow-stack enforcement, and a shadow-stack-compatible image is not
proof of active hardware IBT. Neither facility validates lengths, object
ownership, credentials or the semantic correctness of an allowed operation.

## CETCOMPAT is extended PE metadata, not the ordinary NX/CFG field
MSVC /CETCOMPAT marks an image shadow-stack-compatible. The reviewed linker
documentation scopes this switch to x64; it is a compatibility marker, not an
inserted bounds check. [2] In PE, IMAGE_DLLCHARACTERISTICS_EX_CET_COMPAT=0x0001
is carried in IMAGE_DEBUG_TYPE_EX_DLLCHARACTERISTICS data. It is not bit 0 of
the ordinary optional-header DllCharacteristics. [3]

Decode the debug-entry type and bounded payload before interpreting the value.
The PE specification also defines EX_FORWARD_CFI_COMPAT=0x0040 but explicitly
states that Windows does not use that bit. [3] Do not infer an active Windows
forward-edge policy from that declaration or conflate it with DYNAMIC_BASE's
0x0040 in a different field.

## Compatibility, strict and audit modes change shadow-stack conclusions
PROCESS_MITIGATION_USER_SHADOW_STACK_POLICY (Windows 10 2004+) exposes
EnableUserShadowStack, EnableUserShadowStackStrictMode and AuditUserShadowStack.
Compatibility mode makes violations in CET-compatible modules fatal; strict
mode covers all shadow-stack violations. Audit mode logs would-be fatal
violations instead of making them fatal. Hardware support is still required. [4]

Investigative consequence: record all three fields, not just Enable. A surviving
test under audit is not proof of a bypass. Lack of a compatibility marker on one
DLL does not prove that shadow stacks are globally disabled.

## Binary admission and context validation are additional policy dimensions
The same shadow-stack policy has independent context-IP validation and audit
fields. BlockNonCetBinaries blocks incompatible images;
BlockNonCetBinariesNonEhcont additionally requires EH continuation metadata.
AuditBlockNonCetBinaries permits would-be rejected loads while logging them. [4]

Record the actual successful query and fields before claiming a load rejection
or context-restoration restriction. A module list alone cannot identify whether
admission was audited. Do not generalize this user-process policy to kernel-mode
hardware-enforced stack protection or assume a supported SDK field is enforced
by every OS build.

## EH continuation metadata distinguishes absent from present-but-empty
MSVC /guard:ehcont (VS 2019 16.7+) supplies sorted continuation-target RVAs for
64-bit processes on a 64-bit OS. The option is passed at compile and link stages.
In the documented NtContinue validation path, an IP first matches the shadow
stack or is checked against the containing image's continuation data. Legacy
absence permits compatibility continuation; present EHCONT data with zero
entries does not supply any valid in-image continuation targets. [5]

Use load-config Guard Flags plus continuation table/count, not count alone.
A zero count is not enough to distinguish the two states. This describes the
documented validation path, not a claim that every context change always invokes
it: retain the process policy and any audit/relaxed configuration. EHCONT is
not a complete inventory of functions or ordinary indirect-call destinations.

## Investigation boundary: mitigation event is not the earlier root cause
A return-address mismatch, a context-IP rejection and a DLL admission failure
are different observations. Preserve the triggering instruction/API, module
identity, policy snapshot, compatibility metadata and event/error evidence.
Then trace the earlier write, lifetime error or incompatible control transfer.

Constructed distinction: a data-only authorization field is corrupted while
all returns remain legitimate. No shadow-stack violation is required for that
logic failure. Conversely, an unusual hand-written stack switch can violate a
contract without proving attacker control. Do not infer exploitability or its
absence solely from a mitigation label.


## Sources and limits
Primary documentation reviewed 2026-10-02. No corrupt-return experiment claimed.

1. [Intel CET technical overview](https://www.intel.com/content/www/us/en/developer/articles/technical/technical-look-control-flow-enforcement-technology.html): distinct hardware facilities, not Windows enablement.
2. [MSVC CETCOMPAT](https://learn.microsoft.com/en-us/cpp/build/reference/cetcompat?view=msvc-170).
3. [PE extended DLL characteristics](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): debug payload and field-specific encodings.
4. [User shadow-stack policy](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_user_shadow_stack_policy): compatibility/strict/audit, admission and context fields.
5. [MSVC EH continuation metadata](https://learn.microsoft.com/en-us/cpp/build/reference/guard-enable-eh-continuation-metadata?view=msvc-170): absent versus empty table and validation scope.
