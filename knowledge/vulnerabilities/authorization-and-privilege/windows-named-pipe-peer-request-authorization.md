---
id: vulnerability-authorization-windows-named-pipe-peer-request-authorization
title: Windows named-pipe peer or per-request authorization failure
kind: vulnerability
topics: [windows, named-pipes, peer-identity, authorization, ipc, request-framing]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows named-pipe peer or per-request authorization failure

## Definition and violated invariant

A named-pipe peer/request vulnerability occurs when a component trusts a connected pipe peer without establishing the peer identity required by its threat model, or accepts an operation without binding authenticated caller, action and resolved object. Pipe access control establishes only the principals and rights admitted by the effective descriptor; it does not authenticate a particular executable or authorize every protocol message.

Expected-peer authentication and per-operation authorization are distinct. A public pipe may need no product-peer restriction while still requiring object-level policy for sensitive methods.

## Conditions that establish the issue

Recover pipe name and server instance, DACL and granted access, local or remote reachability, connection generation, complete message framing, identity from impersonation token or authenticated protocol, expected-peer policy, caller-controlled action and object fields, per-method authorization, effective context and completed effect. Prove an unauthorized peer can submit an accepted forbidden request.

Bind identity to the same connection and message generation. PID or image-path inspection is diagnostic and race-prone unless joined to a durable authenticated object.

## Evidence that is not sufficient

A permissive pipe, successful connection, missing PID comparison, executable-name check, impersonation call, privileged server, message opcode or client-controlled ID is not sufficient. Protocol authentication or later object policy may enforce the boundary, or the endpoint and operation may intentionally be public.

Conversely, a restrictive DACL cannot replace semantic authorization among multiple permitted users or tenants.

## Investigation sequence

First reconstruct connection and message boundaries, including byte versus message mode and partial reads. Then bind a trusted caller identity to that connection and trace action/object fields through decoding and resolution. At the sensitive operation, compare the policy tuple and effective token with the final live object. Repeat for every opcode and alternate framing path.

At binary level, follow `ImpersonateNamedPipeClient`, token queries, authentication records and dispatch-table edges. Keep claimed identity fields separate from OS-derived identity.

## Hypothetical request example

```text
client connects to pipe and sends { operation: "read_record", record_id: X }
server returns record X because the client could connect
```

Connection permission does not authorize every record. The example is vulnerable only if policy forbids that connected principal from reading X, the request is accepted and no later caller/object check intervenes.

## Primitive and impact limits

The direct primitive is an operation or data access accepted from an unauthorized pipe peer or permitted peer acting outside its object scope. Impact is bounded by the server method and authority. A pipe connection alone does not establish code execution or elevation.

## Related knowledge and primary sources

`reference-windows-named-pipe-security-identity` supplies DACL, client-token, PID and framing contracts; `reference-logic-authorization-object-binding` supplies per-request policy. The privileged named-pipe deputy profile covers service-token operations.

Reviewed 2026-10-09 against Microsoft [Named Pipe Client Impersonation](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-client-impersonation), [`ImpersonateNamedPipeClient`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient), and named-pipe security documentation. The example is hypothetical.
