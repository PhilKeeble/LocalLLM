---
id: reference-apple-containers-groups-authority
title: Apple app containers, app groups, extensions and keychain authority
kind: reference
topics: [containers, app-groups, extensions, keychain, entitlements, ipc, sharing]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Container and sharing evidence

## An app container and an app-group container have different sharing scopes

Apple's iOS sandbox model gives an app a separate home directory. Configured app
groups let associated apps/extensions share an on-volume container and preferences.
[1][2] macOS sharing needs its own applicable sandbox and entitlement evidence.

Bind an observed path to the selected app/group and actual access policy. A
container-shaped pathname or matching bundle prefix does not prove membership.
Shared storage is a declared communication surface; group members can still
supply malformed or stale content. Membership does not validate every record.

## Keychain access groups govern item access beyond a single process

Apple describes securityd checking keychain access-group and application
entitlements for item access; permitted groups allow sharing between apps. [3]

Recover item group, requesting process's accepted entitlements, accessibility
conditions and returned result. An app-group file read does not prove access to
all keychain items. Do not generalize the documented mobile keychain model to
every macOS keychain API or assume a bundle identifier alone grants key access.
Protected-key invocation and raw disclosure remain different claims.

## Extension and IPC boundaries need the actual executing principal

For analysis, distinguish containing app, extension, host, broker and recipient.
Shared developer ownership or group membership does not collapse these into one
process, one lifetime or one authorization decision.

Follow selected extension entry, message/data representation, caller binding and
resource effect. A helper can legitimately act for another component; establish
the permitted delegation before reporting excessive authority. A configured group
does not prove the extension launched or accessed a particular file/item.

## Sources and scope

Reviewed 2026-10-08. [iOS runtime sandbox](https://support.apple.com/guide/security/security-of-runtime-process-sec15bfe098e/web)
[1], separate-home concept; [App protection and groups](https://support.apple.com/guide/security/sec1a976c067/web)
[2], Joining an App Group; [Keychain data protection](https://support.apple.com/guide/security/secb0694df1a/web)
[3], access-group authorization paragraphs. No private database/container layout
or universal macOS policy assumed. Workflow: playbook-apple-service-authority.
