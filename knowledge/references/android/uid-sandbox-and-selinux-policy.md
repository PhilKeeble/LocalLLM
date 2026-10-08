---
id: reference-android-sandbox-policy
title: Android UID sandbox, SELinux domains and service reachability
kind: reference
topics: [android, sandbox, uid, selinux, mandatory-access-control, service-policy]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android principal and policy evidence

## Native code remains within the application's kernel-enforced sandbox

Android uses Linux user/group identities and process-level facilities for its
app sandbox; native code is subject to that boundary as well as managed code.
[1]

Recover actual process UID/groups, user/profile, sandbox and delegated handles.
Do not infer escape merely because the app calls native code or a syscall.
Default app separation is not proof every process has a unique UID: shared,
isolated or service identities require actual target evidence. A package name
alone is not an authenticated principal.

## SELinux permission is independent of ordinary UID permission

Android SELinux applies mandatory access control to processes, including root.
Enforcing mode rejects denied operations; permissive mode logs denials without
enforcing them. [2]

Bind subject domain, object/service label, class/action and effective enforcement
state. A root UID or successful discretionary permission check cannot alone prove
SELinux allows the effect. A denial log in permissive mode does not prove the
operation was blocked. Policy source must match the device's effective policy.

## Discoverability, transport and per-operation policy need separate evidence

For analysis, distinguish service lookup, Binder/driver access, accepted request
and resource effect. A broker may intentionally cross a resource boundary under
its own authority, while retaining responsibility for requester policy.

One allowed service call cannot establish all resources are accessible. One
denial also cannot establish every alternative route is closed. State the actual
caller, instance, request and gate rather than claiming universal isolation from
a label or version name. HAL scope: reference-android-native-hal-boundary.

## Sources and scope

Reviewed 2026-10-08. [AOSP Application Sandbox](https://source.android.com/docs/security/app-sandbox)
[1], kernel/native-code paragraphs; [SELinux in Android](https://source.android.com/docs/security/features/selinux?hl=en)
[2], mandatory control and enforcement modes. No release-specific UID formula,
default-policy history or universally enabled mechanism asserted.
Workflow: playbook-android-service-authority.
