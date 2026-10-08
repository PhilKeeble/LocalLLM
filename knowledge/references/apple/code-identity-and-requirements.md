---
id: reference-apple-code-identity-requirements
title: Apple code signatures, requirements, entitlements and executing identity
kind: reference
topics: [code-signing, requirements, entitlements, identity, notarization]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Signed identity and policy evidence

## Signature validity, requirement satisfaction and notarization are distinct

Apple distinguishes developer code signing from notarization's check for known
malware. Its requirement language evaluates Boolean predicates on signed code;
the verifier selects the requirements to apply. [1][2]

Record what was checked, under which policy, and the actual result. A valid
signature or notarization ticket cannot establish harmless intent, correct
authorization or the absence of unknown malicious behavior. A displayed identity
is not evidence that the executing service checked the same requirement.

## Signing identifiers and entitlement values are scoped predicates

Apple requirements can match the signature's identifier, certificate properties
and embedded entitlement dictionary. Existence tests and value comparisons are
different, and Boolean alternatives can allow acceptance through another branch.
An ad-hoc signature has no certificate identity. [2]

Recover the whole accepted predicate and input code object. A bundle-name match
does not replace signer trust; an entitlement-looking plist not bound to accepted
signed code does not prove a process possesses that entitlement. Do not infer
every capability from membership in one development team.

## Disk artifacts must be bound to the process or module under investigation

For analysis, distinguish a bundle on disk, selected architecture slice, main
executable, loaded module and running peer. Retain code-object identity and the
time of verification through loading or message handling.

A path reused after checking can name different content. Conversely, a changed
file does not prove a running process loaded that change. Code identity helps
bind evidence; it does not supply input validation or per-object permissions.
Use reference-apple-xpc-peer-request-authority for message-bound peer evidence.

## Sources and scope

Reviewed 2026-10-08. [Apple macOS signing process](https://support.apple.com/guide/security/app-code-signing-process-sec3ad8e6e53/web)
[1], signing/notarization distinction; [Requirement Language](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/RequirementLang/RequirementLang.html)
[2], Evaluation, Identifier, Certificate and Entitlement. Archived syntax details
are not a current cryptographic-policy or complete signature-layout reference.
Workflow: playbook-apple-service-authority.
