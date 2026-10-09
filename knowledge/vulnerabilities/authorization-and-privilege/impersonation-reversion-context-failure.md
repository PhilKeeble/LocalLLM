---
id: vulnerability-authorization-impersonation-reversion-context-failure
title: Impersonation or reversion failure causes work under the wrong identity
kind: vulnerability
topics: [authorization, impersonation, reversion, security-context, services, threads]
platforms: [cross-platform]
architectures: [any]
---

# Impersonation or reversion failure causes work under the wrong identity

## Definition and violated invariant

An impersonation-context vulnerability occurs when a service intends to enter or leave a caller security context but fails, uses the wrong thread or token, mismatches API families, restores the wrong outer context, or continues after an unchecked transition result. The protected operation then executes under service, prior-client or other unintended authority.

Impersonation is platform- and mechanism-specific. Obtaining caller identity for inspection does not necessarily permit acting as that caller, and restoring from nested impersonation need not mean returning to the process primary identity.

## Conditions that establish the issue

Recover the initiating caller, prior thread context, token or credential type and level, impersonation API and result, dynamic scope, nested callbacks, operation thread, object access, matching reversion API and result, failure/exception paths, subsequent request reuse and final effective security context. Prove the wrong context performs or authorizes a forbidden operation.

Separate failure to enter caller context from failure to revert. The former can leave service or prior identity active; the latter can contaminate later work with caller identity.

## Evidence that is not sufficient

An impersonation API, missing visible cleanup, thread pool, failed call, token handle, service account or resource access is not sufficient. Structured cleanup may restore state, another layer may stop the request, the token may be identification-only, or the operation may use an already-open handle whose grant is independent of current identity.

Calling a reversion function is not proof it succeeded or matched the mechanism that established impersonation.

## Investigation sequence

Build a thread-specific state timeline: prior context, entry attempt/result, checks, resource acquisition and use, callbacks or handoffs, reversion attempt/result, and next work item. Label handles opened before and during impersonation separately. Verify the effective context at each sensitive operation using the platform contract, not the process label.

At binary level, follow Boolean or status returns and every exit edge, including exceptions and early returns. Identify whether work moves to a thread that never entered the caller context.

## Hypothetical failed-entry example

```text
if not impersonate_client(connection):
    log("impersonation failed")
open_and_modify(request.path)
revert_identity()
```

If failed entry leaves the worker under a more privileged service identity, continuing can perform the caller-selected operation with service authority. The finding requires the actual failure state, reachable privileged object and no independent authorization. It does not follow merely from an unchecked-looking function name.

## Primitive and impact limits

The direct primitive is a check or resource operation under unintended security context. Impact depends on the rights of that context and selected object. Existing handles, remote delegation limits and later authorization can narrow the effect; process privilege alone does not establish successful access.

## Related knowledge and primary sources

Windows token/impersonation, COM/RPC and platform credential references define mechanism-specific entry, level and restoration contracts. This profile keeps thread state and actual operation together.

Reviewed 2026-10-09 against Microsoft [`RevertToSelf`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-reverttoself) and [impersonation-level](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ne-winnt-security_impersonation_level) contracts as a concrete mechanism. The example is hypothetical; other OS and IPC mechanisms require their own context rules.
