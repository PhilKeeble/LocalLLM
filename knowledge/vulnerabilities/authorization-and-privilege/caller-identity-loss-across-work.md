---
id: vulnerability-authorization-caller-identity-loss-across-work
title: Caller identity lost across IPC, callbacks, queues, asynchronous work, or retries
kind: vulnerability
topics: [authorization, caller-identity, ipc, async, queues, callbacks]
platforms: [cross-platform]
architectures: [any]
---

# Caller identity lost across IPC, callbacks, queues, asynchronous work, or retries

## Definition and violated invariant

A caller-identity propagation vulnerability occurs when work initiated for one actor crosses an IPC, callback, queue, worker, retry or reconnection boundary and later authorization uses no identity, the component's own identity or an identity belonging to another request. The required invariant is not automatic thread-context propagation; it is durable binding of the initiating authority and approved action/object to every delayed effect.

An application may intentionally replace caller authority with a service delegation. That transition is safe only when policy authorizes the caller's requested operation and operands before privileged execution.

## Conditions that establish the issue

Identify the initiating actor and authenticated identity source, incoming operation and object, authorization decision, task or callback contents, queue and retry identity, worker security context, policy validity interval, object generation and final effect. Prove the deferred path executes a forbidden operation because caller authority was dropped, substituted, confused or rebound.

Include request cancellation, connection reuse, pooled task objects and retries after authentication changes. A copied numeric UID or username is trusted only if its binding to the original authenticated request survives the transition.

## Evidence that is not sufficient

Queued work, a thread switch, missing thread-local principal, cleared IPC identity, callback, retry or service-context execution is not sufficient. The request may carry a server-created authorization capability, the operation may have been fully authorized before queueing, or the service may intentionally own the delegated action.

Conversely, copying a caller ID is not sufficient when action, object, tenant, generation or policy state can change before use.

## Investigation sequence

Draw the request from authenticated ingress through every handoff to completion. At each boundary, record which identity and authorization tuple is captured, who can modify it, how it is serialized, when it expires and which object generation it names. Compare the worker's effective token, credential or namespace with the identity used by the policy decision and effect.

At binary or managed-code level, follow task construction, closure captures, context suppression, message fields and retry reconstruction. Distinguish audit attribution from the principal actually used for authorization.

## Hypothetical queued-work example

```text
on_request(caller, message):
    work_queue.push({ action: message.action, object_id: message.object_id })

worker(task):
    if policy.allows(current_process_identity(), task.action, task.object_id):
        perform(task)
```

If the policy is meant to constrain the original caller, the task loses that identity and checks the service process instead. The path is vulnerable only if the service is more authorized, the caller controls the queued operation or object, and no earlier durable authorization covers the eventual effect.

## Primitive and impact limits

The direct primitive is execution under a substituted or unbound authority context. Impact equals the forbidden operation the worker completes and may be horizontal, vertical or cross-boundary. The identity loss does not itself prove code execution or resource access without the final operation.

## Related knowledge and primary sources

Platform references for Android Binder, Windows RPC/COM and managed execution contexts provide concrete propagation rules. `reference-logic-authorization-object-binding` supplies the tuple that must survive.

Reviewed 2026-10-09 against Android's [`Binder`](https://developer.android.com/reference/android/os/Binder) calling-identity contract as one concrete example of transaction-scoped identity and later worker behavior, and NIST [SP 800-53 Rev. 5 AC-3](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) for the authorization requirement. The example is hypothetical and does not generalize Binder mechanics to other IPC systems.
