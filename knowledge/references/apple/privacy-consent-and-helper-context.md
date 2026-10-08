---
id: reference-apple-privacy-helper-context
title: macOS privacy consent, protected resources and helper context
kind: reference
topics: [tcc, privacy, consent, helpers, authorization, macos]
platforms: [macos]
architectures: [x86, x64, arm64]
---
# Privacy access and helper evidence

## Privacy consent is scoped to a protected resource and operation

Apple describes user-consent controls for protected files and separate permissions
for accessibility and automation. Transparency, Consent and Control (TCC) is the
privacy-policy boundary commonly investigated for such access. [1]

Identify resource category, requested action, attributed application/process and
effective decision. A file-mode permission or root UID does not itself establish
privacy consent. Neither an API import nor a purpose string proves consent was
granted or protected data was read. Protected categories and attribution details
require the target's actual policy, not an assumed release-wide list.

## A helper's successful access does not prove its requester was authorized

For analysis, distinguish the requester, intermediary, process attributed by
privacy policy and process performing the effect. Recover where caller identity
and per-operation authorization survive delegation.

One application's accepted access is not a transferable global permission merely
because another process can contact its helper. Conversely, delegated access can
be intentional and authorized. Retain the supplied object, caller policy and
actual effect before reporting confused authority. Private TCC database layouts
and undocumented attribution rules are not evidence contracts.

## Prompt, denial and retry need their actual result consumers

For investigation, map request, prompt or policy response, completion and failure
branches. Include asynchronous callbacks and retries when present. A visible
prompt does not prove acceptance, and lack of a prompt does not prove bypass:
existing grants, denial or managed policy need separate evidence.

Bind observed success to the selected resource and process generation. A generic
access error does not identify which policy denied the action. State missing
attribution or decision evidence explicitly instead of inferring a system-wide
privacy failure from one helper's behavior.

## Source and scope

Reviewed 2026-10-08. [Apple: Controlling app access to files in macOS](https://support.apple.com/guide/security/controlling-app-access-to-files-secddd1d86a6/web)
[1], consent and accessibility/automation paragraphs. Only conceptual resource
and consent distinctions adopted; no database schema, UI path, exact category
matrix or release-dependent attribution behavior. Workflow:
playbook-apple-service-authority; peer identity: reference-apple-xpc-peer-request-authority.
