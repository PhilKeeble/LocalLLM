---
id: reference-windows-privileged-service-broker-boundaries
title: Windows privileged service and broker boundaries
kind: reference
topics: [windows, services, brokers, privilege-boundaries, authorization, ipc]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows privileged service and broker boundaries

## Separate control planes

The Service Control Manager's service-object security controls who can query,
configure, start, stop, or delete a service. It does not authorize the service's
application IPC. Named pipes, RPC/COM endpoints, sockets, shared memory, files,
registry keys, and device objects each have their own security and protocol
decisions.

A service account (LocalSystem, LocalService, NetworkService, virtual account,
or configured user) defines one part of process authority. Also record token
privileges, integrity, service SID, restricted SID/token configuration,
filesystem/registry ACLs, impersonation, and child-process token creation.
“Runs as administrator” is too imprecise for boundary analysis.

## Service-manager rights and service-object rights

SC_MANAGER_CREATE_SERVICE (0x2) is a right on the SCM database object;
SERVICE_CHANGE_CONFIG (also 0x2) is a right on a particular service object.
The same bit value does not identify the same authority without object type.
SERVICE_START (0x10) and SERVICE_STOP (0x20) are separate from change-config.
Changing configuration can replace the executable the service runs. [1]

Inference: service start permission does not prove permission to replace its
binary, and a protected service object does not prove its executable directory
is protected. File/registry ACLs, SCM/service DACLs and application IPC policy
are independent surfaces. A proposed configuration-to-execution finding needs
both actual change authority and evidence that the altered configuration is used.

## Service SID type is not the service account

SERVICE_SID_TYPE_UNRESTRICTED (1) adds the service SID to the process token;
the word unrestricted does not mean administrator or unrestricted access to
all resources. SERVICE_SID_TYPE_RESTRICTED (3) includes that behavior and adds
the service SID to the restricted SID list along with documented additional
SIDs. If services share a process and one is restricted, all must be restricted.
Service SID names have the form NT SERVICE\SvcName. [3]

A service account and service SID configuration are different inputs to token
authority. Stored configuration is not a substitute for the current process
token or effective impersonating thread token. Restricted-token access rules
are in reference-windows-access-check-rights-integrity; this SID-type label is
not proof that a specific operation is denied or an isolated process exists.

## Broker caller identity and restoration

Do not authorize solely by executable name/path, PID, parent PID, window,
session, or a client-supplied identity field. These can be useful telemetry but
need a security principal/protocol and race-resistant binding for authorization.

Impersonation can reduce authority for caller-scoped access, but a successful
entry and the applicable level must be established on the actual operation's
thread. Restoration must match the API family and its result: RevertToSelf,
RpcRevertToSelf/Ex and CoRevertToSelf are not interchangeable. CoRevertToSelf
restores the authentication that preceded COM impersonation; that need not be
the process primary token. See reference-windows-tokens-sids-groups-impersonation
and reference-windows-com-rpc-authentication-impersonation. Explicit privileged
work after restoration still needs authorization and validated operands.

## Configuration and loading

For AppContainer/LPAC clients, use reference-windows-appcontainer-token-capabilities
and reference-windows-appcontainer-resources-brokers. The dedicated workflow is
playbook-re-appcontainer-broker-boundary; package identity, endpoint reachability
and authorization of a broker operation are separate evidence.

CreateServiceW expects the fully qualified binary path, quoted when it contains
spaces; the string can include arguments. SERVICE_WIN32_OWN_PROCESS (0x10)
and SERVICE_WIN32_SHARE_PROCESS (0x20) distinguish own/shared service hosting. [4]
A service name is therefore not a unique process boundary.

Inference: an unquoted path alone does not establish a vulnerability. The
candidate executable resolution, caller's ability to place/replace that file,
service launch/restart conditions and resulting authority must be evidenced.
DLL/plugin and configuration inputs are additional loading boundaries, not
automatically governed by the executable's ACL. Workflow and counterevidence
belong in playbook-vr-windows-cross-boundary.

## Sources

Reviewed 2026-10-02. Service configuration facts do not assert live authority
for any target installation. Token and COM contracts retain their primary homes.

- [1. Service Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights): SCM versus service objects and specific rights.
- [2. Service User Accounts](https://learn.microsoft.com/en-us/windows/win32/services/service-user-accounts): account context.
- [3. SERVICE_SID_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/ns-winsvc-service_sid_info): SID types, restricted/shared hosting and service SID names.
- [4. CreateServiceW](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-createservicew): path quoting, arguments and process type.
- [5. CoRevertToSelf](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coreverttoself): restoration to prior authentication.
- [6. RevertToSelf](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-reverttoself): Win32 restoration and RPC API distinction.
