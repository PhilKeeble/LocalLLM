---
id: vulnerability-windows-privileged-named-pipe-confused-deputy
title: Privileged Windows named-pipe confused deputy
kind: vulnerability
topics: [windows, named-pipes, confused-deputy, authorization, privilege-boundary]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Privileged Windows named-pipe confused deputy

## Definition and violated invariant

A privileged named-pipe confused deputy exists when a less-trusted client can ask a pipe server to perform an operation with the server's greater authority without authorization that binds the authenticated caller to the requested action, operands and resolved object. The invariant is per-operation authorization over the tuple `(caller, action, object, operands, context)` at the point the privileged effect is selected.

A broadly reachable pipe, a LocalSystem server or client-controlled path is not independently a vulnerability. The defect requires an operation outside the caller's permitted authority that the server performs because it lends its own authority without the required binding.

## Conditions that establish the issue

Prove that the initiating principal can connect and send a complete accepted request, that attacker-controlled fields select a sensitive action or object, that no adequate caller-bound decision covers the final resolved operands, and that the server performs the effect with greater authority. Record pipe DACL, local/remote reachability, client token or authenticated protocol identity, request frame, dispatch path and effective token at the sensitive API.

If the server intentionally exposes the operation to every reachable client, establish the contrary policy before calling it unauthorized. Product expectations, UI restrictions and executable-name checks are not substitutes for an enforceable authorization contract.

## Evidence that is not sufficient

Default pipe permissions, a permissive DACL, `CreateNamedPipe`, `ImpersonateNamedPipeClient`, `GetNamedPipeClientProcessId`, or a privileged file API is not sufficient. The endpoint may enforce protocol authentication and per-action policy, or the operation may deliberately be public and narrowly scoped.

A client PID or image path is diagnostic evidence, not durable authorization identity. PIDs can be reused and process-image inspection races with exit or replacement. Likewise, successful connection authenticates only what the pipe security and protocol establish; it does not authorize every message.

## Investigation sequence

Recover the effective pipe name, namespace, server instances, creation flags, security descriptor and requested client access. Reconstruct byte versus message mode, length fields, partial reads and connection generations so identity and requests are not accidentally joined across clients. Determine the principal from a bound token or authenticated protocol, not a client-supplied identity field.

Trace every dispatch value to the sensitive operation, including path canonicalization, handle transfer, object lookup and later substitutions. At that operation, establish whether the thread is impersonating the client or has reverted to the service token, which access check ran, and whether an explicit policy binds that caller to the final action and object.

## Constructed deputy example

This pseudocode represents a service that accepts an output path and writes using its own token after parsing the request:

```c
request = read_complete_pipe_message(pipe);
if (request.operation == EXPORT) {
    handle = open_for_write_as_service(request.output_path);
    write_export(handle, request.record_id);
}
```

The path is vulnerable only if a reachable less-privileged client can select a forbidden target and the service neither performs the open under appropriately impersonated client authority nor enforces an equivalent caller/action/object policy. A protected destination that rejects the service, a strict server-owned target mapping, or authorization over the final object can refute the constructed case.

## Authority and request flow

```text
client principal
  -> pipe DACL and connection
  -> complete framed request
  -> authenticated client identity
  -> requested action and operands
  -> canonicalized or resolved object
  -> authorization for that caller/action/object
  -> effective token at privileged operation
  -> observable effect
```

Keep these stages distinct. Impersonation can make an OS object access use client authority, but it does not validate semantic operands such as another user's record ID. Explicit authorization can safely permit a service-token operation, but only for the scope actually checked.

## Primitive and impact limits

The direct primitive is an unauthorized operation performed by the deputy. Classify it precisely: chosen-file write, protected-file read, handle opening, service configuration, process launch, registry modification or another action. A privileged operation is not automatically arbitrary read/write, and a chosen path may still be constrained by flags, content, namespace and access checks.

Privilege escalation requires a route from the demonstrated operation to greater effective authority. Code execution requires an executable or control-bearing target and a trigger under that authority. Report those additional steps rather than labeling every confused deputy as escalation.

## Related knowledge and primary sources

`reference-windows-named-pipe-security-identity` owns DACL, impersonation, PID, framing and connection-generation contracts. `reference-logic-authorization-object-binding` owns caller/action/object binding, and `reference-windows-privileged-service-broker-boundaries` owns service-token distinctions. Their decisive rules are repeated here for isolated use.

Reviewed 2026-10-09 against Microsoft [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), [Named Pipe Client Impersonation](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-client-impersonation), [`ImpersonateNamedPipeClient`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient), [`GetNamedPipeClientProcessId`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-getnamedpipeclientprocessid), and [MITRE CWE-441](https://cwe.mitre.org/data/definitions/441.html). The code and flow are constructed.
