---
id: vulnerability-authorization-excessive-capability-transfer
title: Descriptor, handle, or capability transfer grants excessive or unintended rights
kind: vulnerability
topics: [authorization, capabilities, handles, file-descriptors, delegation, ipc]
platforms: [cross-platform]
architectures: [any]
---

# Descriptor, handle, or capability transfer grants excessive or unintended rights

## Definition and violated invariant

A capability-transfer vulnerability occurs when a process delegates an object reference to a recipient that is not authorized for the object, operation or granted rights, or when intended attenuation fails and the transferred reference preserves broader authority. A descriptor or handle can convey authority without re-resolving the object's pathname or repeating its original open check.

Handle and descriptor integers are process-relative. Transfer concerns the underlying object reference, grant and recipient, not equality of numeric values across processes.

## Conditions that establish the issue

Recover the initiating sender and authenticated recipient, transfer mechanism, source object identity and generation, source grant, requested attenuation and flags, receiver-side reference and rights, message association, recipient process and namespace, lifetime, downstream checks and exercised operation. Prove an unintended recipient obtains or uses authority beyond the delegation policy.

Include inheritance and child launch, broker duplication, Unix ancillary data and capability tokens. Determine whether the object type permits the requested rights and whether transfer succeeded.

## Evidence that is not sufficient

A handle value in IPC, `SCM_RIGHTS`, `DuplicateHandle`, inheritable flag, broad source handle, received descriptor or missing close is not sufficient. The transfer may fail, reach the intended trusted recipient, preserve only permitted rights, or refer to a harmless object; a raw integer may transfer no object at all.

Closing the sender's reference does not revoke a separately transferred reference. Conversely, a receiver-side descriptor number cannot be interpreted using the sender's descriptor table.

## Investigation sequence

Draw source reference, transfer call or ancillary message, receiver reference and eventual operation. Record object type, granted access or open mode, flags affecting attenuation, both process identities and message framing. Follow process creation restrictions and error/truncation paths to learn the actual set delivered. Compare the receiver's ordinary authority with the transferred capability.

At binary level, trace source and target process handles, desired-access masks, duplication flags, ancillary counts and receiver ownership. Decode rights by object type before naming impact.

## Hypothetical failed-attenuation example

```text
broker source handle: READ | WRITE
request intended grant: READ
duplicate_to_client(source, desired=READ, flags=SAME_ACCESS)
```

For an API where `SAME_ACCESS` preserves the source grant and ignores the requested mask, the client can receive `READ | WRITE`. The finding requires successful delivery to an unauthorized client and a meaningful object; it does not imply rights can be amplified beyond the source handle.

## Primitive and impact limits

The direct primitive is possession of an object capability with unintended rights. Impact is bounded by that object's operations and remaining checks. Escalation or escape requires the capability to cross an authority boundary and grant a host or privileged effect unavailable to the recipient otherwise.

## Related knowledge and primary sources

Windows handle-transfer and Linux descriptor/Unix-socket references provide concrete ownership and grant semantics. Platform brokers and process-creation references cover recipient selection.

Reviewed 2026-10-09 against Microsoft [`DuplicateHandle`](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle) for process-relative duplication and `DUPLICATE_SAME_ACCESS`, and Linux [`unix(7)`](https://man7.org/linux/man-pages/man7/unix.7.html) for `SCM_RIGHTS` transfer of open-file-description references. The example is hypothetical and mechanism-specific.
