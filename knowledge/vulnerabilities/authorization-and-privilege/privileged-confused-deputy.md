---
id: vulnerability-authorization-privileged-confused-deputy
title: Privileged deputy performs an unapproved caller-selected action or object operation
kind: vulnerability
topics: [authorization, confused-deputy, brokers, services, delegation, privileges]
platforms: [cross-platform]
architectures: [any]
---

# Privileged deputy performs an unapproved caller-selected action or object operation

## Definition and violated invariant

A confused-deputy vulnerability occurs when a component uses authority it legitimately holds to perform an operation for a requester without binding the requester to the permitted action, object and operands. The deputy's privilege is not itself the defect; the defect is misuse of that authority outside the intended delegation contract.

This differs from an ordinary missing check inside a peer process because the authority provenance matters: the initiating actor causes a deputy to cross a boundary using credentials, handles, namespaces or privileges unavailable to that actor directly.

## Conditions that establish the issue

Identify the initiating actor and authenticated caller, IPC or invocation boundary, caller-controlled action and operands, deputy's effective security context and retained capabilities, intended delegation policy, selected object and namespace, authorization decision, completed effect and exact authority gained. Prove the caller cannot perform the effect directly but can induce the deputy to do it outside approved scope.

Account for caller impersonation, object capabilities, allowlisted operations and downstream access checks. A service may intentionally provide a narrow privileged function.

## Evidence that is not sufficient

A privileged service, broker, helper, root-owned binary, caller-supplied path, IPC endpoint or successful privileged operation is not sufficient. The caller may already possess equivalent authority, the operation may be the service's documented purpose, operands may be constrained to an authorized object or the deputy may act under the caller's context.

Running under a service account only identifies possible authority; recover the actual token, credential, namespace, entitlement or handle used for the effect.

## Investigation sequence

Draw an authority flow from caller through request parsing and identity selection to the deputy's operation. Label which fields the caller controls, where each is normalized or resolved, which security context performs every lookup and write, and what policy binds caller to action and object. Compare the caller's direct access with the deputy-mediated result using the same resolved object.

At binary level, trace IPC fields into privileged APIs and identify impersonation or credential switches around them. Follow failure and restoration paths so an apparent caller-context check is not separated from a later service-context effect.

## Hypothetical deputy example

```text
request = receive_from_authenticated_client()
destination = request.path
privileged_service.write_file(destination, generated_contents)
```

The path is vulnerable only if the client is not authorized to choose the resolved destination, the service opens or writes it with greater authority, and no object-constraining check intervenes. A service-owned directory selected object-relatively under a narrow policy can make caller-supplied leaf names acceptable.

## Primitive and impact limits

The direct primitive is a deputy-performed operation under authority unavailable to the requester. Impact depends on the operation, resolved object and deputy context: it may be horizontal access, vertical elevation or isolation escape. A privileged file write supports code execution only when activation, content control and trigger conditions are also established.

## Related knowledge and primary sources

`reference-logic-authorization-object-binding` and platform broker, token and filesystem references provide the underlying authority and resolution contracts. Named-pipe and WebView profiles specialize this invariant for particular deputies.

Reviewed 2026-10-09 against Norm Hardy's [The Confused Deputy](https://www.cs.umd.edu/~jkatz/security/downloads/capabilities.html) for the authority-provenance model and [CWE-441](https://cwe.mitre.org/data/definitions/441.html) for unintended proxy/intermediary behavior. The example is hypothetical and requires the target's delegation policy.
