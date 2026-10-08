---
id: reference-uefi-image-service-variable-capsule
title: UEFI PE and TE images, service phases, protocols, variables and capsules
kind: reference
topics: [uefi, pe, te, boot-services, runtime-services, protocols, variables, capsules]
platforms: [uefi]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# UEFI interface and image evidence

## PE and TE identify image formats rather than a Windows environment

PI TE images are derived from PE32/PE32+ executables with reduced headers that
retain the fields needed for PI execution. [1] A PE/COFF image can therefore be
firmware code; an MZ-like format finding does not identify Windows userland.

Recover machine, image kind, entry and relocation interpretation for the actual
loader. TE header reduction means ordinary PE file-coordinate assumptions cannot
be copied blindly. A recoverable image is not proof it was dispatched. Container
ancestry and selected boot phase remain separate evidence; no private firmware
loader offsets are assumed.

## Successful ExitBootServices changes the service and memory contract

Successful UEFI ExitBootServices terminates boot services. A first unsuccessful
attempt can already partially shut them down. The specification recommends
restricting subsequent boot-service calls to memory-allocation services after
the first attempt. Runtime services have a separate continuing contract and can
have availability limits.
UEFI protocols are GUID-identified interfaces associated with handles; their
functions and instance data supply the device/interface contract. [2][3]

Bind an indirect call to its actual table/interface and phase. A retained boot-
service pointer is not automatically valid after the transition. A GUID string
alone does not identify the called function or prove an interface is installed.
Unless explicitly specified otherwise, UEFI protocol methods are not runtime
interfaces. Status and phase evidence must accompany conclusions about use.

## A UEFI variable needs name, vendor GUID, attributes and operation policy

UEFI variables are identified by name and vendor GUID; attributes describe
properties including nonvolatile storage and boot/runtime accessibility. [3]

Recover the exact variable identity, returned extent, attributes, write policy
and consumer. A familiar name under a different GUID need not be the same object.
Nonvolatile storage does not by itself prove authenticated writes, boot influence
or malicious persistence. Accessibility depends on phase and the variable's
contract; the existence of a variable API does not establish every variable is
writable by every caller.

## Capsule delivery and applied firmware are different outcomes

UEFI capsule headers identify content format by CapsuleGuid; HeaderSize describes
the header and CapsuleImageSize includes header plus payload. Processing may be
immediate or deferred across reset, according to the capsule and platform. [3]

Bind format, complete extent, physical/virtual representation, selected consumer
and result. Submission success is not automatically proof the intended firmware
was installed or booted. Authentication belongs to the relevant payload/update
policy, not merely the generic header's existence. Preserve deferred processing
and failure reporting. Workflow: playbook-specialist-firmware-evidence.

## Sources and scope

Reviewed 2026-10-08. Specification editions are source provenance; match a target's
interface and phase without assuming support or private table layouts.

1. [PI 1.8 Errata A TE image](https://uefi.org/specs/PI/1.8A/V1_TE_Image.html): section 15 introduction/header purpose.
2. [UEFI 2.10 boot services](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html): protocol handlers and ExitBootServices; [overview protocols](https://uefi.org/specs/UEFI/2.10/02_Overview.html), section 2.4 runtime limits.
3. [UEFI 2.10 runtime services](https://uefi.org/specs/UEFI/2.10/08_Services_Runtime_Services.html): availability, variable services and section 8.5.3 capsule definitions/delivery.
