---
id: reference-firmware-boot-trust-recovery
title: Firmware boot chains, authentication, rollback policy and recovery evidence
kind: reference
topics: [firmware, boot-chains, authentication, rollback, recovery, activation]
platforms: [embedded, uefi]
architectures: [arm, arm64, x86, x64, riscv32, riscv64, mips, powerpc]
---
# Boot acceptance and transition evidence

## Firmware authentication and update authorization answer different questions

RFC 9019's IoT update architecture separates identifying an image/manifest author
from deciding which actions that author is permitted to request. Trust provisioning
supplies this authorization context. [1]

Recover each accepting stage's trusted keys/policy, verified bytes, selected
component and transfer of control. A signature routine or signed package does
not prove the device verified that package before executing it. Validation of
one stage does not establish all later images, configuration or recovery paths.
This is an investigation model, not a claim that every platform implements the
RFC architecture or the same immutable root of trust.

## A valid old image can still violate rollback policy

RFC 9019 identifies old but valid firmware as a distinct update risk and describes
manifest information addressing component, storage and update decisions. [1]

Bind accepted freshness/sequence policy to the component actually activated and
the retained state used by its verifier. A human-readable version string is not
proof of a protected rollback counter. Authentication alone does not establish
freshness. Keep ordinary boot, update acceptance and recovery downgrade policy
separate; fallback to a prior image may be intentional and needs the target's
authorized recovery contract before it becomes a defect.

## Recovery is a separate selection path with its own evidence

RFC 9019 describes recovery after failed update/invocation, including multiple
application images or a recovery image. An invalid new image requires a recovery
decision rather than proving successful activation. [1]

Recover failure result, selected slot/image, retained boot state and control-flow
handoff. Staging bytes, requesting a reset and booting them are different events.
An interrupted update does not prove persistent corruption or that recovery
bypasses authentication. Inspect recovery's actual inputs and acceptance policy;
the RFC's possible designs do not establish a target's installed behavior.

## Boot behavior and malicious persistence require separate conclusions

Report the established transition and resulting executable identity, with unknown
stages and mutable policy stated explicitly. A stored boot entry or alternate
image can be legitimate maintenance/recovery. Evidence of malicious persistence
requires the trigger, selected code, execution context and supported behavior;
reference-malware-persistence-trigger-context supplies that interpretation.

Shared verification/installation facts: reference-logic-update-verification-installation
and reference-crypto-update-trust-activation. Workflow:
playbook-specialist-firmware-evidence.

## Source and scope

Reviewed 2026-10-08. [RFC 9019](https://www.rfc-editor.org/rfc/rfc9019.html) [1],
April 2021, bootloader/firmware-consumer and manifest/security sections. Adopted
authentication/authorization, old-valid-image and recovery concepts only. No
hardware fuse scheme, recommended algorithm, vendor defaults or bypass recipe.
