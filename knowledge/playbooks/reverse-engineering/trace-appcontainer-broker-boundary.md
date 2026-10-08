---
id: playbook-re-appcontainer-broker-boundary
title: Reconstruct an AppContainer request and broker authorization boundary
kind: playbook
topics: [windows, appcontainer, capabilities, brokers, authorization, reverse-engineering]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Investigate one container-to-broker operation

For Windows AppContainer broker analysis, preserve the authenticated caller,
effective token, requested operation, checked object, object actually used and
transferred authority. Establish the intended policy before alleging a violation.
Direct client access and intentionally brokered access are different paths;
neither package membership nor endpoint acceptance alone proves method permission.

## Establish the actual isolation and request identities
Reviewed 2026-10-02. Local investigation workflow; no permission to change host
profiles, ACLs, firewall exemptions or running application policy. Record target
OS/build, process architecture, package manifest/trust level and creation path.
Trace SECURITY_CAPABILITIES and LPAC attributes through checked creation results
to the actual child token. Keep API failure separate from measured absence.

For the sensitive request, bind authenticated IPC context to the effective
token on the executing thread. Record user, AppContainer SID, capability SIDs
and attributes, token type/level, restrictions and integrity. Inspect callbacks
and worker handoffs separately. Identity asserted in payload text, a PID or
an executable path is not by itself this binding. Factual home:
reference-windows-appcontainer-token-capabilities.

## Prove endpoint reachability before auditing the privileged sink
Identify endpoint namespace, transport, interface registration descriptor,
callback and runtime authentication checks. Distinguish a default RPC descriptor
from a null DACL. Preserve a rejecting path as well as an accepted one. A
successful low-integrity desktop client is not proof that an AppContainer caller
can reach the same handler. Conversely, connection acceptance is not method
authorization. Trace operation number, dispatch and all policy branches to the
specific sink. Facts: reference-windows-appcontainer-resources-brokers.

Record direct access, broker-mediated access and returned-handle use as different
paths. For named objects retain full resolution context; for network operations
retain traffic direction, classification and exemption/filter state. Do not
weaken the environment to obtain a successful trace and then call that success
a deployment vulnerability.

## Bind the decision to the exact operation and object
Recover capability/membership APIs' success AND out-parameter branches. Identify
the token selected by a NULL handle before and after impersonation/reversion.
State the broker policy as caller principal + operation + object + allowed rights.
Track caller-controlled paths, IDs, handles, lengths and state through validation,
resolution, privileged use and response transfer. Use
playbook-re-sensitive-data-flow and reference-native-data-flow-alias-call-context
for alias and interprocedural tracking.

Constructed candidate: a broker permits opening object A, then resolves a mutable
client path and returns a writable handle to B. Evidence must show different
identities, a feasible change interval, transferred rights and absence of another
binding check. A capability check alone neither proves nor refutes this candidate.
Use existing filesystem and handle references for the specific acquisition API;
do not assume all handles are reauthorized after token changes.

## Separate expected delegation from a violated boundary
Write the smallest falsifiable claim: this authenticated container, under these
capabilities and policy, can cause this unauthorized operation on this object.
Include call coordinates, statuses, token/descriptor evidence, object identity,
grant/transfer masks and a control case. Label direct observations, documented
contracts and inference separately. A broker intentionally returning a permitted
resource is not an escape. A parser crash in the client is not proof of broker
code execution or privilege gain.

State which premises follow from instruction/API evidence and which depend on
unobserved runtime state. A statically supported path is not an observed execution;
an unavailable observation does not automatically invalidate a complete static
argument. Any separately authorized execution needs isolation and recorded policy.
Changing capability ACEs or network exemptions changes the conditions of the claim.
Arithmetic intersection models and upstream tests do not reproduce the Windows
security reference monitor or prove a target service's policy.

## Source basis
Workflow synthesis reviewed 2026-10-02; no specimen execution claimed.

- [CheckTokenCapability](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-checktokencapability): token selection and result distinction.
- [RpcServerRegisterIf3](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcserverregisterif3): interface gate.
- [Client impersonation](https://learn.microsoft.com/en-us/windows/win32/rpc/client-impersonation): thread context and reversion.
- [GetPackageFamilyNameFromToken](https://learn.microsoft.com/en-us/windows/win32/api/appmodel/nf-appmodel-getpackagefamilynamefromtoken): token-derived package identity.
