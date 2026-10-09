---
id: vulnerability-information-address-layout-mitigation-state-disclosure
title: Address, layout or mitigation-state disclosure
kind: vulnerability
topics: [information-disclosure, pointer-disclosure, aslr, mitigation-state]
platforms: [cross-platform]
architectures: [any]
---

# Address, layout or mitigation-state disclosure

## Definition and violated invariant

This vulnerability exposes a pointer, mapped address, module base, relocation delta, object layout or security-policy state to an actor who is not authorized to learn it. The narrow root cause may be an excessive response, format string, out-of-bounds read, diagnostic field or authorization failure; layout disclosure describes the confidentiality primitive and should be reported with that cause when known.

The invariant is contextual: many addresses and mitigation settings are intentionally public to an authorized debugger or same-process component. A security issue requires an observer outside the intended boundary and information that reduces uncertainty about protected placement or policy.

## Conditions that establish the issue

Identify the exact disclosed value, its object and address space, the observer, the delivery path and the policy that makes it protected. For a claimed ASLR reduction, connect the value to the relevant randomized region or derive the region's base using a target-valid offset. For mitigation state, show that the exposed bit or response corresponds to effective policy for the attacked process or object.

Account for per-process, per-boot, per-image and per-allocation randomization scope. An address from one process, architecture or launch may not locate the corresponding object in another.

## Evidence that is not sufficient

Hexadecimal output, a pointer-shaped value, a nonpreferred module address or knowledge that ASLR is enabled does not establish useful disclosure. The value may be an identifier, file offset, relative virtual address, sanitized handle, stale address, or public policy. A leak of one mapping does not reveal every module or heap object.

Do not claim mitigation bypass merely because a base address is known. Exploitation still requires a separate memory or control primitive, usable targets, correct build identity and satisfaction of other active protections.

## Investigation sequence

Trace the value from its source to the observer and preserve its coordinate system: process virtual address, module-relative offset, file offset, physical address or opaque token. Establish module/build identity and compute any inferred base with checked arithmetic. Compare repeated observations across launches only to characterize scope, not as a prerequisite for recognizing a direct leak.

Recover effective mitigation settings from authoritative process, image and platform state. Distinguish compile-time eligibility from runtime activation and a module property from process-wide policy. Record which exploit uncertainty the disclosure removes and which remains.

## Constructed representation

A hypothetical error response contains `handler=0x00007ff8123419a0`. If binary evidence identifies the same build's handler at relative virtual address `0x19a0`, the response supports an inferred module base of `0x00007ff812340000` for that process instance. This inference fails if the value is not a live virtual address, the build differs, rebasing uses another coordinate system or the observer is already authorized to inspect the process.

## Primitive and impact limits

The direct primitive is knowledge of an address, layout relation or effective policy. State its precision, lifetime, address space, repeatability and attacker visibility. It may support target selection or reduce ASLR uncertainty but does not write memory or redirect control flow.

Privilege escalation or code execution requires an independent reachable primitive and a complete mitigation-aware chain. Describe the leak as supporting evidence rather than the exploit itself.

## Related knowledge and primary sources

Platform image, loader and mitigation references govern the meaning and scope of individual values. The profile remains self-contained by requiring the analyst to preserve coordinate system, process identity and policy provenance.

Reviewed 2026-10-09 against Microsoft's [`PROCESS_MITIGATION_ASLR_POLICY`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-process_mitigation_aslr_policy), Linux [`proc_pid_maps(5)`](https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html), [MITRE CWE-200 mapping guidance](https://cwe.mitre.org/data/definitions/200.html) and [MITRE CWE-209](https://cwe.mitre.org/data/definitions/209.html). Platform interfaces describe authorized observability; they do not make every address secret or prove exploitability.
