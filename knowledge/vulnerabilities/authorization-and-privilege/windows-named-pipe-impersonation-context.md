---
id: vulnerability-authorization-windows-named-pipe-impersonation-context
title: Windows named-pipe impersonation, level, or reversion context failure
kind: vulnerability
topics: [windows, named-pipes, impersonation, reversion, access-tokens, authorization]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows named-pipe impersonation, level, or reversion context failure

## Definition and violated invariant

A named-pipe impersonation vulnerability occurs when a pipe server assumes it is acting as the client but impersonation failed, selected the wrong message/client generation, provides an insufficient level for the intended operation, occurs on a different thread, or is not correctly reverted. Checks or resource access then execute under the service, a prior client or another unintended token.

On successful `ImpersonateNamedPipeClient`, the calling server thread impersonates the security context of the last message read from the pipe. That specific connection, read and thread relation must be preserved.

## Conditions that establish the issue

Recover pipe instance and connection generation, last completed read and client, worker thread, impersonation call and result, resulting token and level, checks and handles acquired during the scope, callbacks or handoffs, matching `RevertToSelf` result, early and error exits, instance reuse and later request effect. Prove a forbidden operation runs under the wrong effective context.

Differentiate access through a handle opened before impersonation from a fresh open during impersonation. The former can retain the service's earlier grant.

## Evidence that is not sufficient

An impersonation call, missing nearby revert, service account, token query, pipe reuse, failed open or privileged API is not sufficient. Structured cleanup may cover all exits, the operation may be explicitly authorized under service authority, or the handle may have been acquired under a different intended context.

Successful identity inspection at `SecurityIdentification` level does not establish authority to perform local or remote operations as the client.

## Investigation sequence

Construct a per-thread timeline from connection and read through impersonation, token-dependent checks, object opens and uses, reversion and next client. Record API returns and token level at each step. Join overlapped completion and request framing to the same connection generation before assigning client identity.

At binary level, follow Boolean results and all cleanup edges. Locate resource acquisition relative to impersonation, and distinguish `RevertToSelf` from COM or RPC reversion APIs.

## Hypothetical failed-impersonation example

```text
read_request(pipe, request)
ImpersonateNamedPipeClient(pipe)   // return ignored
open_and_modify(request.path)
RevertToSelf()
```

If impersonation fails and the server continues, the open can use the privileged service token. The path is vulnerable only if a reachable client controls a forbidden path, the open succeeds with greater authority and no equivalent policy check applies.

## Primitive and impact limits

The direct primitive is a pipe request checked or executed under unintended Windows token authority. Impact depends on the granted rights and selected object. A failed impersonation call is not itself escalation; the subsequent successful privileged effect is required.

## Related knowledge and primary sources

`reference-windows-named-pipe-security-identity` and Windows token/impersonation references define last-read, thread, level and reversion semantics. The generic impersonation profile covers shared reasoning across IPC systems.

Reviewed 2026-10-09 against Microsoft [`ImpersonateNamedPipeClient`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-impersonatenamedpipeclient), [Named Pipe Client Impersonation](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-client-impersonation), and [`RevertToSelf`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-reverttoself). The example is hypothetical.
