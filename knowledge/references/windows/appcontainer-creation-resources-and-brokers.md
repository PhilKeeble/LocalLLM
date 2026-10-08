---
id: reference-windows-appcontainer-resources-brokers
title: AppContainer creation, resource namespaces and broker boundaries
kind: reference
topics: [windows, appcontainer, capabilities, brokers, namespaces, network-isolation]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Trace AppContainer requests beyond the manifest

## Profile creation is not process creation
Reviewed 2026-10-02. CreateAppContainerProfile creates per-user/per-app folders
and registry storage for the current user; another user's profile requires
impersonating that user. It returns HRESULT, including an already-existing
profile result; the returned SID is freed with FreeSid. [1]
DeriveAppContainerSidFromAppContainerName obtains the profile SID and also
requires FreeSid for its result. [2]

Investigative inference: a profile creation call is not evidence that a child
was launched in the container. Do not confuse persistent profile configuration,
derived identity and the token attached to an executing child. Observe both
new-profile and existing-profile branches. Never delete another application's
profile merely to make an experiment start cleanly.

## Creation attributes carry nested pointer lifetimes
SECURITY_CAPABILITIES contains AppContainerSid, a SID_AND_ATTRIBUTES capability
array pointer, CapabilityCount and Reserved. [3] The launch guide initializes
Reserved to zero and supplies the structure in STARTUPINFOEX's attribute list
before CreateProcess with EXTENDED_STARTUPINFO_PRESENT. [4]
UpdateProcThreadAttribute's SECURITY_CAPABILITIES attribute creates an
AppContainer child on successful process creation; lpValue must persist until
DeleteProcThreadAttributeList. [5]

Reverse-engineering consequence: cbSize describes the attribute value, not the
total bytes of every pointed-to SID. Trace array count, SID attributes, native
pointer layout and backing allocation lifetimes. Do not model the structure as
a self-contained serialized blob. Attribute construction, child creation and
observed child token are separate evidence; trace failure paths that retry
without restrictions.

## Token-bound package lookup is not a client-supplied name
GetPackageFamilyNameFromToken returns a LONG error code: ERROR_SUCCESS on
success, APPMODEL_ERROR_NO_PACKAGE for no package identity, and
ERROR_INSUFFICIENT_BUFFER with required capacity. Length is in characters,
including the terminator in the returned size, not bytes. [6]

Investigative inference: zero is success here, unlike a successful BOOL API.
A broker must bind the queried token to the authenticated request before using
this result. A name sent in an IPC payload is not equivalent evidence. Package
identity still does not establish AppContainer status or authorize every
operation for that package; see reference-windows-appcontainer-token-capabilities.


## Named object lookup includes the container namespace
GetAppContainerNamedObjectPath retrieves the container's named-object path.
When both Token and AppContainerSid are NULL, selection uses the current
process token, or the thread token while impersonating. Each AppContainer has
its own named-object path. [7]

Investigative inference: equal event/mutex/mapping suffixes do not prove the
same object across broker, client and session contexts. Record resolved path,
token, session, descriptor and returned handle. Path discovery is not an access
grant. Do not replace the API with a guessed universal directory string, or
change object ACLs on the analysis host to resolve an unexplained failure.
General collision and mapping facts: reference-windows-object-namespaces-collisions,
reference-windows-shared-mapping-evidence.

## RPC interface defaults distinguish low integrity from AppContainer
RpcServerRegisterIf3's NULL SecurityDescriptor selects a default descriptor;
it is not a null DACL. For a non-AppContainer server the documented default
denies AppContainer clients but permits ordinary clients including low-integrity
processes. An AppContainer server's default denies clients in other containers.
When an explicit descriptor and callback both exist, the descriptor is checked
before the callback. [8]

Consequences: a local endpoint or low-integrity client trace does not prove
AppContainer reachability. Conversely, explicit container access does not prove
each manager operation is authorized. Record registration arguments, defaults,
callback path, actual transport and operation-specific guards. Other RPC
authentication/registration conditions still apply. See
reference-windows-com-rpc-authentication-impersonation for identity and reversion.

## Manifest capability, consent and resulting access are separate
Packaged applications' requirements depend on trust level. User privacy settings
can dynamically restrict sensitive-resource access even after capabilities are
declared. [9] Restricted-capability Store approval requirements are not equivalent
to runtime access enforcement; Microsoft states that Store approval is not
required merely to sideload an app declaring restricted capabilities. [10]

Investigative inference: neither a manifest string nor a successful SID
derivation proves the resource can currently be used. Recover installed
configuration, effective token, relevant broker/API decision and privacy state.
Do not classify intentional file-picker or broker-mediated access as a sandbox
escape solely because a direct path open is denied. Establish the product's
intended authorization rule and any violated object/operation binding.

## Network capability names describe different traffic scopes
For AppContainer capability declarations, internetClient covers outbound
Internet access; internetClientServer includes it and permits incoming Internet
traffic, not local-network access. privateNetworkClientServer covers inbound
and outbound home/work-network access. [9]
Microsoft's UWP connectivity guidance identifies WFP filtering, capability
tokens, loopback permission and policy-configured private ranges as distinct
causes of failures. [11]

Do not equate localhost with an unrestricted trusted caller, or a timeout with
a proven sandbox denial. Record destination classification, direction, matching
filter/drop evidence and any loopback exemption. Debug/sideload exemptions can
make development behavior differ from deployment. These facts are not a rule
that every full-trust packaged desktop application has UWP network restrictions.

## A brokered resource can differ from direct acquisition
In Chromium commit 90ebe709881f7572f250d30e9ec77a39b5d8a482, SocketBrokerTest
separates AppContainer use, direct versus brokered sockets, adapter selection
and a socket-brokering rule. Its expected-result logic permits a brokered socket
with the rule while expecting failure without it. [12] This is source/test
evidence, not a local network execution or a guarantee for every Chromium build.

Investigation consequence: a successful operation need not show that the
client's direct acquisition policy was bypassed. Trace who created the resource,
what authority was transferred, which recipient received it, and which broker
rule allowed it. A confused deputy requires a demonstrated policy violation,
not merely different privilege between client and server. See
reference-windows-privileged-service-broker-boundaries and
reference-windows-handle-authority-transfer.

## Sources: creation and identities
Reviewed 2026-10-02; contract review, not execution of a target sandbox.

1. [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile).
2. [DeriveAppContainerSidFromAppContainerName](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername).
3. [SECURITY_CAPABILITIES](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-security_capabilities).
4. [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer): creation attributes.
5. [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute): SECURITY_CAPABILITIES and lpValue lifetime.
6. [GetPackageFamilyNameFromToken](https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-getpackagefamilynamefromtoken).

## Sources: resources and boundaries
7. [GetAppContainerNamedObjectPath](https://learn.microsoft.com/en-us/windows/win32/api/securityappcontainer/nf-securityappcontainer-getappcontainernamedobjectpath).
8. [RpcServerRegisterIf3](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcserverregisterif3): default descriptor and callback ordering.
9. [App capability declarations](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/app-capability-declarations): trust level, privacy and network table.
10. [UWP capability guidance](https://learn.microsoft.com/en-us/windows/uwp/packaging/app-capability-declarations): restricted capabilities and sideloading.
11. [UWP connectivity troubleshooting](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/troubleshooting-uwp-firewall): WFP, loopback and private ranges.
12. [Chromium pinned AppContainer tests](https://chromium.googlesource.com/chromium/src/+/90ebe709881f7572f250d30e9ec77a39b5d8a482/sandbox/win/src/app_container_test.cc): SocketBrokerTest.
