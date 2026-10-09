---
id: vulnerability-authorization-windows-named-pipe-permission-exposure
title: Windows named-pipe security descriptor grants unintended endpoint rights
kind: vulnerability
topics: [windows, named-pipes, dacl, permissions, ipc, pipe-instances]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows named-pipe security descriptor grants unintended endpoint rights

## Definition and violated invariant

A named-pipe permission vulnerability occurs when the effective pipe security descriptor grants an unintended principal connect, read, write or server-instance creation rights across a user, session or network boundary. The precise right matters: generic write can include `FILE_CREATE_PIPE_INSTANCE`, while read or connection access does not by itself authorize every application message.

Pipe DACL enforcement and application protocol authorization are separate. This profile establishes excessive endpoint or object rights; caller/action/object policy failures belong to the neighboring pipe profiles.

## Conditions that establish the issue

Recover the effective full pipe name and host, server instance and generation, creator security context, explicit or default security descriptor, owner and ordered DACL, requested and granted object-specific rights, local/remote-client flags, session and namespace, initiating principal, competing instance creation, protocol behavior and resulting access. Prove the unintended principal obtains and exercises the relevant pipe right.

For server-instance creation, establish the name collision or client-routing consequence and which instance receives a connection. Creation permission alone does not prove service impersonation.

## Evidence that is not sufficient

A NULL security-attributes argument, default descriptor, Everyone ACE, generic access mask, pipe name, successful open, `FILE_FLAG_FIRST_PIPE_INSTANCE` or remote-client setting is not sufficient. Decode the actual descriptor and requested rights, include other policy layers and show a security-relevant endpoint or data effect.

Do not apply mutex `Global` or `Local` namespace rules to pipe names. Record the pipe's actual naming and server location.

## Investigation sequence

Resolve the active pipe object and enumerate each server instance and connection generation. Decode generic rights into pipe-specific rights and evaluate the DACL for the initiating token. Trace client open mode, server creation flags and remote reachability into read, write, connect or instance creation. Then follow application framing separately.

At binary level, reconstruct `SECURITY_ATTRIBUTES`, descriptor construction and `CreateNamedPipe` arguments, checking all return paths and fallback creation without the intended descriptor.

## Hypothetical permission example

```text
pipe DACL grants GENERIC_WRITE to a broad user group
service assumes only its own executable can create server instances for that pipe name
```

Because pipe generic write includes the instance-creation right under the documented contract, the grant may permit another principal to create an instance. A finding still requires the actual DACL, successful creation or feasible collision and a security effect in client routing or data handling.

## Primitive and impact limits

The direct primitive is an unintended named-pipe object right. Read or write may expose protocol data; instance creation may enable collision or interception under additional connection behavior. Privilege escalation requires a client or server to trust the resulting endpoint or data in a way that grants greater authority.

## Related knowledge and primary sources

`reference-windows-named-pipe-security-identity` owns pipe DACL, rights, instance and remote-client contracts. Windows access-check references define token and ordered DACL evaluation.

Reviewed 2026-10-09 against Microsoft [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights) and [`CreateNamedPipe`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew). The example is hypothetical and does not infer application authorization from pipe access alone.
