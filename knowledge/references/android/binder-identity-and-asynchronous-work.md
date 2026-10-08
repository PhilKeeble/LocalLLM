---
id: reference-android-binder-identity-async
title: Binder identity clear/restore, delegated checks and asynchronous work
kind: reference
topics: [android, binder, identity, clear-calling-identity, async, delegation, authorization]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Binder identity transition evidence

## clearCallingIdentity changes thread IPC identity rather than process credentials

Binder.clearCallingIdentity resets incoming IPC identity on the current thread,
so subsequent local permission checks can use the service's own identity. It
returns an opaque token for restoreCallingIdentity. [1]

Recover checks before and after this transition, the selected object and the
authority intended for the operation. Clearing can be deliberate delegation;
its presence alone does not prove unauthorized use. Do not interpret it as an
OS-level UID change or as preservation of the original caller for later checks.

## Identity restoration must cover the actual dynamic scope

Binder.restoreCallingIdentity restores a previously cleared thread identity from
its returned token. [1] For analysis, pair token, thread and nesting through
success, exception, early return and callback paths.

An unrelated token or restore on a different worker does not establish the
original request context there. Restoring identity also does not undo an operation
already performed under service authority. Distinguish identity cleanup from
transaction rollback and retain the observed effect.

## Queued work needs explicit request authority evidence

For investigation, distinguish incoming Binder handling from a later job on
another thread or after transaction return. Calling UID outside the incoming
transaction reports local identity. [1]

Recover what authenticated identity/policy was captured, which object/action it
authorizes, whether it remains valid and how the job consumes it. A passed UID or
package string is not trusted merely because it is in a task object. Binder's
caller-supplied WorkSource attribution is not an authenticated caller replacement.
[1] Unknown delegation binding remains a gap, not proof of a completed bypass.

## Source and scope

Reviewed 2026-10-08. [Binder API](https://developer.android.com/reference/android/os/Binder)
[1], clear/restoreCallingIdentity, getCallingUid and getCallingWorkSourceUid.
Named thread-context contract only; no platform implementation offsets or
universal async framework propagation assumed. Workflow: playbook-android-service-authority.
