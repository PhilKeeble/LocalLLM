---
id: reference-freebsd-authority-interface-evidence
title: FreeBSD credential context, Capsicum, jails and kernel request interfaces
kind: reference
topics: [freebsd, credentials, capsicum, jails, ioctl, syscalls, authority]
platforms: [freebsd]
architectures: [x86, x64, arm, arm64, riscv64, powerpc]
---
# FreeBSD authority and interface evidence

## Credential identity and jail context are separate authority evidence

FreeBSD's architecture handbook describes jail association through credentials
and a prison object. Jails share the host kernel; their restrictions and allowed
operations depend on configured policy. [1][2]

Recover caller identity, jail context, object and selected policy at the actual
decision. A UID displayed as root inside a jail does not prove host-root authority.
A shared kernel does not mean every resource is shared without restriction.
The handbook's structure names illustrate the relationship, not portable field
offsets or complete current credential lifetime rules. Other BSD systems require
their own jail/sandbox and credential contracts.

## A credential retained for later work has its own lifetime and policy context

FreeBSD's documented ucred interfaces use crhold to retain a credential reference
and crfree to release it, with final release reclaiming credential storage. [6]

Recover the credential selected for an access-control decision and what retains
it across later work. A captured numeric UID is not the complete credential or
object authority. Retaining a credential keeps that object alive; it does not
prove later policy or resource state stayed unchanged. Match the target's actual
credential acquisition/release contract before interpreting calls, rather than
applying Linux credential APIs or private structure offsets.

## Capsicum capability mode restricts global namespace access

FreeBSD cap_enter places a process in capability mode: permitted operations use
descriptors or limited global state rather than unrestricted global namespaces.
Descendants inherit this mode. The manual warns that inherited memory/resources
and other rights still matter. [3]

Recover whether entry succeeded and which descriptors, shared memory and delegated
services remain available. Capability mode does not mean no I/O or no authority.
A request through a retained service can have its own policy and effect. A sandbox
API reference alone is not evidence the process entered the sandbox.

## Descriptor capability rights can be reduced, not expanded

FreeBSD cap_rights_limit reduces the rights associated with a descriptor; it cannot
add rights absent from that descriptor. Operations are constrained by the resulting
rights. [4]

Bind descriptor identity, rights at the operation, any transfer and the requested
action. Possessing a descriptor does not imply every ioctl or write is permitted.
Rights, caller/jail policy and service-side authorization are separate gates.
These object-associated Capsicum rights are not Linux's process capability sets;
do not apply Linux capability names or exec transitions to them.

## FreeBSD ioctl and syscall evidence needs the actual user ABI

FreeBSD's ioctl manual describes request encoding for input/output direction and
argument byte size. [5] Those fields help identify a command; they do not validate
every nested pointer or the handler's semantic interpretation.

Recover object, command, user ABI, copied layout and selected handler. Do not
reuse Linux request numbers, structures or error conventions because the CPU is
the same. abi-darwin-freebsd-service-evidence supplies separately scoped native
AMD64 entry/return evidence; it does not establish all BSD or compatibility ABIs.
Workflow: playbook-specialist-kernel-boundary.

## Sources: credential context and jail scope

Reviewed 2026-10-08. Rolling FreeBSD manuals; architecture examples are historical
explanations, not private layout guarantees. No default permissions are imported.

1. [Jail architecture](https://docs.freebsd.org/en/books/arch-handbook/jail/): section 4.1 credential/prison association.
2. [Handbook jails](https://docs.freebsd.org/en/books/handbook/jails/): shared-kernel model and configured permissions.

## Sources: Capsicum and request contracts

Reviewed 2026-10-08. The publisher's default manual snapshot displayed FreeBSD
15.1; that label is provenance, not a target release requirement.

3. [cap_enter(2)](https://man.freebsd.org/cgi/man.cgi?query=cap_enter&sektion=2): Description, results and Caveats.
4. [cap_rights_limit(2)](https://man.freebsd.org/cgi/man.cgi?query=cap_rights_limit&sektion=2): Description and rights reduction.
5. [ioctl(2)](https://man.freebsd.org/cgi/man.cgi?query=ioctl&sektion=2): argument and request encoding.
6. [ucred(9)](https://man.freebsd.org/cgi/man.cgi?manpath=FreeBSD+10.3-RELEASE&query=crfree&sektion=9): Description, credential retention/release concepts only. This available historical manual does not establish a current private layout, every acquisition path or unchanged implementation.
