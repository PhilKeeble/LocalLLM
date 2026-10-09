---
id: vulnerability-authorization-caller-name-stale-object-authorization
title: Broker authorization bound to a caller-controlled name or stale object
kind: vulnerability
topics: [authorization, brokers, identity-binding, stale-objects, pid-reuse, time-of-check]
platforms: [cross-platform]
architectures: [any]
---

# Broker authorization bound to a caller-controlled name or stale object

## Definition and violated invariant

A broker identity-binding vulnerability occurs when authorization trusts a caller-provided name, PID, package, path, window, session label or other attribute that is not securely bound to the authenticated requester, or when a valid identity check is later applied to a replaced or recycled object generation. Authorization must bind a trusted principal and live object to the operation, not merely compare descriptive metadata.

Names and process identifiers can be useful telemetry. They become unsafe authorization inputs when an attacker can choose, race, reuse or detach them from the object that receives the privileged effect.

## Conditions that establish the issue

Recover the initiating actor and authenticated channel, claimed identity fields and attacker control, authoritative identity source, process/object generation and lifetime, check time, retained handle or reference, later resolution, broker security context, requested operation and final object. Prove a lower-authority caller can satisfy the descriptive check while the effect targets a different or unauthorized principal/object.

For reuse races, establish the original object's termination or replacement, identifier reuse and the later successful resolution. A theoretical reuse window without a controllable transition remains a candidate.

## Evidence that is not sufficient

A PID, executable name, package string, parent process, window handle, delayed operation, reopened path or separate identity lookup is not sufficient. The value may be kernel-bound to the connection, a retained handle may preserve object identity, lifetime guards may exclude reuse, or operation-specific authorization may occur later.

Signed code identity or package membership also does not automatically authorize every action or object for that code.

## Investigation sequence

Trace identity from transport- or OS-authenticated provenance into the policy decision, then follow the exact referenced object to the privileged effect. Record generation and lifetime, retain handles or capabilities where used, and mark every reopen or relookup. Compare caller-supplied fields with independently obtained token, peer-credential, audit-token or channel evidence.

At binary level, distinguish numeric identifiers and display strings from live kernel references. Follow close, process exit, reconnect and object replacement paths between check and use.

## Hypothetical stale-PID example

```text
if process_name(request.pid) == "trusted-client":
    queue_privileged_delivery(target_pid=request.pid)

later: duplicate_capability_into(open_process(task.target_pid))
```

If the trusted process exits and the identifier is reused before the later open, the capability can reach a different process generation. The finding requires feasible reuse and successful delivery; retaining and using a handle to the checked process would change the identity relation.

## Primitive and impact limits

The direct primitive is privileged service action or capability delivery to an unauthenticated or stale object. Impact depends on the operation and transferred rights. A process-name or PID mismatch alone establishes no privilege gain until the final recipient and authority are shown.

## Related knowledge and primary sources

Platform peer-identity, process-handle, audit-token and object-lifetime references define authoritative binding. The incorrect-authorization and capability-transfer profiles cover adjacent root causes.

Reviewed 2026-10-09 against Linux [`pidfd_open(2)`](https://man7.org/linux/man-pages/man2/pidfd_open.2.html) for stable process references and PID-reuse motivation, and Microsoft [kernel objects](https://learn.microsoft.com/en-us/windows/win32/sysinfo/kernel-objects) for process-relative handles and object lifetime. The example is hypothetical; exact stable-identity mechanisms are platform-specific.
