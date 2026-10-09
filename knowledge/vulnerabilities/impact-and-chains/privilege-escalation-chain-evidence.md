---
id: vulnerability-impact-privilege-escalation-chain-evidence
title: Privilege-escalation chain and authority-gain evidence
kind: vulnerability
topics: [privilege-escalation, authority, kernel-memory, scope, impact]
platforms: [cross-platform]
architectures: [any]
---

# Privilege-escalation chain and authority-gain evidence

## Privilege escalation is a demonstrated authority transition

A privilege-escalation chain begins with a defined actor and existing authority, traverses a reachable weakness and privileged component or resource, and ends with rights the actor did not already hold. Record the initiating principal, trust boundary, vulnerable operation, effective identity at the protected effect, selected object, and resulting permissions or capabilities. Code execution, a crash, or access to a privileged process does not alone establish gained authority.

Separate vertical escalation from horizontal cross-user or cross-tenant access. A same-user process escape can still be a meaningful gain when the destination has broader capabilities, integrity, sandbox grants, credentials, or resources.

## Privileged arbitrary read, write or kernel memory corruption

A privileged memory primitive supports escalation only when the lower-authority actor can trigger or control it and the resulting read/write reaches a security-bearing object in the privileged address space. Describe address/value/width constraints, object lifetime, synchronization, hardening, and the exact credential, code, page-table, function target, or policy state affected.

Kernel memory corruption is not synonymous with kernel code execution. A controlled read can expose protected data without changing authority; a write can crash before a useful consumer. Prove the resulting credential, execution context, or kernel-only operation and identify whether it persists beyond the affected task or boot.

## Local, remote, same-user and cross-user scope

State what access is required to invoke the chain: unauthenticated remote, authenticated remote, local interactive, local code execution, same account, another account, sandboxed process, administrator, or physical access. State the final principal and effective rights in the same vocabulary. Ordinary code execution under the caller's existing identity is not privilege escalation.

Do not infer local scope merely because the final vulnerable API is local when a remotely reachable service forwards attacker-controlled input to it. Conversely, a remotely delivered input that yields code execution only in the already compromised client is not automatically remote escalation.

## Constructed authority chain

```text
standard user -> writable request field -> privileged service operation -> protected file replaced -> service restart -> code executes as service account
```

This chain is complete only if the user can reach the service, control the field after parsing, bypass or encounter missing operation/object authorization, replace the selected protected file, cause or await loading, and gain the service account's rights. A writable file or service restart alone leaves essential links unresolved.

## Impact limits and primary sources

Report the exact new rights, namespace, session, integrity/label context, token or credential, duration, and affected objects. Administrator/root user mode, kernel mode, hypervisor/host, firmware, and secure world are distinct authority scopes rather than interchangeable labels.

Reviewed 2026-10-09 against NIST [SP 800-53 access-control concepts](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), Linux kernel [credentials documentation](https://www.kernel.org/doc/html/latest/security/credentials.html), Microsoft [access tokens](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-tokens), and MITRE [CWE-269](https://cwe.mitre.org/data/definitions/269.html) as taxonomy. Platform-specific references define how each effective authority is computed.
