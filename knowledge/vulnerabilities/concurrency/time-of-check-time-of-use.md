---
id: vulnerability-concurrency-time-of-check-time-of-use
title: Time-of-check/time-of-use race on files, names, permissions, or objects
kind: vulnerability
topics: [concurrency, toctou, filesystem, authorization, object-identity]
platforms: [cross-platform]
architectures: [any]
---

# Time-of-check/time-of-use race on files, names, permissions, or objects

## Definition and violated invariant

A time-of-check/time-of-use vulnerability occurs when a security decision is made about one object, identity, authority state, or generation, but the later operation re-resolves or consumes state that can change independently. The checked subject, object and attributes must remain bound to the operation for the policy's required interval.

Elapsed time alone is not the issue. A delayed use is safe with an immutable object, retained object identity, suitable transaction, or protocol that excludes relevant changes.

## Conditions that establish the issue

Identify the exact check, the object and credentials it observes, the later name resolution or object lookup, mutable namespaces or fields between them, attacker ability to perform the change, and the resulting operation. Prove the check and use can bind to different objects or authority states and that policy requires the checked state at use or commit time.

For files, include every path component, links, mounts, directory control, relative-path base, final open mode, retained descriptor, and credentials used by each operation. For non-file objects, include generation, owner, revocation and lookup keys.

## Evidence that is not sufficient

Separate check and use calls, pathname input, symbolic-link support, a mutable object, or a long interval is not sufficient. The namespace may be inaccessible to the attacker, resolution may be constrained, the operation may use a descriptor for the checked object, or policy may intentionally grant authority at an earlier point.

String equality does not establish object identity, while a different pathname does not prove a different object. Use stable object or generation evidence where available.

## Investigation sequence

Trace authority from the checking credentials through the checked object and attributes, then trace the operation independently through its credentials and object resolution. Mark every mutable component and the actor able to change it. Construct an interleaving only from operations the platform permits.

After the object is opened or retained, distinguish name replacement from later content, permission, owner, or mount changes. State the policy's intended authorization point instead of assuming every change invalidates an earlier grant.

## Constructed privileged file example

```c
if (access(path, W_OK) == 0)
    fd = open(path, O_WRONLY | O_TRUNC);
```

Constructed schedule: the check resolves `path` to file A using the invoking user's identity; an attacker replaces a writable path component or link; the privileged `open` resolves the same text to file B and truncates it under different effective authority. On Linux, `access` and `open` also use different credential semantics in the documented cases. The finding requires attacker control over the relevant resolution component and a reachable privileged effect on B.

## Primitive and impact limits

The direct primitive is substitution of the object or state consumed after validation. Consequences can include unauthorized read, write, deletion, execution, ownership change, or policy bypass; impact is bounded by the use operation's actual authority.

## Related knowledge and primary sources

`reference-concurrency-mutable-validation-double-fetch` and filesystem resolution references cover stable object binding and platform-specific lookup. This profile repeats the authority, namespace, and object-identity proof locally.

Reviewed 2026-10-09 against Linux [access(2)](https://man7.org/linux/man-pages/man2/access.2.html), [openat2(2)](https://man7.org/linux/man-pages/man2/openat2.2.html), and [path resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html). The source and schedule are constructed; other operating systems require their own namespace and handle contracts.
