---
id: vulnerability-authorization-sandbox-host-capability-mediation-gap
title: Sandbox host capability exposed without object and operation mediation
kind: vulnerability
topics: [authorization, sandbox, brokers, capabilities, appcontainer, isolation-escape]
platforms: [cross-platform]
architectures: [any]
---

# Sandbox host capability exposed without object and operation mediation

## Definition and violated invariant

A sandbox-capability mediation vulnerability occurs when restricted code can invoke a host, broker or privileged peer capability without authorization binding the sandbox principal to the requested operation, object and rights. Brokered access is an intentional part of many sandboxes; the defect is broader delegation than the sandbox policy permits.

Direct denial followed by broker success does not prove an escape. The broker may intentionally create a narrowly scoped resource and transfer it under policy.

## Conditions that establish the issue

Recover the initiating sandbox identity and restrictions, broker endpoint reachability and authenticated caller binding, request framing, attacker-controlled operation and object selectors, host capability and effective security context, policy decision, resource acquisition, transferred rights or completed effect, recipient and lifetime. Prove the result grants authority outside the sandbox's permitted capability set.

Include package, origin, process or connection identity and race-resistant binding where the platform uses them. A client-supplied PID, path, package name or origin string is not authoritative by itself.

## Evidence that is not sufficient

A broker, IPC endpoint, privileged host process, file picker, socket broker, passed handle, sandbox denial or successful host operation is not sufficient. The request may be constrained to user-approved or policy-approved resources, the recipient may already hold equivalent authority, or transferred rights may be attenuated.

A sandbox label also does not establish the effective token, namespaces, entitlements or capabilities of the requesting process.

## Investigation sequence

Draw the capability path from sandbox principal through endpoint authentication, request decoding and broker policy to host object selection and effect or transfer. Record canonical object identity, operation-specific rights and recipient. Compare direct sandbox authority with the exact brokered result, and inspect alternate request types and failure fallbacks for inconsistent mediation.

At binary level, trace IPC fields into host APIs and transfer calls, then locate the caller/object policy that dominates them. Preserve the worker's effective context and any impersonation transitions.

## Hypothetical broker example

```text
request = { operation: "open", path: caller_supplied_path, rights: caller_supplied_rights }
host_handle = broker.open_as_host(request.path, request.rights)
broker.transfer_to_client(host_handle)
```

The path is vulnerable only if the sandbox client can select an object or rights outside its delegated policy and the broker transfers a usable capability without an independent authorization decision. A fixed allowlist or user-approved object capability can make the same architecture intentional.

## Primitive and impact limits

The direct primitive is a brokered host operation or capability outside sandbox policy. Impact is bounded by the object and rights granted. Classify isolation escape only when the capability reaches authority outside the initiating sandbox; host code execution needs an additional executable object or control primitive.

## Related knowledge and primary sources

AppContainer, Apple sandbox-extension, Android component and Linux descriptor references define concrete broker and capability mechanisms. The generic confused-deputy profile supplies the shared authority model.

Reviewed 2026-10-09 against Microsoft [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation) for token- and capability-based resource access and Chromium's [Windows sandbox design](https://chromium.googlesource.com/chromium/src/+/main/docs/design/sandbox.md) for one broker/target architecture. The example is hypothetical and does not assign either implementation's policy to another sandbox.
