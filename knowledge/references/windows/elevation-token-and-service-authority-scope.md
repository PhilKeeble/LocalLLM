---
id: reference-windows-elevation-token-service-authority-scope
title: Windows standard, filtered, elevated, service and SYSTEM authority scope
kind: reference
topics: [windows, tokens, uac, elevation, services, system, integrity]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows elevation and service authority scope

## Elevation type, group membership and integrity are separate observations

Windows token elevation type distinguishes a full token, a limited token, and a default token that has no linked elevated/limited pair under the documented UAC model. Administrator-group membership, elevation state, enabled privileges, restricted or deny-only SIDs, integrity level, session and AppContainer state remain separate inputs to authority. A high integrity label or an administrator-looking SID does not establish every object right or the token used by the sensitive operation.

Recover the primary or impersonation token actually selected at the check/effect, then record token type, groups and attributes, privileges and enablement, restrictions, integrity, AppContainer/capabilities and granted handle rights. UI shield, consent dialog, process name or parentage is contextual evidence rather than the resulting token.

## Standard, filtered and elevated contexts must be tied to the actual token

Under UAC, an administrator account can receive a filtered token for ordinary execution and a linked elevated token after the applicable elevation flow. A standard user can also launch a process using different supplied credentials; that is a logon/credential transition, not proof that the original user's token became elevated.

Identify account logon SID, token user, linked-token relationship where applicable, elevation type and process/thread token at the operation. Do not infer elevation from `runas` text or a manifest alone: policy, consent/credential outcome and process creation determine the resulting context.

## Service identity, service SID and LocalSystem are different properties

A Windows service runs under its configured account or service-host arrangement. A service SID can identify the service for resource ACLs and can participate in restricted service tokens; it is not the account itself. LocalSystem is a highly privileged predefined local account whose network presentation can differ from its local authority.

For an escalation claim, recover the service object and configuration, account/token, enabled privileges, service SID restrictions, session, protected resources and exact gained rights. Code execution in a service does not automatically mean SYSTEM, and SYSTEM does not mean kernel-mode execution.

## AppContainer and low integrity are distinct restrictions

AppContainer authority includes package/container identity and capability-based resource grants in addition to token and object policy. Low integrity is a mandatory-integrity property and is not a substitute for determining AppContainer or LPAC state. A process can be packaged without running in AppContainer, and full-trust packaging terminology does not mean elevated administrator authority.

Use `reference-windows-appcontainer-token-capabilities` and `reference-windows-access-check-rights-integrity` for the independent policy layers. Report the resulting operation and resource, not one label as a complete privilege level.

## Primary sources and scope

Reviewed 2026-10-09 against Microsoft [`TOKEN_ELEVATION_TYPE`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_elevation_type), [access tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens), [User Account Control operation](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works), [service security and access rights](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights), [service SIDs](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights#service-sids), and [LocalSystem](https://learn.microsoft.com/en-us/windows/win32/services/localsystem-account). Effective authority remains operation- and object-specific.
