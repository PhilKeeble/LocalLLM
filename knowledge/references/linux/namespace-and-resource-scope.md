---
id: reference-linux-namespace-resource-scope
title: Linux namespace views, user-ID mappings and resource authority
kind: reference
topics: [linux, namespaces, containers, user-namespaces, mount-namespaces, network-namespaces, authority]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Namespace membership and resource authority

## Different namespace types isolate different resource views

Linux namespaces separate classes of resources rather than supplying one indivisible
container boundary. Mount namespaces concern mount views; network namespaces
concern networking resources; user namespaces concern identities and capabilities.
The namespace API identifies these as distinct memberships. [1]

For investigation, bind the operation to the relevant namespace objects and process
generation. A container name, image manifest or one namespace difference cannot
establish every membership or access boundary. Processes can share some namespaces
and differ in others. Preserve what was actually captured; missing host visibility
is not proof that a resource was absent or inaccessible to the target.

## User-namespace root is not automatically authority in an ancestor

Linux user namespaces map IDs to other namespace contexts. Capabilities held in a
user namespace apply to resources governed by that namespace and applicable
descendants, not automatically to resources governed by its ancestors. [2]

Investigate the caller's mapped credentials and the user namespace governing the
checked resource. The number zero or an effective capability bit alone leaves
that relation unresolved. Some operations concern resources governed by the
initial user namespace; they require that context's authority. Do not infer host
privilege merely from a child namespace's root status, or harmlessness merely
from using a child namespace.

## A mount view and an opened object need separate identities

For analysis, bind pathname selection to root, working directory and mount
namespace, then bind a returned descriptor to its actual object. Mount visibility
and existing-reference authority answer different questions.

Use reference-linux-path-resolution-identity and
reference-linux-descriptors-open-file-descriptions. A path absent from one view
does not prove a descriptor, shared mapping or broker cannot access the underlying
resource. Likewise, the same path text across two views need not identify the
same file. Claims about containment need the specific selection and access checks,
not a universal conclusion drawn from mount-namespace membership.

## Network visibility does not supply application authorization

Linux's namespace overview identifies networking resources as a separate
namespace domain. [1] A connection observation must retain its network context.

For investigation, bind endpoint address, listener, route/transport context and
process-associated operation. A host capture can omit traffic visible elsewhere;
the same address display can be ambiguous across namespace contexts. Reachability
does not grant permission for the requested application action. Shared brokers,
passed sockets and external forwarding require their own data/authority relations;
do not assume their presence or absence from a container label.

## Sources and scope

Reviewed 2026-10-08. Linux man-pages 6.19: namespace types and user-namespace
capability/mapping concepts. No container-product defaults, creation recipe,
supported-filesystem list or namespace-structure offsets.

1. [namespaces(7)](https://man7.org/linux/man-pages/man7/namespaces.7.html): distinct resource domains and membership.
2. [user_namespaces(7)](https://man7.org/linux/man-pages/man7/user_namespaces.7.html): mapped IDs and governing-resource authority.

Workflow: playbook-linux-authority-boundary. Policy checks beyond namespace
membership: reference-linux-seccomp-lsm-mediation.
