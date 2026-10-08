---
id: playbook-re-windows-handle-child-authority
title: Trace authority transferred through Windows handles and child creation
kind: playbook
topics: [windows, handles, process-creation, inheritance, authorization, evidence]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Investigate a Windows authority transfer
Use this workflow when a binary opens, passes or inherits handles, or creates
a child process across an intended authorization boundary. Preserve separate
evidence for acquired authority, recipient identity and the operation performed.

## Build a per-process handle ledger
Reviewed 2026-10-02. Use authorized evidence without modifying production token,
ACL or handle state. For each relevant acquisition record call coordinates,
source/target process, effective identity, object type/identity, requested and
granted rights, status, owner and aliases. Follow the handle through storage,
IPC, duplication, inheritance, use and close. Keep PID, raw handle value and
kernel object identity distinct.

For broker transfer, establish how the recipient process is bound to the
authenticated request. A client-supplied PID or numeric handle does not by
itself supply that binding. Find the exact sensitive operation the recipient
could perform, not merely a broadly named access flag. Facts:
reference-windows-handle-authority-transfer and
reference-windows-access-check-rights-integrity.

## Reconstruct the complete child launch input
Identify the final API after wrappers; recover token type/source, creation and
logon flags, executable parameter, full command line, environment, working
directory, desktop/session and startup attributes. Decode the handle list and
any alternate parent, not just bInheritHandles. Check attribute-construction
results and whether the final call actually uses the constructed list.

Test the intended invariant against the path: correct principal, correct image,
correct parsed arguments, only intended authority transferred, and meaningful
child outcome. Each can fail independently. Trace caller-controlled inputs into
these fields and identify the checks that bind them to the authorized request.
Facts: reference-windows-process-creation-context and
reference-windows-tokens-sids-groups-impersonation.

## Preserve failure and concurrency evidence before claiming a defect
Trace failed acquisition, duplicate-with-close, failed launch, suspended child,
late child failure and every ownership-transfer branch. Identify other threads
changing inheritability or launching with broad inheritance during the same
interval. A handle list on one path does not establish coverage of another.

Constructed candidate: a privileged file handle reaches a child intended only
to read an IPC stream. Establish the actual inherited/duplicated grant, the
child's ability to use it and the violated policy. Merely finding inheritance
enabled is not a confirmed vulnerability. Likewise, parent cleanup is not proof
that transferred authority disappeared. Report observed results, API-based
inferences and missing runtime evidence separately; a set model cannot reproduce
all Windows launch/security behavior.

## Follow transferred authority to behavior, not just a process-tree label

For suspected malware, trace the selected child image, parsed arguments, effective
identity and transferred resources to the operation they enable. Process creation
or duplication alone establishes neither malicious intent nor completed execution.
An alternate parent can change reported ancestry without identifying the creating
caller; recover the actual creation path before assigning origin or responsibility.

Constructed distinction: a child receives a readable file handle. That supports
an access-capability inference, not proof it read or transmitted the contents.
Follow uses, result handling, destination and observable effects; keep failed,
suspended and terminated launches separate. A permitted grant can support harmful
behavior without a defect in the handle-transfer mechanism itself.

## Source basis
Reviewed 2026-10-02. Workflow synthesis, not a target reproduction.

- [DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle): ownership context and exceptional close side effect.
- [Process inheritance](https://learn.microsoft.com/en-us/windows/win32/procthread/inheritance): transferred objects and grants.
- [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute): per-child attributes.
