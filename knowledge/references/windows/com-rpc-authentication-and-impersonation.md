---
id: reference-windows-com-rpc-authentication-impersonation
title: Windows COM and RPC authentication boundaries
kind: reference
topics: [windows, com, rpc, authentication, impersonation, authorization]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows COM and RPC authentication boundaries

## Boundary model

Scope: Windows COM/DCOM and related RPC boundaries, reviewed 2026-10-02 against
the Microsoft sources linked below. Separate activation/launch permissions,
process access restrictions, proxy settings, authentication service and level,
impersonation authority, effective identity and method/resource authorization.
Interface discovery or successful activation does not establish unrestricted
method access. Default settings are not necessarily the effective settings.

Record server identity/activation, interface IID and method/opnum, endpoint,
effective launch/access permissions, authentication level, impersonation level,
client token acquisition, and method-specific access check. Use
`reference-windows-com-activation-interface-evidence` for discovery and
`reference-windows-tokens-sids-groups-impersonation` for token semantics. This
reference does not turn a COM policy into a rule for all non-COM RPC servers.

## Security initialization may precede the explicit call in the binary

Windows `CoInitializeSecurity` sets process security once, explicitly or implicitly.
If the application has not called it, COM initializes security when an interface
is first marshaled or unmarshaled. A later explicit call can return
`RPC_E_TOO_LATE`; its supplied settings must not be treated as installed policy.
Inspect initialization ordering and HRESULT, including component activity.

The server's authentication-level default also governs its incoming minimum;
the impersonation-level argument is a client proxy default, not an incoming
server-side minimum. `RPC_C_IMP_LEVEL_DEFAULT` is not valid for this API.
Do not confuse it with `CoInitializeEx`, which initializes thread concurrency.
[CoInitializeSecurity](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializesecurity).

## CoInitializeSecurity flags determine what pSecDesc means

In Windows COM, `pSecDesc` can describe an absolute security descriptor, an
IAccessControl object or an AppID; decode capability flags before assigning a
type. `EOAC_APPID` selects registry-derived settings and ignores other arguments.
`EOAC_ACCESS_CONTROL` selects IAccessControl. Their combination is invalid.
Without either flag, NULL pSecDesc permits all callers at this access-permission
layer; it is not an empty DACL. Computer-wide restriction policy still applies.
[CoInitializeSecurity parameter rules](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializesecurity).

Inference: NULL alone is not enough to diagnose anonymous reachability; also
check flags, authentication, restrictions and the actual method path. For
IAccessControl, COM caches access decisions, so changing its ACL after
initialization is not a supported way to implement changing per-call policy.
[Process-wide security](https://learn.microsoft.com/en-us/windows/win32/com/setting-processwide-security-with-coinitializesecurity).

## Launch permissions and instance access permissions are different

Windows COM AppID `LaunchPermission` governs launching a server, with
`DefaultLaunchPermission` as its documented fallback. Registry `AccessPermission`
governs access to instances under registry-based process security, with
`DefaultAccessPermission` as fallback. Explicit process initialization can select
another policy; EOAC_APPID explicitly selects registry policy. Inspect that path
rather than treating a registry export as the effective decision.

Inference: allowed launch does not prove allowed connection to every instance or
authorization for every method. Conversely, permission to access an existing
object does not by itself prove permission to start a new server. Machine-wide
restrictions and application checks remain separate evidence. No default ACL
membership is inferred from the name of a permission value.
[LaunchPermission](https://learn.microsoft.com/en-us/windows/win32/com/launchpermission),
[AccessPermission](https://learn.microsoft.com/en-us/windows/win32/com/accesspermission).

## Authentication versus authorization

For COM authentication, CONNECT authenticates the connection without giving
subsequent payload integrity/confidentiality from that level alone.
PKT_INTEGRITY protects data integrity but not confidentiality; PKT_PRIVACY adds
encryption. DEFAULT selects a level; it is not equivalent to NONE. Inspect the
effective service/transport and negotiated settings, not merely one constant in
the caller. These levels do not authorize a resource operation.
[Authentication levels](https://learn.microsoft.com/en-us/windows/win32/com/authentication-level).

Impersonation level describes how the server may use client identity, not packet
protection. A high authentication level does not imply delegate-level authority,
and encryption does not prove correct application access checks. Record the
actual token, object and requested operation at the decision and privileged sink.

## DCOM activation hardening is update-qualified and not universal method policy

Microsoft KB5004442 documents packet-integrity minimums for non-anonymous DCOM
activation, client-side automatic raising of those requests, and the March 14,
2023 update phase that removed the ability to disable the hardening. Retained
legacy registry values therefore do not prove a fully updated server disabled
it. Record client/server builds and installed updates before interpreting an
older low-level activation constant or compatibility workaround.

The guidance explicitly preserves anonymous activation where the server allows
it. Do not claim that hardening forbids every anonymous call, or that activation
integrity guarantees privacy or per-method authorization. A low constant in the
client is not proof of a low effective activation level after automatic raising.
[KB5004442, updated March 20, 2023](https://support.microsoft.com/en-au/servicing/os/windows/2021/06/kb5004442-manage-changes-for-windows-dcom-server-security-feature-bypass-cve-2021-26414).

## A security blanket belongs to the specific proxy used for the call

COM `CoSetProxyBlanket` changes the specified proxy's authentication, impersonation,
identity and capability settings. `pAuthInfo` with explicit identity and a cloaking
flag is an invalid combination. NULL `pServerPrincName` generally retains the
previous principal; it does not reset it. An authentication-provider change with
that retained principal can fail. Check HRESULT and follow the exact proxy into
the call rather than assuming the proposed blanket took effect.
[CoSetProxyBlanket](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cosetproxyblanket).

`CoQueryProxyBlanket` queries proxy configuration, not the result of a server's
application authorization. Its returned principal string needs CoTaskMemFree;
returned authentication-identity memory must not be written or freed by the
caller. Preserve that ownership distinction in cleanup analysis. A local direct
interface is not automatically a queryable remote proxy.
[CoQueryProxyBlanket](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coqueryproxyblanket).

## Shared proxy changes and CopyProxy QueryInterface can alter the evidence path

COM blanket changes affect all users of that proxy instance. `CoCopyProxy` permits
a private copy whose blanket can change independently; copying a pointer variable
does not create that isolation. In the documented example, QueryInterface on an
IA proxy copy for IID_IA returns the original IA proxy, not the private copy.
Do not assume a private blanket survives a subsequent QueryInterface.

Inference: record aliasing, copy creation, QueryInterface results and the final
receiver of each call. A shared proxy reconfigured for one task can affect another
task's later call; a defect still requires a feasible schedule and violated policy.
Some custom-marshaled objects lack IClientSecurity, so missing blanket support
does not establish that an object is unprotected or not COM.
[CoCopyProxy](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocopyproxy),
[proxy security](https://learn.microsoft.com/en-us/windows/win32/com/setting-security-at-the-interface-proxy-level).

## Cloaking selects projected identity; local impersonation alone is insufficient

For Windows COM, without cloaking the outgoing proxy normally uses process or
explicit authentication identity, not an arbitrary current thread token. Dynamic
cloaking selects the current thread token per call, falling back to the process
token. Static cloaking fixes identity: process-default static cloaking captures
on first proxy use, whereas setting a static blanket captures at that time.
Schannel does not support cloaking.

Constructed broker example: a reused static proxy captured caller A before the
thread later impersonates B. That thread-token change alone does not establish
that the downstream server sees B. Record proxy history and effective identity.
Dynamic cloaking is not permission to delegate across arbitrary machines;
authentication-provider and impersonation-level constraints still apply.
Keep proxy-call cloaking distinct from CLSCTX activation cloaking.
[COM cloaking](https://learn.microsoft.com/en-us/windows/win32/com/cloaking).

## COM broker impersonation has call-scoped restoration, not a nesting counter

Windows `CoImpersonateClient` impersonates the current COM caller and requires
CONNECT-or-higher authentication. Check its HRESULT before client-authority work;
an attempted call does not establish a changed token. COM automatically reverts
when the call ends if necessary, but that does not protect privileged work done
earlier under an unintended identity. One CoRevertToSelf undoes any number of
CoImpersonateClient calls; do not model them as a counted push/pop stack.
[CoImpersonateClient](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coimpersonateclient).

`CoRevertToSelf` restores the thread's authentication information from before
COM impersonation. Do not replace that contract with an assumption that it always
selects the process primary token. Distinguish CoRevertToSelf from RPC's
RpcRevertToSelf/Ex and Win32 RevertToSelf; inspect each API's failure/restoration
contract rather than applying one broker cleanup rule to all three families.
[CoRevertToSelf](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coreverttoself).

## Asynchronous COM Signal changes whether new impersonation can begin

For the documented asynchronous COM Begin_/ISynchronize protocol, the server
cannot newly impersonate the client after its `ISynchronize::Signal` call
completes, even if Begin_ has not returned. If impersonation began before Signal,
that token remains until explicit IServerSecurity reversion or Begin_ returns,
whichever happens first. Signal therefore does not mean the thread necessarily
stopped impersonating at that instant.

Inference: mark both impersonation start and completion signaling in the timeline.
Do not extend this rule to arbitrary thread-pool jobs, language async/await or
non-COM asynchronous RPC. A retained object reference is not a retained call
security context. Establish the API's actual protocol before moving client work
after a completion signal.
[Impersonation and asynchronous calls](https://learn.microsoft.com/en-us/windows/win32/com/impersonation-and-asynchronous-calls).

## Parser and lifetime review

Treat generated stubs as transport code and follow unmarshalled values into
server implementation. Check count/length correlations, integer conversions,
context-handle ownership and rundown, cancellation, asynchronous completion,
and object lifetime across reconnects. A stub-level bounds check does not
validate application semantics or later native copies.

For RPC contract detail, use `reference-windows-rpc-interface-stub-evidence`,
`reference-windows-ndr-marshaling-contracts` and
`reference-windows-rpc-context-callback-lifetime`. These distinguish interface
admission callbacks from static RPC callbacks and wire validity from manager
semantics; they do not replace COM activation or per-proxy security review.
