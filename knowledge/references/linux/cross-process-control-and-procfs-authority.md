---
id: reference-linux-cross-process-control-procfs-authority
title: Linux ptrace, process memory and procfs cross-process authority
kind: reference
topics: [linux, ptrace, procfs, process-vm, credentials, namespaces, lsm]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# Linux cross-process control and procfs authority

## Cross-process access uses a selected ptrace access-mode check

Linux gates many process-inspection operations through ptrace access-mode checks that consider credential mode, same-thread-group cases, dumpability, capabilities in the target's user namespace, and LSM policy. Different operations request read versus attach strength and filesystem versus real-credential modes. A matching numeric UID or a visible `/proc` entry is not a complete authorization result.

For investigation, identify caller and target tasks, their user namespaces, selected credentials, target dumpable state, capability relation, LSM/Yama policy and the exact operation's access mode. Do not generalize one successful metadata read to memory write, register control, or signal authority.

## ptrace attachment and operation are separate gates

`ptrace` relationships and requests have request-specific state and effects. Attachment/seizure, stop state, register/memory operations and continuation are distinct events. Prove the caller establishes the required tracing relationship and that the selected request succeeds against the intended target generation.

A `ptrace` import, anti-debug check or process ID does not establish cross-process control. PID reuse and PID namespaces require binding the observed identifier to the same task throughout the evidence chain.

## process_vm and procfs expose scoped process objects

`process_vm_readv` and `process_vm_writev` transfer between local and remote iovec ranges and are governed by ptrace access checks; partial transfers are possible. `/proc/pid/mem` and other procfs objects have their own open/read semantics and access checks. A procfs mount can also be restricted or namespaced, changing visibility without changing every underlying task relationship.

Track local and remote extents, partial progress, target lifetime and object opened. Reading maps, status or a descriptor link does not prove permission to open memory, duplicate a descriptor, or control execution.

## Primary sources and scope

Reviewed 2026-10-09 against Linux man-pages [`ptrace(2)` access-mode algorithm](https://man7.org/linux/man-pages/man2/ptrace.2.html), [`process_vm_readv(2)` and `process_vm_writev(2)`](https://man7.org/linux/man-pages/man2/process_vm_readv.2.html), [`proc_pid_mem(5)`](https://man7.org/linux/man-pages/man5/proc_pid_mem.5.html), and kernel [Yama documentation](https://docs.kernel.org/admin-guide/LSM/Yama.html). Apply the target kernel configuration, LSM stack and namespace relationships.
