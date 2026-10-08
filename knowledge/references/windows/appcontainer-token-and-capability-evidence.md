---
id: reference-windows-appcontainer-token-capabilities
title: AppContainer tokens, capability decisions and LPAC evidence
kind: reference
topics: [windows, appcontainer, capabilities, tokens, lpac, authorization]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Distinguish AppContainer identity from authority

## Package identity is not AppContainer status
Reviewed 2026-10-02. Windows AppContainer starts with Windows 8; API and LPAC
availability still require target-build checks. Packaged desktop applications
can run at medium integrity/full trust, outside AppContainer. The manifest's
uap10:TrustLevel distinguishes appContainer from mediumIL. [1][7]

Investigative inference: an MSIX file, package family name, runFullTrust string,
or low-integrity label does not alone classify the executing token. Full trust
in this packaging terminology does not mean an elevated administrator. Recover
each actual process and effective thread token rather than applying one package
label to every helper. See reference-windows-tokens-sids-groups-impersonation
for token selection and reference-windows-access-check-rights-integrity for
separate integrity policy.

## Token queries and identification-level caveat
GetTokenInformation TokenIsAppContainer returns a DWORD; TokenCapabilities
returns TOKEN_GROUPS; TokenAppContainerSid returns TOKEN_APPCONTAINER_INFORMATION
with a null SID for a token not associated with an AppContainer. Preserve API
success separately from these values. Microsoft warns that a zero
TokenIsAppContainer result on an identification-level impersonation token must
not become a trusted non-container authorization path: deny access. [2]

Recover token type and impersonation level as well as status. An unavailable
information class or failed query is not a measured false value. The enum page's
general minimum-OS table does not establish availability of every newer member.
Never decode a returned TOKEN_GROUPS as a flat array without its count, native
layout and buffer bounds.

## Two principal sets constrain discretionary grants
For AppContainer discretionary access, the user/group grant and the
package/capability grant intersect; neither replaces the other. [1]
Constructed mask model: user grants READ|WRITE, container grants READ, so the
intersection permits READ only. A capability ACE cannot confer a right missing
from the user-side grant. This is a simplified DACL contribution, not the entire
Windows access algorithm: object rules, token restrictions, mandatory policy
and the actual acquisition path remain relevant.

Investigative inference: a user-only permission audit misses the container
principal; a capability-only audit misses the user. Record the precise requested
rights and matching ACEs. A denied direct open does not establish that a
separately brokered or transferred handle lacks authority. Handle facts live in
reference-windows-handle-authority-transfer.

## AppContainer integrity interaction is not the ordinary low-IL example
Microsoft's AppContainer launch guidance explicitly permits read/write/execute
according to both principals' DACL grants for a resource labeled medium or lower
when access is granted through a package or capability SID. [1] Do not apply a
plain non-AppContainer low-integrity/no-write-up example as an unconditional
denial rule for this AppContainer case.

This is not permission to write every medium-integrity object. Preserve the
actual container token, label, relevant ACEs, rights and API result. It also does
not assert access to higher-integrity resources or eliminate other object and
broker policy. An apparent difference from a normal low-IL process is not by
itself a vulnerability; identify which rule governs the particular access path.

## CheckTokenCapability has two results and a token choice
CheckTokenCapability requires TOKEN_QUERY on a supplied impersonation token.
With TokenHandle=NULL it uses the thread's impersonation token, or obtains an
impersonation token from the primary context when not impersonating. Its BOOL
return reports API success; HasCapability reports capability membership. [3]

Constructed branch: return TRUE with HasCapability=FALSE is a completed negative
check, not permission. A broker calling with NULL after reverting may inspect
itself rather than the request's caller. A successful capability check is not
an object-specific access decision or authorization of arbitrary request
operands. Preserve the tested SID, token provenance, both results and branch.

## CheckTokenMembershipEx does not grant universal access
CheckTokenMembershipEx accepts an impersonation token or uses the current
effective token when NULL. CTMF_INCLUDE_APPCONTAINER permits AppContainer
participation subject to the other membership conditions, including an enabled
SID. BOOL success and IsMember are separate. [4]

Investigative inference: the flag is not a request to authorize every
AppContainer or bypass its restrictions. Record the SID actually tested and
the consuming policy branch. Do not replace a capability-specific check with a
generic group test merely because both functions return BOOL.

## Capability SID derivation and ownership
DeriveCapabilitySidsFromName returns two counted arrays: group SIDs under NT
Authority and capability SIDs under AppAuthority. The caller must LocalFree
each individual returned SID and each array. Legacy pre-Windows-10 capability
SIDs retain their published values; their service-group SID is hash based. [5]

The arrays are different outputs, not interchangeable aliases. Successful
derivation computes an identifier; it does not prove that a caller's token
contains it, that an object grants it access, or that a broker trusts it. Track
which array supplies an ACL or SECURITY_CAPABILITIES entry. Do not infer a
uniform fixed SID size from one example. The API page's broad minimum-OS table
is not used here to assert named-capability support on Windows XP.

## Less Privileged AppContainer removes the broad all-applications grant
Microsoft describes TokenIsLessPrivilegedAppContainer as the Less Privileged
AppContainer (LPAC) distinction:
ALL_APPLICATION_PACKAGES does not supply the usual access. LPAC creation is
imperative, not an appxmanifest declaration. [2] The launch guide uses
PROC_THREAD_ATTRIBUTE_ALL_APPLICATION_PACKAGES_POLICY with
PROCESS_CREATION_ALL_APPLICATION_PACKAGES_OPT_OUT. [1]

LPAC is not simply a lower integrity label, nor proof that all access is denied.
Inspect explicit package/capability grants and the effective token. Do not treat
an SDK enum declaration or a requested creation attribute as evidence that the
target OS accepted it. Preserve query/creation failures as unknown or failed,
not as successful isolation.

## LPAC grants and thread capabilities need their own evidence
Chromium commit 90ebe709881f7572f250d30e9ec77a39b5d8a482, CheckLpacToken,
constructs a descriptor granting Everyone bits 0x3, ALL_APPLICATION_PACKAGES
bit 0x1 and ALL RESTRICTED APPLICATION PACKAGES (S-1-15-2-2) bit 0x2.
Its LPAC AccessCheck(MAXIMUM_ALLOWED) assertion expects 0x2; the comment
contrasts ordinary AppContainer's 0x3. [6]

These are arbitrary test rights, not file rights. This is reviewed upstream
test evidence, not a local Windows execution. WithImpersonationCapabilities
also checks process and thread tokens against separately configured capability
sets. Investigative consequence: do not assume their capabilities are identical
or infer LPAC from the mere presence of the all-restricted-packages SID.

## Sources and limits
Primary API contracts and scoped source review, 2026-10-02. No AppContainer or
LPAC process was launched for this document; no sandbox escape was reproduced.

1. [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer): introduction, intersection and LPAC attributes; examples are not copied as production code.
2. [TOKEN_INFORMATION_CLASS](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-token_information_class): AppContainer, capabilities, SID and LPAC members.
3. [CheckTokenCapability](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokencapability): token selection and outputs.
4. [CheckTokenMembershipEx](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokenmembershipex): token, flag and membership.
5. [DeriveCapabilitySidsFromName](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-derivecapabilitysidsfromname): arrays and allocation ownership.
6. [Chromium pinned AppContainer tests](https://chromium.googlesource.com/chromium/src/+/90ebe709881f7572f250d30e9ec77a39b5d8a482/sandbox/win/src/app_container_test.cc): CheckLpacToken and WithImpersonationCapabilities.
7. [App capability declarations](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/app-capability-declarations): package trust level versus container status.
