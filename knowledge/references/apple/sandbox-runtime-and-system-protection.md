---
id: reference-apple-protection-policy-boundaries
title: App Sandbox, hardened runtime, library validation and SIP boundaries
kind: reference
topics: [sandbox, hardened-runtime, library-validation, sip, policy, code-loading]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Apple protection-policy evidence

## A sandbox bounds resources; it is not application authorization

Apple's iOS runtime model isolates third-party apps and uses entitlements for
access beyond ordinary runtime identity. [1] macOS App Sandbox applicability
must be established for the particular process; do not generalize iOS deployment
rules to every macOS executable.

Identify the actual sandbox, entitlement scope and brokered resource access.
A permitted IPC call can ask a more privileged service to act, so the service's
request policy remains relevant. A sandbox label alone does not prove isolation
of every passed descriptor, shared object or permitted operation.

## Hardened runtime exceptions change specific protections

Apple documents hardened-runtime restrictions and entitlements that relax selected
protections. When macOS library validation applies, loaded code must be Apple
signed or share the main executable's Team ID; the disable-library-validation
entitlement relaxes that restriction. [2][3]

Recover enabled runtime policy and exceptions for the actual process. A valid
signature alone does not establish hardened runtime or library validation.
An exception can be intentional for a plugin host; establish reachable loading,
selected code and effect before interpreting it as a defect or malicious act.

## SIP protects system resources even from administrative processes

System Integrity Protection (SIP) is macOS policy protecting system locations and
restricting attachment to protected system processes. Its scope includes
administratively privileged and unsandboxed processes. [4]

Root authority therefore cannot alone establish permission for a protected action.
Record applicable resource, policy state and actual decision. SIP is not a
universal barrier for all user data or every third-party process. No fixed list
of protected paths, boot-mode default or disablement procedure is assumed here.

## Sources and scope

Reviewed 2026-10-08. [iOS runtime security](https://support.apple.com/guide/security/security-of-runtime-process-sec15bfe098e/web)
[1], Sandboxing/Entitlements; [hardened runtime configuration](https://developer.apple.com/documentation/xcode/configuring-the-hardened-runtime)
[2], exception purpose; [library validation entitlement](https://developer.apple.com/documentation/BundleResources/Entitlements/com.apple.security.cs.disable-library-validation)
[3], Discussion; [SIP introduction](https://developer.apple.com/library/archive/documentation/Security/Conceptual/System_Integrity_Protection_Guide/Introduction/Introduction.html)
[4], protection concepts only, not archived deployment/configuration advice.
Workflow: playbook-apple-service-authority.
