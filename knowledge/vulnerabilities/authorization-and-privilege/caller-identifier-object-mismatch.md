---
id: vulnerability-authorization-caller-identifier-object-mismatch
title: Caller-controlled identifier resolves an object outside the authorized scope
kind: vulnerability
topics: [authorization, idor, object-binding, tenants, ownership, identifiers]
platforms: [cross-platform]
architectures: [any]
---

# Caller-controlled identifier resolves an object outside the authorized scope

## Definition and violated invariant

An insecure direct object reference or identifier-to-object mismatch occurs when a caller can change an identifier and make an operation resolve an object outside that caller's authorized scope because authorization is absent or bound to a different identifier, tenant, namespace or object generation. Identifier secrecy or unpredictability is not a substitute for authorization unless the value is intentionally an unforgeable capability under its contract.

This is a specific object-binding authorization failure. It can produce horizontal access between users or tenants without a nominal privilege-level increase.

## Conditions that establish the issue

Recover the initiating principal and tenant, attacker-controlled identifier representation, decoding and normalization, lookup namespace and uniqueness scope, resolved live object and owner, requested operation, authorization inputs, effective execution context and resulting read or change. Prove the identifier selects a forbidden object that the caller can access or modify.

For composite or recycled IDs, include every namespace component and object generation. Establish enumeration or acquisition feasibility only to the degree required by the actual interface.

## Evidence that is not sufficient

A numeric ID, sequential value, UUID, global table, object endpoint, changed parameter, successful lookup or missing owner field is not sufficient. The lookup may be scoped by trusted tenant state, a policy helper may authorize the resolved object, the identifier may convey capability authority, or the object may be public.

Client-side filtering and difficult guessing do not prove server authorization, but their absence also does not prove a forbidden object was reachable.

## Investigation sequence

Trace the identifier from request bytes through decoding, tenant/namespace selection and lookup to a concrete object generation. Record which identity selects each namespace component and compare the resolved owner or policy attributes with the authenticated principal before the effect. Exercise equivalent routes, batch endpoints and indirect references conceptually in the data flow.

At binary level, distinguish a global lookup keyed only by object ID from a composite lookup that incorporates trusted tenant or owner state. Follow the returned pointer or handle into the operation and any downstream policy check.

## Hypothetical tenant-scope example

```text
caller = authenticated_session.principal
document = global_documents[request.document_id]
return document.contents
```

The example is vulnerable only if the caller can select a document owned by another principal or tenant and no policy authorizes that read. A lookup keyed by trusted `(caller.tenant, document_id)` plus an object-level read check can make the same external identifier safe.

## Primitive and impact limits

The direct primitive is unauthorized access to or modification of the resolved object. Classify read, write, delete or action authority and whether it is horizontal, vertical or cross-tenant. Broader escalation requires the selected object or operation to control additional credentials, policy or execution.

## Related knowledge and primary sources

`reference-logic-authorization-object-binding` provides identifier, tenant and capability distinctions. Parser and object-lifetime references apply when decoding or recycling changes the selected object.

Reviewed 2026-10-09 against [CWE-639](https://cwe.mitre.org/data/definitions/639.html) for authorization bypass through caller-controlled keys and NIST [SP 800-53 Rev. 5 AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for the underlying authorization requirement. The example is hypothetical; identifier shape alone is not a finding.
