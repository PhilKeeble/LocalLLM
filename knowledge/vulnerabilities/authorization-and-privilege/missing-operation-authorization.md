---
id: vulnerability-authorization-missing-operation-authorization
title: Missing authorization check for a sensitive action or resource
kind: vulnerability
topics: [authorization, access-control, missing-check, entry-points, privileges]
platforms: [cross-platform]
architectures: [any]
---

# Missing authorization check for a sensitive action or resource

## Definition and violated invariant

A missing-authorization vulnerability occurs when a reachable entry path performs a protected operation on an object without deciding whether the initiating subject may perform that operation on that object in the current context. Authentication establishes an identity; it does not authorize every action available to an authenticated principal.

The narrow finding is the absent mediation on an effective path. A public operation or an object intentionally shared with the caller does not require a denial merely because it is sensitive elsewhere.

## Conditions that establish the issue

Identify the initiating actor and authenticated principal, entry point and alternate routes, requested operation and operands, resolved live object, tenant or namespace, policy and state, effective execution security context, missing decision, and completed effect. Prove policy forbids the actor's tuple of subject, action, object and context while the path succeeds.

Include middleware, transport gates, object capabilities and downstream enforcement before concluding that the check is absent. Record configuration and deployment conditions that make the route reachable.

## Evidence that is not sufficient

A handler without a nearby role check, privileged process, sensitive API, client-hidden control, authenticated request, direct function call or successful operation is not sufficient. Authorization may be enforced by middleware, an unforgeable capability, object lookup, OS access control or a downstream service, and the operation may be intentionally public.

A denial on one route does not establish equivalent routes are mediated. Conversely, an unprotected status or discovery endpoint does not authorize a finding about a separate state-changing operation.

## Investigation sequence

Enumerate all externally reachable paths to the protected effect. For each, build the authorization tuple: subject, operation, resolved object, operands, tenant/session/channel context, policy generation and time. Trace identity from its trusted source through dispatch and object resolution into every policy decision and the effective context of the operation. Compare successful low-authority and intended high-authority paths.

At binary level, follow dispatch-table targets, early exits and shared helpers. A caller may enter after a common check through an alternate export, callback or IPC opcode, so control-flow dominance matters more than function proximity.

## Hypothetical missing-check example

```text
request = authenticate(connection, message)
if request.operation == "delete_account":
    accounts[request.account_id].delete()
```

The example is vulnerable only if the authenticated principal is not authorized to delete the resolved account and no other layer mediates the operation. Authentication and successful object lookup do not supply the missing action/object decision.

## Primitive and impact limits

The direct primitive is an unauthorized operation under the component's effective authority. Classify the result as horizontal access, vertical elevation or isolation escape from the actual principals and boundary crossed. Remote code execution requires the unauthorized operation itself to execute code or to create a separate execution primitive.

## Related knowledge and primary sources

`reference-logic-authorization-object-binding` provides the authorization tuple and policy-evidence model. Platform token, namespace and entitlement references define the effective subject at a particular boundary.

Reviewed 2026-10-09 against NIST [SP 800-53 Rev. 5 AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for enforcement of approved authorizations and [CWE-862](https://cwe.mitre.org/data/definitions/862.html) for the missing-authorization classification. The example is hypothetical; neither source establishes a target's policy or reachability.
