---
id: reference-windows-access-check-rights-integrity
title: Windows generic rights, ordered DACL checks, restricted SIDs and mandatory integrity
kind: reference
topics: [windows, access-checks, dacl, access-masks, restricted-tokens, integrity]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Recover the exact Windows access decision

## Generic rights need the object's mapping
Reviewed 2026-10-02. GENERIC_READ=0x80000000, GENERIC_WRITE=0x40000000,
GENERIC_EXECUTE=0x20000000 and GENERIC_ALL=0x10000000 map to object-specific
sets of standard/specific rights. MapGenericMask applies the supplied mapping;
it is not an authorization decision. [1][2]

Constructed private-object mapping: GenericRead maps to 0x00000005. Input
GENERIC_READ|0x00000002 becomes 0x00000007, retaining the explicit bit. This
example is not a Windows file/process mapping. Using another object's mapping
changes which operations are checked. Preserve original mask, mapping fields,
mapped mask and object type. A high generic bit is not itself a file offset,
page-protection constant or final granted-rights mask.

## Standard rights do not mean content read and content write
READ_CONTROL permits reading security-descriptor information other than the
system access-control list (SACL); WRITE_DAC changes its discretionary
access-control list (DACL); WRITE_OWNER changes its owner. SYNCHRONIZE
permits supported object waits. STANDARD_RIGHTS_WRITE equals READ_CONTROL,
not a universal data-write right. [3]

Investigative consequence: an operation that modifies security policy and one
that modifies object contents are different capabilities. Do not label a
READ_CONTROL-only handle as allowing arbitrary data reads, or a symbolic
STANDARD_RIGHTS_WRITE mask as permitting memory/file writes. Recover the
object-specific bits required by the eventual API and the actual grant. A
policy-changing right can be security-relevant even without immediate content
write access, but demonstrate the permitted state transition rather than
declaring every broadly named right equivalent to full control.

## The same low mask bit means different operations on different objects
For a process, 0x0001 is PROCESS_TERMINATE. For a file, 0x0001 is
FILE_READ_DATA; for a directory that value identifies
FILE_LIST_DIRECTORY. [4][5] Decode values by object type, not a global flag list.

Constructed observation: raw mask 0x0001 on a process handle supports the
termination-right interpretation, not file read. It does not by itself prove
the handle is valid or that termination was attempted. Conversely, reading a
file's data and listing directory entries share a numeric value but are different
operations. Record API, object kind, requested rights, actual granted rights
and result separately. Do not reuse PE section flags or memory-protection masks
to interpret an object access mask.

## Null and empty DACLs have opposite discretionary meanings
A null discretionary access-control list (DACL) supplies no discretionary access
restriction; an initialized empty DACL has no access-control entries (ACEs)
granting access. [6] These describe the DACL contribution, not
the whole access decision across mandatory policy, privileges and object rules.

Constructed inspection: a descriptor's DACL pointer is NULL versus a valid ACL
with AceCount=0. Reporting both as an empty ACL loses the essential distinction.
Do not confuse either with passing NULL for an API's optional security-attributes
argument, which has that API's default-security semantics. Retain descriptor
control/presence state and the actual ACL bytes. A DACL snapshot alone is not
proof that an existing handle lacks authority or that every attempted open
will succeed; bind the evidence to the operation being analyzed.

## ACE order matters; deny is not an unconditional global override
Windows examines applicable DACL ACEs in sequence, stopping on a relevant
denial or when requested rights have been granted; insufficient grants fail.
The preferred order puts explicit ACEs before inherited ACEs and deny before
allow within the documented groups. [7][8]

Constructed ordinary DACL-only check for one mapped right R, with both ACEs
applicable: [allow R, deny R] can grant before reaching the deny; reversing
them denies. This excludes conditional/object-specific ACE complications,
special privilege/owner grants and other policy checks. Do not sort the observed
ACEs merely to simplify analysis; that changes the decision being modeled.
Retain inheritance flags and applicability. A deny-only SID can match deny but
not allow ACEs; see reference-windows-tokens-sids-groups-impersonation.

## AccessCheck API success is not AccessStatus success
AccessCheck takes a client impersonation token with TOKEN_QUERY and a desired
mask already mapped to remove generic rights. Its Boolean return reports
whether the function succeeded; AccessStatus reports grant/denial. A failed
function does not set GrantedAccess; a denied check sets it to zero. [9]

Constructed call returns TRUE but AccessStatus=FALSE: a branch testing only
the function return may proceed after a denied decision. Conversely, TRUE and
AccessStatus=TRUE support only the supplied token, descriptor and requested
rights. The API does not bind arbitrary later paths or objects to that check.
An invalid descriptor lacking owner/group SIDs can fail the API; do not treat
stale output storage as a valid authorization result. Recover both output
locations and the actual success/failure branch before classifying the check.

## MAXIMUM_ALLOWED reports a mask, not universal authorization
For AccessCheck, MAXIMUM_ALLOWED asks for the maximum rights that the supplied
descriptor allows the client, returned in GrantedAccess. AccessCheck itself
does not generate an audit record. [9]

Constructed private-object decision: GrantedAccess=READ, while the later
operation requires WRITE. Successful maximum-allowed evaluation does not prove
WRITE was granted. Compare the operation's required mapped bits with the grant;
do not substitute a successful Boolean for that comparison. Also distinguish
this explicit access calculation from opening a kernel handle and from an
application's separate policy. The absence of an audit event is not proof
that no AccessCheck call occurred.

## Restricting SIDs add an intersection, not extra group authority
For ordinary restricting-SID tokens, both the enabled-SID check and the
restricting-SID check must permit the requested rights. CreateRestrictedToken
also supports WRITE_RESTRICTED, where restricting SIDs are considered for write
access only. [10][11] Preserve creation flags and target-version details.

Constructed ordinary restriction example: normal pass permits {READ,WRITE},
restricted pass permits {READ}. Effective permission is their intersection
{READ}, not union {READ,WRITE}. A deny-only group and a restricting SID are
different mechanisms; do not merge their lists into one set of enabled groups.
Conversely, apply the ordinary two-pass rule cautiously to a write-restricted
token's read request. Presence of a restricted token does not itself establish
that every privileged handle, IPC route or operation was constrained.

## Mandatory integrity can deny a DACL-permitted operation
Mandatory integrity control (MIC) evaluates integrity and mandatory policy before discretionary checks. Object
labels are in SACL mandatory-label ACEs; unlabeled objects are treated as medium.
The default no-write-up policy differs from optional no-read-up/no-execute-up
policies. [12] Integrity is not group membership or an all-purpose trust score.

Constructed non-AppContainer low-integrity caller requests write access to a medium object with
no-write-up: a DACL allow is insufficient. Conversely, no-write-up alone does
not establish no-read-up; inspect the policy bits and operation. A high-integrity
token does not make every DACL permit access. Record token level/policy, object
label, requested rights and actual API result. Do not infer an AppContainer's
complete capability/broker policy solely from its integrity level, or confuse
a label ACE in the SACL with a discretionary allow ACE. AppContainer-specific
interaction with medium/lower resource labels is qualified in
reference-windows-appcontainer-token-capabilities; do not generalize this
ordinary low-IL example to every container access path.

## Rights sources
All sources reviewed 2026-10-02; documented Windows contracts, not native tests.
Examples are constructed and their access-check simplifications are explicit.

1. [Generic rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/generic-access-rights): values and object-specific mapping.
2. [MapGenericMask](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-mapgenericmask): mapping and retained nongeneric bits.
3. [Standard rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/standard-access-rights): security descriptor, wait and combined masks.
4. [Process rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights): PROCESS_TERMINATE value.
5. [File rights](https://learn.microsoft.com/en-us/windows/win32/fileio/file-access-rights-constants): FILE_READ_DATA and FILE_LIST_DIRECTORY.

## Access-decision sources
6. [Null and empty DACLs](https://learn.microsoft.com/en-us/windows/win32/secauthz/null-dacls-and-empty-dacls): discretionary distinction.
7. [DACL evaluation](https://learn.microsoft.com/en-us/windows/win32/secauthz/how-dacls-control-access-to-an-object): ordered checks and termination.
8. [ACE ordering](https://learn.microsoft.com/en-us/windows/win32/secauthz/order-of-aces-in-a-dacl): explicit/inherited and deny/allow ordering.
9. [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck): parameters, separate outputs, descriptor validity, MAXIMUM_ALLOWED and auditing.
10. [Restricted tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/restricted-tokens): two access checks.
11. [CreateRestrictedToken](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-createrestrictedtoken): WRITE_RESTRICTED qualification; do not universalize historical flag values.
12. [Mandatory integrity](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control): labels, policy and discretionary-check relationship.
