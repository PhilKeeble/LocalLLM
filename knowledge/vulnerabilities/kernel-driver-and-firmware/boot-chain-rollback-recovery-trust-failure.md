---
id: vulnerability-kernel-boot-chain-rollback-recovery-trust-failure
title: Boot-chain, rollback, recovery or selected-component trust failure
kind: vulnerability
topics: [firmware, secure-boot, rollback, recovery, component-selection, trust-chain]
platforms: [embedded, uefi]
architectures: [any]
---

# Boot-chain, rollback, recovery or selected-component trust failure

## Definition and violated invariant

This vulnerability occurs when a boot or recovery stage transfers control to a component whose exact bytes, identity, authorization, freshness or dependency state were not established by the intended trust policy. The invariant is that each accepting stage must authenticate the representation it actually executes, authorize it for the selected component, enforce rollback policy where required and pass verified state to the next stage without substitution.

Signature validity, signer authorization and freshness are separate. An old correctly signed image can violate rollback policy, while a newly signed image can target a component its signer is not authorized to update.

## Conditions that establish the issue

Recover immutable or earlier trust anchor, keys and roles, manifest and authenticated byte range, component/device identity, dependency and configuration selection, rollback counter storage, ordinary and recovery policies, installed slot, activation and control transfer. Prove an attacker-influenced image or state is accepted contrary to one of those rules.

Include reset and power-loss behavior around monotonic state and slot commits. Recovery is a separate path whose intended downgrade and physical-presence rules must be identified.

## Evidence that is not sufficient

A signature check, old version string, alternate slot, recovery image, writable flash or successful update submission is not sufficient. A later stage may reject the image; the version label may not drive protected freshness; fallback may be authorized; and stored bytes may never be selected.

Do not equate measured boot with enforced boot unless the target policy uses the measurement result to gate execution or another security decision.

## Investigation sequence

Draw every stage as `selected input -> authenticated representation -> signer/role -> component/freshness policy -> installed object -> next control target`. Preserve which stage owns each decision. Trace failure and recovery selections with retained state across resets.

At binary level, follow key selection, hash/signature inputs, result branches, component IDs, rollback comparisons, slot flags and final branch or reset. Check for verification-to-use substitution: the bytes hashed must be the bytes later loaded.

## Constructed flow

A hypothetical bootloader verifies the signature on manifest M, then uses an unauthenticated external filename from M's surrounding package to choose the image loaded. An attacker can retain the valid manifest while substituting the selected payload if the filename-to-bytes binding is absent.

The finding is refuted if the authenticated manifest contains and verifies a digest or authenticated identity for the exact loaded image and the loader enforces it.

## Primitive and impact limits

The direct primitive is booting, installing or recovering to an unauthorized or stale component. Persistent code execution requires attacker control of that component and actual activation in the stated privilege domain. A policy discrepancy without an accepted image remains a candidate.

## Related knowledge and primary sources

`reference-firmware-boot-trust-recovery` and update-authority profiles provide role and recovery distinctions. This profile retains end-to-end selected-byte binding and rollback evidence.

Reviewed 2026-10-09 against [RFC 9019](https://www.rfc-editor.org/rfc/rfc9019.html) firmware update architecture and [NIST SP 800-193](https://csrc.nist.gov/pubs/sp/800/193/final) platform firmware protection, detection and recovery guidance. The flow is hypothetical and does not prescribe one boot architecture.
