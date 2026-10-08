---
id: reference-android-native-hal-boundary
title: Android native services, HAL interfaces, vendor policy and parsers
kind: reference
topics: [android, native-services, hal, aidl, hidl, vendor, parsers, policy]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Native service and hardware boundary

## A HAL interface separates a client from device-specific implementation

A hardware abstraction layer (HAL) exposes an interface to device-specific code.
Binderized HALs run separately and register with a service manager; some interfaces
use same-process implementations. AIDL and HIDL are distinct interface families.
[1]

Identify actual instance, process/backend, implementation and registration. A
generic interface name does not prove this device implements every method or
uses the same transport. Keep vendor additions distinct from upstream contracts;
source presence is not proof the service is installed or reachable.

## Service-manager access and Binder call policy are separate gates

AOSP AIDL HAL documentation distinguishes service-name/type mapping, client
access, service registration and Binder communication policy. [2]

Recover applicable SELinux service type, caller/server domains and enforcement
for the actual instance. Finding a service does not prove all calls or operations
are allowed, and Binder transport permission does not replace per-method checks.
No current macro recipe or universal policy type name is assumed.

## The final native parser still needs input and authority evidence

For investigation, trace app/framework/broker inputs through parcel/handle
decoding into vendor parser, shared buffer and hardware effect. Retain lengths,
representation, ownership, selected device and completion state at each boundary.

An authorized broker can still forward untrusted content. Conversely, a parser
defect in unreachable vendor code is not established device exposure. Record
which caller can reach which instance and violated requirement; interface imports
alone prove neither vulnerability nor malicious hardware use.

## Sources and scope

Reviewed 2026-10-08. [HAL overview](https://source.android.com/docs/core/architecture/hal)
[1], terms/Binderized and Same Process HAL; [AIDL for HALs](https://source.android.com/docs/core/architecture/aidl/aidl-hals)
[2], interface scope and SEPolicy roles. No release-dependent migration mandate,
private vendor structures or assumed installed backend. Workflow:
playbook-android-service-authority; sandbox: reference-android-sandbox-policy.
