---
id: reference-windows-tokens-sids-groups-impersonation
title: Windows tokens, SIDs, group checks, and impersonation
kind: reference
topics: [windows, access-tokens, sids, groups, impersonation, authorization]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows tokens, SIDs, group checks, and impersonation

## Token identity is not a single administrator Boolean

Reviewed 2026-10-02. Windows process primary tokens and thread impersonation
tokens describe security contexts, including user/group security identifiers
(SIDs), privileges, token
type and restriction information. OpenProcessToken selects a process primary
token; OpenThreadToken selects a thread impersonation token. [1]

Record the exact token source and thread at the sensitive operation. Group
membership, enabled privileges, integrity and elevation are different properties;
a SID's display name is not evidence that the intended principal was selected.
A service process identity does not by itself describe an impersonating worker's
effective context. Conversely, a token handle stored in a variable is not proof
that the executing thread is using that token. Tie identity evidence to the
operation and time, not only to process startup or an earlier request.

## Group membership has a selected token and a separate Boolean result

CheckTokenMembership requires an impersonation token with TOKEN_QUERY when
an explicit handle is supplied. NULL selects the calling thread's impersonation
token, or a duplicate of the process primary token if not impersonating. The
function return reports API success; IsMember reports the membership result. [2]

Constructed service path: a worker checks NULL without establishing client
impersonation, then authorizes a client request using its own enabled groups.
The intended and tested identities differ. Prove the actual worker context
before reporting this path; do not infer it from the NULL argument alone.
A nonzero function return with IsMember=FALSE is not membership. Preserve both
values and the branch that consumes them. This API is not a general test of
elevation, integrity, privilege enablement or operation-specific authorization.

## Enabled, disabled and deny-only groups are different
An access-control entry (ACE) is a rule in an access-control list. An enabled SID
participates in allow and deny ACE checks. A disabled SID is
ignored unless marked deny-only; a deny-only SID participates in deny ACEs but
not allow ACEs and cannot be reenabled with AdjustTokenGroups. [3]

Constructed nonrestricted token contains group G only as deny-only. An allow
ACE for G does not grant access merely because G appears in TokenGroups.
An applicable deny ACE for G can still deny it. Preserve SID attributes when
interpreting a token dump; dropping them changes the access-check meaning.
CheckTokenMembership also considers restricting SIDs for restricted tokens;
Microsoft directs AppContainer membership checks to CheckTokenMembershipEx. [2]
Do not replace a full requested-rights check with raw SID presence or apply an
unqualified group-membership result to every restricted-token configuration.

## Impersonation level limits what the server may do as the client
SecurityIdentification permits inspecting client security information for
access decisions, not acting as that client. SecurityImpersonation permits
local impersonation; SecurityDelegation permits remote impersonation, subject
to the surrounding authentication configuration. SecurityAnonymous does not
provide client identification or impersonation. [4]

Investigative consequence: successfully obtaining client identity information
does not establish that a later resource open runs with that client's authority.
Record token type, level, actual impersonation API result and the executing
thread. A token that is suitable for a private-object access decision is not
automatically suitable for every process-creation or remote-operation API.
Check that API's contract instead of treating all token handles as interchangeable.

## Impersonation entry and restoration require separate success evidence

Impersonation is thread-scoped. [1] RevertToSelf ends supported Win32 client
impersonation; Microsoft specifies RpcRevertToSelf/RpcRevertToSelfEx after
RpcImpersonateClient. If RevertToSelf fails, client context remains; Microsoft
advises shutting down the process rather than continuing. [5]

Do not collapse entry failure and reversion failure into one identity rule.
Failure to enter the intended client context does not establish that context;
continued work may use server authority or a previously active context.
Failure to revert does not prove restoration of server identity. Trace entry,
operation and matching reversion on success/error paths and across callbacks
or worker dispatch. Merely calling the cleanup routine is not proof it worked.
Keep any intended outer impersonation/restoration contract explicit. Opening
an IPC endpoint or knowing a PID still does not authorize a specific operation.

COM's CoRevertToSelf restores pre-COM-impersonation authentication, not
necessarily the process primary token. Its call-scoped, non-counted restoration
contract is in reference-windows-com-rpc-authentication-impersonation; do not
generalize a Win32 reversion rule to every API family.

## AdjustTokenPrivileges can succeed without assigning every request
AdjustTokenPrivileges cannot add privileges absent from the token. A nonzero
return can accompany ERROR_NOT_ALL_ASSIGNED, even when nothing was adjusted.
Disabling and removing differ: a removed privilege cannot be reenabled in
that token. [6] TOKEN_ADJUST_PRIVILEGES controls this token operation.

Constructed trace: the caller requests a missing privilege, sees a nonzero
return and assumes its next privileged operation will succeed. That inference
is unsupported without the documented last-error/result check and actual
operation result. Conversely, a privilege's presence does not prove enablement
or exercise. Capture requested LUID/attributes, token identity, previous state,
API result and immediate error status; a later unrelated GetLastError value
is not evidence about this adjustment.

## OpenAsSelf selects the access-check context, not a different token
OpenThreadToken targets the supplied thread's token. OpenAsSelf=TRUE performs
the open access check under process-level security; FALSE uses the calling
thread's current context. This allows a caller impersonating at identification
level to open a thread token using process authority. Anonymous impersonation
tokens cannot be opened. [7]

Constructed server call opens its worker's client token with OpenAsSelf=TRUE.
That does not mean the returned handle names the process primary token or that
impersonation ended. Distinguish the object being opened from the identity used
to authorize the open. Capture failure status rather than silently substituting
the process token whenever a thread-token open fails.

## Token-handle access rights are not privileges held by the token
OpenProcessToken requests rights on the token object; its process handle needs
PROCESS_QUERY_LIMITED_INFORMATION under the documented current contract. [8]
TOKEN_QUERY permits inspection; TOKEN_DUPLICATE permits token duplication;
TOKEN_ADJUST_PRIVILEGES permits privilege adjustment. Token objects do not
support SYNCHRONIZE. [9]

Constructed handle has TOKEN_QUERY to a token containing a powerful privilege.
This does not confer TOKEN_ADJUST_PRIVILEGES or make the executing thread use
that token. Conversely, a broad token-handle mask does not prove the token has
any particular enabled privilege. Keep handle grants, token contents and active
execution context as three separate observations. Historical process-query
requirements must be checked for the target OS, not inferred from current names.

## DuplicateTokenEx creates a token; DuplicateHandle does not convert its type
DuplicateTokenEx requires TOKEN_DUPLICATE and creates a new token of the
requested primary/impersonation type. Its desired-access value zero requests
the existing handle's rights, not a zero-rights token; MAXIMUM_ALLOWED requests
rights valid for the caller. DuplicateToken can create only impersonation
tokens, unsuitable for CreateProcessAsUser. [10]

Constructed flow duplicates an impersonation-token handle using DuplicateHandle
and passes it to a primary-token API. Another handle to the same token is not
token-type conversion. Track the actual API, requested TokenType, result and
output handle. Creating a token does not itself activate it on a thread or
launch a process. Handle-reference semantics:
reference-windows-handle-authority-transfer; launch contracts:
reference-windows-process-creation-context.

## Common interpretation errors

- Administrator group membership is not the same as an elevated token.
- A privilege present in a token may be disabled.
- Integrity levels influence mandatory integrity control, not discretionary
  group membership.
- A process primary token and a thread impersonation token can represent
  different principals.
- A successful access check for one object/right does not authorize unrelated
  operations.

## Identity and group sources
Reviewed 2026-10-02; documented Win32 contracts, not a target token inspection.
Examples are constructed. Stable source ID retained during this accuracy audit.

1. [Access tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens): token contents, primary/impersonation selection and APIs.
2. [CheckTokenMembership](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokenmembership): handle requirements, NULL selection, outputs, restricting SIDs and AppContainer caveat.
3. [SID attributes](https://learn.microsoft.com/en-us/windows/win32/secauthz/sid-attributes-in-an-access-token): enabled and deny-only semantics.

## Context and privilege sources
Reviewed 2026-10-02. API-specific authentication and delegation restrictions
remain additional requirements, not promises made by an enum value.

4. [Impersonation levels](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-security_impersonation_level): identification, local and remote scope.
5. [RevertToSelf](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-reverttoself): failure context and RPC-specific reversion.
6. [AdjustTokenPrivileges](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-adjusttokenprivileges): rights, partial assignment and removal.

DACL, generic-rights, restrictions and integrity facts:
reference-windows-access-check-rights-integrity.

## Token acquisition and duplication sources
Reviewed 2026-10-02; token objects, their handle grants and current context are
different layers. API outcomes have not been reproduced on a target.

7. [OpenThreadToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openthreadtoken): OpenAsSelf and anonymous-token limitation.
8. [OpenProcessToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken): process-query and requested token access.
9. [Token access rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-rights-for-access-token-objects): object-specific rights and unsupported SYNCHRONIZE.
10. [DuplicateTokenEx](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-duplicatetokenex): new token type, rights request and DuplicateToken distinction.
