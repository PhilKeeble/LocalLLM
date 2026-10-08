---
id: playbook-re-windows-access-decision
title: Validate a Windows token, requested right and access-decision path
kind: playbook
topics: [windows, authorization, access-checks, tokens, impersonation, security-descriptors]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Reconstruct one Windows authorization decision

## Identify the operation and token actually used
Reviewed 2026-10-02. Local investigation workflow, not an instruction to alter
tokens, ACLs or privileges on the analysis host. Record target OS/build, thread,
API call, object identity/type and the intended caller/operation policy.
Distinguish an explicit AccessCheck from an object open, a membership test,
privilege adjustment and an application-specific authorization branch.

Trace token provenance, primary/impersonation type, level and the exact thread
context. Record relevant group attributes, restricting SIDs, privileges and
integrity independently. Inspect entry and matching reversion results, including
worker/callback paths. Do not infer successful impersonation from a saved token
handle or successful restoration from a cleanup call. Facts:
reference-windows-tokens-sids-groups-impersonation.

## Decode the descriptor and requested operation without changing them
Preserve original mask, generic mapping, mapped rights and actual object type.
Retain DACL presence/null/empty state, ACE order, SID attributes and applicability;
do not sort ACEs before deciding what the original check does. Preserve mandatory
label/policy separately from discretionary grants and token restrictions.

Bind the checked descriptor/object to the object later used. An application
checking one name and later resolving another object needs identity evidence.
Requested access, computed grants and rights on a returned/inherited handle are
separate observations. This workflow does not assume a later token or ACL change
rechecks every existing handle. Handle acquisition/transfer requires its own
API contract and evidence; use playbook-re-windows-handle-child-authority.
Access-check facts:
reference-windows-access-check-rights-integrity.

## Follow both the API status and the authorization output
Locate the Boolean return, out-parameter storage, relevant immediate error
status and branch conditions. Identify which outputs are valid after failure.
For maximum-allowed calculations, compare the actual grant with the subsequent
operation's required mapped rights. For privilege adjustment, verify assignment
rather than treating a nonzero return as evidence all privileges were enabled.

Constructed candidate: AccessCheck succeeds as a function, reports denial in
AccessStatus, but the caller branches only on the function return. Preserve that
path and the resulting sensitive action; a missing IsMember/AccessStatus use is
not enough if another independent check rejects the operation. Capture both
allowing and rejecting paths without assuming nearby checks authorize the same
object, rights or token.

## Report the smallest supported boundary conclusion
Retain token/descriptor snapshots, call coordinates, exact masks, output values,
failure/reversion handling and the affected object operation. Classify observed
results, contract-based inference and unresolved environmental policy separately.
A DACL grant does not alone establish complete OS authorization; a denied open
does not prove a separately acquired handle lacks authority.

Use only authorized, isolated experiments to test uncertain behavior. Do not
modify production ACLs or token state to complete an evidence checklist. Simple
mask/set models do not reproduce the full Windows security reference monitor.
For broker semantics beyond object rights, use
reference-windows-privileged-service-broker-boundaries.

## Source basis
Reviewed 2026-10-02. Workflow synthesized from these primary contracts and the
linked factual homes, not a claim that a specimen was executed.

- [AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck): explicit decision inputs and outputs.
- [CheckTokenMembership](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokenmembership): token selection and separate membership output.
- [Mandatory integrity](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control): separate mandatory-policy layer.
