---
id: reference-linux-privilege-drop-exec
title: Linux privilege dropping, set-ID execution and no_new_privs limits
kind: reference
topics: [linux, setuid, setgid, privilege-dropping, exec, no-new-privileges, environment]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Privilege transitions and retained execution context

## Set-ID file modes describe a possible exec transition

On Linux execve, executable set-user-ID/set-group-ID modes can change effective
IDs to file owner/group. The documented transitions and file capabilities are
suppressed under no_new_privs, a nosuid mount or tracing conditions described by
execve. Real IDs and supplementary groups are preserved. [1]

Investigate the actual selected file, mount, caller state and successful execution.
A mode bit on a disk artifact does not establish a privileged process. Preserve
effective and saved IDs after exec, and separate privilege acquisition from
behavior performed with that authority. An interpreter or launcher also requires
its own selection contract; do not generalize executable-file rules to arbitrary
scripts or substitute a later file at the same path.

## A UID change needs its result and saved/group authority

Linux setuid with appropriate CAP_SETUID authority also changes real and saved
UIDs; without it, permitted transitions are restricted. setuid can fail even for
UID zero. Supplementary-group changes use a separate interface and permission
check. [2][3]

For investigation, retain requested identity, prior authority, actual result and
post-call state. An unchecked return or a changed effective UID alone does not
establish complete, irreversible privilege removal. Review saved IDs, groups,
filesystem IDs and capabilities under their own contracts. A program's stated
'drop privileges' purpose cannot replace that evidence. API-specific restoration
possibilities must be supported, rather than inferred from one credential field.

## no_new_privs constrains exec gains, not every authority channel

Linux no_new_privs is inherited across fork/clone and exec and cannot be unset
once set. It prevents exec from granting new privilege under its contract. It
does not prevent all non-exec privilege changes or receipt of SCM_RIGHTS. [4][5]

Investigate the setting on the relevant task and its effect on the selected
execution transition. Existing capabilities, descriptors and delegated service
operations need separate analysis. Presence of this flag is not a complete
confinement or harmlessness claim. Absence is not proof that privilege was gained;
the file, mount, credentials and actual transition must still support that result.

## Executing a helper carries operands and state, not merely a filename

Linux execve supplies an argument vector and environment to the new program. [1]
For analysis, bind selected program identity to arguments, working directory,
environment, retained descriptors and the caller's execution authority.

A trusted helper can process untrusted operands. A sanitized loader environment
does not establish that application-specific configuration or commands are safe.
Conversely, an environment string is only a lead until the consumer uses it.
Follow the sensitive operation and its object authorization without assuming
shell interpretation or PATH lookup for every exec interface. Loader-specific
selection is in reference-linux-loader-selection-context.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19 and upstream kernel no_new_privs
documentation. Stable transition concepts; no prescribed privilege-drop sequence,
target execution, private layout or universal Unix semantics.

1. [execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html): set-ID suppression, preserved IDs/groups and supplied arguments/environment.
2. [setuid(2)](https://man7.org/linux/man-pages/man2/setuid.2.html): authority-dependent ID changes and failure.
3. [getgroups/setgroups](https://man7.org/linux/man-pages/man2/setgroups.2.html): independent supplementary-group state and permission.

## Sources: exec restriction scope

Reviewed 2026-10-08. The following sources describe the flag, not the complete
security policy of a service or container.

4. [PR_SET_NO_NEW_PRIVS](https://man7.org/linux/man-pages/man2/PR_SET_NO_NEW_PRIVS.2const.html): irreversible setting and inheritance.
5. [Kernel no_new_privs guide](https://docs.kernel.org/userspace-api/no_new_privs.html): exec-only privilege-gain limit and non-exec channels.

Workflow: playbook-linux-authority-boundary. Related credential/set meanings:
reference-linux-credentials-id-transitions and reference-linux-capability-exec-evidence.
