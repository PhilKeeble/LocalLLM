---
id: vulnerability-information-residual-secret-lifecycle-sanitization-failure
title: Residual secret survives a security-state or ownership transition
kind: vulnerability
topics: [information-disclosure, residual-data, sanitization, reset, privilege-transition]
platforms: [cross-platform]
architectures: [any]
---

# Residual secret survives a security-state or ownership transition

## Definition and violated invariant

This vulnerability occurs when protected data remains in storage or machine state after reset, deallocation, reassignment, privilege transition, sleep/resume or another lifecycle boundary and becomes accessible to a later unauthorized context. Relevant state can include memory, registers, device buffers, persistent media, scratch storage, accelerators and saved execution contexts.

The violated invariant is that the transition must remove protected state or keep the old state inaccessible before authority changes. D03 covers the common case of a reused buffer being returned directly; this profile covers the broader transition and sanitization contract.

## Conditions that establish the issue

Identify the protected bytes or state, the transition that should end their visibility, the required sanitization or isolation contract, the later actor and a supported read path. Establish that the relevant physical or logical state survives and is not completely overwritten, cryptographically erased or rendered inaccessible before reassignment.

Account for copies, caches, remapped pages, device-local memory and compiler elimination of intended clearing. For cryptographic erasure, establish that destroying the actual effective key makes the residual ciphertext infeasible to recover under the stated model.

## Evidence that is not sufficient

Absence of a visible clearing loop, a `free`, reset call or privilege change is not proof. An allocator, kernel, firmware or device may sanitize before exposure; new ownership may remain within the same authorized domain; or reset may remove power from the relevant state. Source code can also omit a clear that occurs in a lower layer.

A clearing call is not conclusive either. Verify its range, completion, ordering and whether optimization can remove it. Sanitizing one copy does not cover replicas or device buffers.

## Investigation sequence

Map the full lifecycle: creation, copies, protected use, transition, sanitization, reassignment and first possible observation. Recover the exact storage domain and reset scope. Compare the secret interval with clear, overwrite, discard, key destruction or access-control changes and establish completion before the new actor can read.

At binary level, confirm stores remain in the shipped code when explicit erasure is relied upon, and follow DMA or asynchronous work that can outlive the logical release. For saved contexts, check which registers and memory images cross privilege or world transitions and which are restored or exposed.

## Constructed lifecycle

A hypothetical accelerator processes tenant A's key in device-local SRAM, reports completion and assigns the same compute unit to tenant B after a software reset that clears command state but not SRAM. If B can issue a diagnostic read that returns the surviving bytes, the reset and reassignment violate the isolation invariant.

The claim is refuted if the documented reset clears that SRAM before reassignment, hardware access control prevents B from reading it, or the bytes are overwritten. A shared device and reset instruction alone are insufficient.

## Primitive and impact limits

State the residual representation, location, lifetime, amount, reader capability and reassignment conditions. Persistence does not imply readability; readability does not imply that a recovered fragment is a complete usable secret.

Downstream authentication, decryption or elevation depends on the recovered value's role and validity. The root effect remains disclosure across a lifecycle boundary.

## Related knowledge and primary sources

The stale-buffer profile covers request or tenant buffer reuse, while this profile covers reset, privilege and device-state transitions. Platform and hardware references must supply the actual reset and sanitization semantics.

Reviewed 2026-10-09 against [NIST SP 800-88 Revision 1](https://csrc.nist.gov/pubs/sp/800/88/r1/final) definitions of clear, purge and destroy, [NIST SP 800-53 Revision 5.1 controls MP-6 and SC-4](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), and [MITRE CWE-226](https://cwe.mitre.org/data/definitions/226.html). Media-sanitization methods do not by themselves define volatile register or device-reset behavior.
