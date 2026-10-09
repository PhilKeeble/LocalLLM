---
id: vulnerability-impact-privileged-service-capability-pipe-chain
title: Privileged service, credential, capability and named-pipe escalation chains
kind: vulnerability
topics: [privilege-escalation, confused-deputy, credentials, capabilities, services, named-pipes]
platforms: [cross-platform, windows, linux]
architectures: [any]
---

# Privileged service, credential, capability and named-pipe escalation chains

## Privileged confused-deputy request

A confused-deputy escalation requires a lower-authority caller to reach a more-authorized service or broker, control a request or selected object, and obtain a privileged effect the caller is not permitted to perform. Bind authorization to caller, operation, object, state, and delegated rights at the point of effect. A privileged process handling untrusted input is not enough when it correctly authorizes every requested action.

Trace identity through IPC, queues, callbacks, retries, worker handoff, and impersonation. A front-end check over one name does not authorize a different object selected after canonicalization or lookup.

## Credential, token, impersonation or security-context substitution

This chain exists when an attacker reads, duplicates, replaces, causes use of, or induces execution under a credential or security context with greater authority. Establish credential type, owner, rights, target scope, lifetime, binding to channel/session, and the operation that accepts it. A token-shaped string, handle value, UID, or SID is not proof of possession or usability.

For impersonation, identify the effective context at each check and effect and prove restoration behavior. Stealing a reference with insufficient access rights or a credential constrained to the attacker's existing scope may not yield escalation.

## Privileged file, service, task or startup replacement

An escalation through files or startup configuration requires lower-authority control over the final executable, library, script, configuration, service/task definition, or search-path-selected object that a higher-authority component later consumes. Recover final path resolution, links/reparse behavior, ownership and permissions, loader search, signature/policy checks, and the activation event.

A writable directory or unquoted-looking path is only a candidate. Prove the attacker can create or replace the name the privileged consumer actually selects and that activation occurs under greater authority.

## Excessive handle, descriptor, capability or IPC delegation

Delegation escalates authority when a higher-authority component transfers a handle, descriptor, capability, endpoint, or operation token whose granted rights, target object, recipient, or lifetime exceeds policy. Establish the original object and rights, transfer mechanism, recipient context, attenuation or duplication rules, and usable operation. Numeric handle equality across processes is meaningless without the transfer.

An endpoint can delegate authority by processing requests even when no OS object handle moves. Evaluate per-operation checks and revocation rather than equating connectivity with full server authority.

## Failed privilege drop or unsafe inherited authority

A privilege-drop chain requires an intended reduction followed by continued possession or reacquisition of rights outside policy. Trace real/effective/saved identities, groups, capabilities/privileges, namespaces, handles/descriptors, environment and loader state, failure results, and subsequent `exec` or operation. One changed UID or token field does not prove complete reduction.

Inherited ambient resources can retain authority after identity changes. Conversely, a retained saved identity or handle can be intentional; the vulnerability requires a reachable lower-trust phase that can use it contrary to policy.

## Named-pipe escalation chain

A named-pipe chain requires lower-privileged reachability, a controllable request or object, missing or incorrect authorization, a privileged effect, and demonstrated authority beyond the caller's existing rights. On Windows, separately establish the pipe security descriptor, actual client token, impersonation level, success of impersonation, reversion, and operation-level authorization. A pipe name, connection, or SYSTEM server is insufficient.

For client-side impersonation attacks, prove the privileged client connects to an attacker-controlled server and exposes a usable impersonation context under the target API's rules. For server-side deputies, prove the untrusted client controls the privileged operation or selected object.

## Primary sources and scope

Reviewed 2026-10-09 against Microsoft [named-pipe security and access rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), [`ImpersonateNamedPipeClient`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient), [process security and access rights](https://learn.microsoft.com/en-us/windows/win32/procthread/process-security-and-access-rights), POSIX [`exec`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html), and Linux [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html). Apply the target OS's actual credential and object-transfer contract.
