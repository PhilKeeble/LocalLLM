---
id: reference-container-host-authority-escape-evidence
title: Container namespace, delegated host capability and escape evidence
kind: reference
topics: [containers, namespaces, capabilities, mounts, devices, management-api, escape]
platforms: [linux, windows, cross-platform]
architectures: [any]
---

# Container and host authority evidence

## Container root and capabilities need their governing namespace

The numeric UID/root label and capability sets visible inside a container must be interpreted through the user namespace and ID mappings governing the protected resource. UID 0 in a child user namespace can have broad authority over resources owned by that namespace while lacking corresponding authority in the initial namespace. Conversely, a workload sharing the host user namespace can expose a different boundary.

Record process credentials, capability sets, user namespace, ID mappings, target resource and its governing namespace. A manifest declaration is intended configuration; bind it to the running process and operation.

## Management sockets and APIs can delegate host operations

A container runtime, orchestration or daemon endpoint can act as a privileged deputy by creating workloads, mounting host paths, attaching devices, changing namespaces or executing in other containers. Exposure becomes an escape path only when the workload can reach the endpoint, authenticate or bypass authorization, request a host-impacting operation and obtain authority outside its intended policy.

A socket path, environment variable or client binary is insufficient. Recover endpoint permissions, peer identity, protocol, authorization plugins/policy, request and resulting host object or process.

## Mounts, devices, credentials and inherited descriptors are direct capabilities

Bind mounts, injected secrets, device nodes, shared memory and inherited descriptors expose particular host objects with particular operations. Their authority does not follow solely from container filesystem modes or process UID. Identify host backing object, mount propagation and flags, descriptor provenance and access mode, device/IOMMU policy, credential scope and lifetime.

An intentional read-only configuration mount is not automatically an escape, though it may disclose data outside policy. Writable host executables, control sockets or sensitive device operations require the actual selection and activation chain.

## Isolation layers must be recovered independently

User, mount, PID, network, IPC and time namespaces isolate different views. Cgroups account and limit resources; seccomp constrains syscall metadata; LSM or host security policy mediates operations; none alone proves a complete container boundary. Shared namespaces or host networking can be intentional and must be assessed against the stated policy.

Record each effective namespace, cgroup, syscall filter, capability, LSM label/profile, filesystem/device exposure and broker. A container label or image hash does not establish this runtime state.

## Cross-container and cross-tenant reuse needs identity reset

Shared volumes, networks, caches, object pools, credentials and control-plane identifiers can cross boundaries without a nominal host escape. Prove that state created for one principal remains observable or actionable by another because identity, ownership, namespace or lifecycle reset is missing. Shared infrastructure alone is not a vulnerability when policy intentionally permits the same object population.

Bind each object generation to tenant/workload identity, cleanup event and later consumer. Numeric container IDs, IP addresses and names can be reused and are not durable identity by themselves.

## Escape conclusion requires out-of-boundary authority

Call a result a container escape only when a reachable host capability or host defect yields an operation, object, identity or execution context outside the initiating workload's isolation policy. A crash, host kernel syscall, visible host metadata or UID 0 inside the container does not establish that conclusion.

Report the initial boundary, enabling capability/defect, final host or peer context and exact gained rights. Kernel code execution, host user-mode execution and access to one mounted host object are different impacts.

## Primary sources and scope

Reviewed 2026-10-09 against the OCI [runtime configuration specification](https://github.com/opencontainers/runtime-spec/blob/main/config.md) for namespaces, mounts, devices, process capabilities and security attributes; Linux man-pages [namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html), [user namespaces](https://man7.org/linux/man-pages/man7/user_namespaces.7.html), and [capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html); kernel [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) and [seccomp](https://docs.kernel.org/userspace-api/seccomp_filter.html); and Docker's [daemon attack-surface discussion](https://docs.docker.com/engine/security/#docker-daemon-attack-surface) as one product example. Runtime and orchestration policy remain target-specific.
