---
id: reference-linux-seccomp-lsm-mediation
title: Linux seccomp filters, security-module policy and mediation limits
kind: reference
topics: [linux, seccomp, lsm, apparmor, policy, mediation, sandbox, observation-limits]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# System-call and object-policy evidence

## A seccomp filter sees syscall metadata, not pointed-to content

Linux seccomp uses Berkeley Packet Filter (BPF) programs to evaluate system-call
numbers, architecture and argument values. They cannot dereference user pointers.
The kernel guide explicitly distinguishes syscall filtering from a complete
sandbox. [1]

For investigation, bind filter, instruction ABI, actual syscall and selected
action. A rule allowing an open-like call does not authorize every pathname;
its pointer value is not the string contents. Conversely, a name in a filter
source is not proof the effective filter enforced that rule. Object checks,
mutable request data and application authorization require their own evidence.

## Filter actions and thread coverage matter as much as filter presence

Linux seccomp supports different actions, including logging without rejecting
the syscall. Its thread-synchronization mechanism has an explicit success/failure
contract. [1][2]

Investigate installed filters, relevant thread, support, installation result and
the action chosen for the operation. A log event need not establish denial; a
filter installed on one thread does not alone establish all-thread coverage.
Filter layering, notifications and supervision need the actual supported interface.
Preserve failure and fallback paths. No default filter policy or universal action
availability is assumed, and filter presence is not a verdict about the program.

## LSM policy adds resource checks beyond discretionary ownership

Linux Security Modules (LSMs) provide a framework for additional security checks.
AppArmor documents task profiles and the need for loaded policy to enforce its
restrictions beyond ordinary discretionary access control, the ownership/mode
permission model. [3][4]

For investigation, identify active policy mechanism, subject profile/label, target
resource and operation at the actual check. A compiled-in module, policy file or
product label is not proof of effective enforcement. UID zero or permissive file
mode does not settle a separate policy check. A denial log also needs the request
and enforcement context before it explains an observed failure. Specific LSM
hooks, stacking order and defaults require the target's applicable contract.

## A brokered operation has both client and broker authority boundaries

For analysis, when filtering or policy delegates a decision, track authenticated
caller, copied request representation, selected resource, decision and the broker's
actual operation. An allowed syscall or supervisor reply is not proof of a final
effect under the intended caller's authorization.

Mutable inputs can change between observation and use; use
reference-logic-authorization-object-binding and
reference-linux-kernel-interface-representations. Identify whether a policy check
applies to the client or broker, and whether the broker binds the checked object
to the consumed object. This is investigative guidance, not a claim that every
seccomp or LSM deployment contains such a broker.

## Sources and scope

Reviewed 2026-10-08. Upstream Linux docs and man-pages 6.19. Only framework,
filter-visibility and named action/synchronization distinctions are adopted;
older guides' setup defaults and private hook APIs are not generalized.

1. [Seccomp BPF guide](https://docs.kernel.org/userspace-api/seccomp_filter.html): visible arguments, no pointer dereference, filtering versus sandbox and actions.
2. [seccomp(2)](https://man7.org/linux/man-pages/man2/seccomp.2.html): thread synchronization and installed-filter scope.
3. [LSM usage](https://docs.kernel.org/admin-guide/LSM/index.html): additional security-check framework; no universal stacking order adopted.
4. [AppArmor guide](https://docs.kernel.org/admin-guide/LSM/apparmor.html): profiles and loaded-policy requirement.

Workflow: playbook-linux-authority-boundary.
