---
id: vulnerability-authorization-incorrect-privilege-transition
title: Incorrect privilege assignment, inheritance, retention, or drop
kind: vulnerability
topics: [authorization, privilege-drop, inheritance, credentials, capabilities, process-creation]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect privilege assignment, inheritance, retention, or drop

## Definition and violated invariant

A privilege-transition vulnerability occurs when a process, thread, child or delegated task receives or retains authority outside its intended post-transition context because identity, groups, capabilities, privileges, descriptors, handles, namespaces or tokens are assigned, inherited or dropped incorrectly. Changing one credential field does not establish the complete effective authority of later operations.

This differs from unnecessary privilege in a deliberately configured process: the defining evidence is a transition whose intended result and actual result disagree.

## Conditions that establish the issue

Recover pre-transition credentials and capabilities, target identity and policy, API and requested change, result status, affected threads, saved/restorable identities, supplementary groups, privileges and capability sets, namespaces, inherited handles or descriptors, child token and environment, post-transition context and final operation. Prove the retained or misassigned authority enables an operation forbidden to the intended resulting subject.

Account for platform rules across fork, clone, exec, process creation and thread pools. A successful UID, token or integrity change may leave unrelated authority channels intact.

## Evidence that is not sufficient

A call named `setuid`, disabled privilege, low-integrity label, restricted token, dropped capability, child process, inheritable handle or unchecked return is not sufficient. The transition may succeed completely under its contract, retained resources may be intentional and narrow, or a later sandbox and object policy may deny the operation.

Likewise, a failed drop is not exploitable unless execution continues into attacker-influenced work with excess authority.

## Investigation sequence

Create before-and-after authority inventories covering identity fields, group and privilege attributes, capability sets, namespace mappings, handles/descriptors and security policy. Follow the exact transition result and all subsequent threads or children. Bind each retained authority to a concrete operation and object rather than reporting a broad process label.

At binary level, trace return values, last-error conventions, requested IDs or token types and process-creation flags. Distinguish a token handle from activation of that token and descriptor inheritability from actual inheritance.

## Hypothetical failed-drop example

```text
set_process_identity(unprivileged_identity)   // result ignored
process_untrusted_requests()
```

The path is vulnerable only if the transition can fail or is incomplete, the program continues, the actual context retains forbidden authority, and an untrusted request reaches an operation using it. A successful platform-specific transition may still require separate review of groups, capabilities and inherited resources.

## Primitive and impact limits

The direct primitive is execution or resource access with authority outside the intended post-transition context. Classify the exact retained right and boundary crossed. Code execution or privilege escalation requires attacker influence over an operation that exercises that right; excess authority without such a path is exposure, not a completed escalation.

## Related knowledge and primary sources

Linux credential/drop/exec, Windows token/process-creation and handle-inheritance references provide concrete transition contracts. This profile supplies the shared evidence model.

Reviewed 2026-10-09 against Linux [`setuid(2)`](https://man7.org/linux/man-pages/man2/setuid.2.html) and [`execve(2)`](https://man7.org/linux/man-pages/man2/execve.2.html) as one platform's identity and execution-transition contracts, and Microsoft [access token](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens) documentation for primary and impersonation token distinctions. The example is hypothetical and does not imply identical Unix and Windows semantics.
