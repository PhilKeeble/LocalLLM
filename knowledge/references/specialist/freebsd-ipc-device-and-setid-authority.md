---
id: reference-freebsd-ipc-device-setid-authority
title: FreeBSD local IPC, device/sysctl exposure and set-ID transitions
kind: reference
topics: [freebsd, unix-sockets, descriptors, ioctl, sysctl, devfs, setuid, privilege-drop]
platforms: [freebsd]
architectures: [x86, x64, arm, arm64, riscv64, powerpc]
---

# FreeBSD IPC, device and credential-transition authority

## Unix-socket peer identity and descriptor transfer are separate evidence

FreeBSD `getpeereid` returns the effective credentials of the peer connected to a local-domain socket. Local credential control messages and passed descriptors have separate socket-option/message contracts. A pathname owner, caller-supplied UID or sender's descriptor integer is not a substitute for the kernel-associated peer or transferred object.

For each request, bind socket generation, peer credential observation, message framing and selected operation. For descriptor transfer, identify the received descriptor's object, access mode and operation-specific capability rights; transfer gives a reference to an open object, not the sender's process-relative number or every possible right.

## Device node, devfs and ioctl policy combine at the operation

FreeBSD device reachability depends on the visible devfs namespace/rules, node permissions, open mode, jail policy and the driver's request handling. IOCTL direction/size encoding describes argument transfer shape but does not authorize the semantic operation or validate nested pointers.

Recover the actual device object and generation, caller credential/jail, effective devfs rule and permissions, command ABI and compatibility mode, copied structure, handler and privileged effect. A device node or request number alone does not prove a lower-authority actor can perform it.

## sysctl names expose heterogeneous kernel operations

FreeBSD `sysctl` accesses a management-information tree whose nodes can be read-only, writable or handler-backed. A discovered name or numeric MIB does not establish write permission, jail visibility, accepted input representation or effect. Recover the exact node, old/new buffers and lengths, caller context, handler and returned status.

Do not treat every sysctl as stored scalar state; handlers can compute data or perform operations and can have subsystem-specific locking and lifetime rules.

## Set-ID execution and privilege dropping require complete credential state

Set-user-ID/set-group-ID execution and credential APIs can change real, effective and saved IDs under documented conditions. A privilege drop must include call success, effective and saved identities, supplementary groups, jail/Capsicum context, retained descriptors and capabilities, loader/environment state, and later execution. One successful `setuid`-family call does not universally prove irreversibility or complete removal of inherited authority.

Apply the exact target APIs and caller privilege. Different set-ID functions intentionally have different effects; do not import Linux saved-ID behavior or infer the result from a decompiler's generic name.

## Primary sources and scope

Reviewed 2026-10-09 against FreeBSD [`getpeereid(3)`](https://man.freebsd.org/cgi/man.cgi?query=getpeereid&sektion=3), [`unix(4)`](https://man.freebsd.org/cgi/man.cgi?query=unix&sektion=4), [`devfs(8)`](https://man.freebsd.org/cgi/man.cgi?query=devfs&sektion=8), [`ioctl(2)`](https://man.freebsd.org/cgi/man.cgi?query=ioctl&sektion=2), [`sysctl(3)`](https://man.freebsd.org/cgi/man.cgi?query=sysctl&sektion=3), [`execve(2)`](https://man.freebsd.org/cgi/man.cgi?query=execve&sektion=2), and [`setuid(2)`](https://man.freebsd.org/cgi/man.cgi?query=setuid&sektion=2). Match the target release and jail/security configuration.
