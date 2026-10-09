---
id: vulnerability-impact-privilege-and-isolation-scopes
title: Privilege and isolation impact scopes
kind: vulnerability
topics: [privilege-escalation, remote-code-execution, authorization, sandbox-escape, container-escape, virtualization, firmware, impact]
platforms: [cross-platform]
architectures: [any]
---

# Privilege and isolation impact scopes

## Unauthenticated remote actor to a service authority context

An unauthenticated remote impact is established when a network-reachable actor can reach the vulnerable operation without first presenting an accepted identity and the resulting sensitive operation or code execution occurs in a named service process and authority context. Recover the complete ingress path, parsing and dispatch state, authentication decision, worker boundary, process credentials or token, sandbox and delegated resources. A listening port, pre-authentication crash, or remote influence over data does not by itself establish code execution or a sensitive operation.

Report the direct result separately from later escalation. Execution in a restricted worker has that worker's authority unless a further defect or exposed capability crosses into a supervisor, host, kernel or other context. An authentication bypass belongs in the chain when the endpoint normally requires identity; it is not equivalent to an endpoint that is intentionally unauthenticated.

## Authenticated lower role to higher role, account or tenant

An authenticated privilege transition requires a valid lower-authority principal, a reachable authorization or object-binding failure, and an operation performed with authority reserved for another role, account or tenant. Bind the authenticated session to the caller identity, requested action, selected object, policy decision and final data or state change. A role label in a request, hidden UI control, or successful call is not proof until the effective policy and protected effect are recovered.

Distinguish vertical gain from horizontal access. Reaching an administrator-only operation is vertical escalation; reading or changing another ordinary user's object can be horizontal authorization failure even when both accounts have the same nominal role. Report the smallest demonstrated scope and do not infer tenant-wide control from access to one incorrectly bound object.

## Same-user sandbox, integrity or capability boundary escape

A process can gain authority without changing operating-system user when it crosses from a sandbox, low-integrity context, capability-restricted process or constrained application identity into a broker or peer that holds broader rights. Compare the initiating and destination contexts using effective token or credential properties, integrity or security labels, capabilities, namespaces, entitlements, accessible objects and delegated handles. The shared account name does not make those contexts equivalent.

Establish the broker entry point, caller identity evidence, per-operation authorization, selected object and resulting operation. Sending a message to a less-restricted process or causing it to crash is insufficient; the actor must cause an operation or acquire a resource that its original context could not perform or obtain.

## Local standard user to administrator, root, SYSTEM or service authority

Local privilege escalation is established when a standard local principal reaches a defect or misconfigured privileged component and gains a specific right held by an elevated administrator, root-equivalent credential, SYSTEM-like account or privileged service. Recover the starting credential, service or helper activation path, authorization and impersonation state, protected object, final execution identity and persistence or lifetime of the gained authority.

Do not collapse privileged labels into one result. Code execution as a narrowly restricted service account, an elevated interactive administrator, a root credential constrained by a namespace or policy, and a system service with powerful privileges can expose different resources. Report the actual effective rights and policy layers at the demonstrated operation.

## Container, jail or application sandbox to host or outside authority

An isolation escape requires an operation, object, identity or execution context outside the initiating container, jail or application sandbox policy. Establish the runtime boundary and its effective namespaces, identity mappings, capabilities, mounts, devices, descriptors, syscall filters and host policy, then connect a reachable host capability or host defect to the out-of-boundary effect. Root inside an isolated identity namespace, use of a host kernel syscall, or visibility of host metadata does not alone prove escape.

Name the exact result: access to one mounted host object, control of a runtime management endpoint, execution as a host user, host kernel execution, or access to another workload. These have different authority and blast radius. Shared storage or networking can instead be an intended policy choice or a horizontal isolation failure, so compare the effect with the declared and effective boundary.

## Administrator or root user mode to kernel authority

Kernel escalation is a transition from user-mode administrative authority to execution or operations available only in the kernel or an equivalent privileged execution domain. Establish a reachable kernel interface, violated invariant, direct primitive and final kernel-context effect, including the affected address space, credential, page tables, device control or code path. Administrative ability to configure the system or load an authorized driver may already grant broad policy authority, but it is not evidence that the investigated defect yielded arbitrary kernel execution.

State the security consequence that remains after accounting for the starting administrator's legitimate powers. Kernel code execution can bypass user-mode monitoring or policy, access kernel-only memory and affect resources across principals, while a constrained kernel read or denial of service supports a narrower result. Platform boot policy, driver-signing policy and virtualization-based isolation can further separate administrator, kernel and protected security contexts.

## Guest to hypervisor, host or another guest

A virtualization escape requires guest-controlled input to cross a virtual CPU, hypercall, device-emulation, shared-memory, management or paravirtual interface and produce an unauthorized effect in the hypervisor, host or a different guest. Recover the guest privilege needed to reach the interface, the selected virtual device or service, host-side parser and worker context, direct primitive, isolation controls and final authority. A VM exit, hypercall, shared page or host crash is only evidence of boundary interaction, not escape.

Report host execution, hypervisor execution, access to a delegated host object and cross-guest access separately. A management socket deliberately exposed to a guest can form a capability path without a hypervisor memory-safety defect; cross-guest access can be horizontal even when no host authority is gained. The chain must identify the actual destination context and affected resources.

## Kernel or OS to firmware, management mode or secure world

A firmware or higher-trust transition requires an OS or kernel actor to reach a defined firmware, management-mode or secure-world interface and gain an operation unavailable in the normal-world kernel context. Trace runtime-service calls, SMI/MM communication, secure monitor calls, device firmware protocols, variable stores or update paths through their validation and authorization to the protected state. Kernel control alone does not prove execution in SMM/MM, EL3, a trusted execution environment or device firmware.

Distinguish transient access to one service from arbitrary higher-trust execution, persistent boot modification and compromise of an update trust root. Establish the executing component, memory or storage domain, accepted image or command, authentication state, persistence across reset and any hardware write protection. Platform firmware layout and protection policy are target-specific, so an interface name or architectural capability cannot establish reachability or impact by itself.

## Cross-user or cross-tenant horizontal authority

Horizontal authorization failure occurs when one principal accesses another principal's protected data, action, object or delegated capability without a nominal role increase. Bind the caller's authenticated identity and tenant or user scope to every object identifier, secondary lookup, cached authorization decision and final consumer. Guessable identifiers, shared infrastructure or equal role names do not prove unauthorized access; demonstrate that policy assigns the selected object or operation to a different principal and that the check is absent, stale or applied to another object.

Report which objects and operations are exposed, whether identifiers are enumerable, whether writes or delegated actions are possible, and whether one success generalizes to a collection. Cross-tenant control-plane access may have broader consequences than a single-record disclosure, but tenant-wide or platform-wide impact needs its own evidence.

## Evidence ladder and primary sources

For every impact scope, record the starting actor and authority, reachable boundary, enabling root cause, direct primitive, destination context, exact gained operation or resource, duration and unresolved conditions. Stop at the strongest supported step: boundary reachability, defect, primitive, sensitive operation, execution in a named context, or demonstrated authority transition. Labels such as remote, administrator, root, kernel, host and firmware are conclusions about different contexts rather than interchangeable severity terms.

Reviewed 2026-10-09 against NIST [SP 800-53 access-control concepts](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), Microsoft [access tokens](https://learn.microsoft.com/windows/win32/secauthz/access-tokens) and [Mandatory Integrity Control](https://learn.microsoft.com/windows/win32/secauthz/mandatory-integrity-control), Linux kernel [credentials](https://www.kernel.org/doc/html/latest/security/credentials.html) and namespace documentation, the OCI [runtime configuration specification](https://github.com/opencontainers/runtime-spec/blob/main/config.md), Intel's [VMX system-programming specification](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html), Arm [EL3 runtime-service guidance](https://trustedfirmware-a.readthedocs.io/en/latest/getting_started/rt-svc-writers-guide.html), and the UEFI Forum [UEFI and PI specifications](https://uefi.org/specifications). Each source defines one authority boundary; the investigated target's effective configuration and code path determine the result.
