---
id: vulnerability-lifetime-handle-descriptor-reuse
title: Stale handle or descriptor reused for a different object
kind: vulnerability
topics: [lifetime, handles, file-descriptors, reuse, object-identity]
platforms: [cross-platform]
architectures: [any]
---

# Stale handle or descriptor reused for a different object

## Definition and violated invariant

A stale-identifier vulnerability occurs when code retains a handle, descriptor, slot, or numeric resource ID after its reference is closed or replaced, and later reuse makes the same value name a different object. Numeric equality does not preserve object identity across release, duplication, replacement, reconnect, or process boundaries.

The result differs from an invalid-handle failure: reuse can redirect an otherwise valid operation to an unintended file, socket, process, token, device, or IPC endpoint.

## Conditions that establish the issue

Identify resource-table context, acquisition generation, underlying object and rights, close or replacement, later allocation selecting the same numeric value, and stale consumer. Prove the consumer uses the old logical identity without a generation or ownership check and that the new object changes security-relevant behavior.

For duplicated references, closing one value does not destroy the underlying object while other references remain. Track descriptors or handles and underlying objects separately.

## Evidence that is not sufficient

A closed value, equal integer at two times, or later successful operation is not sufficient. Establish actual reuse in the same relevant table and the object selected by the consuming call. Another process using the same number does not prove shared identity.

A stale call that reliably fails before reuse supports a different availability or error-handling result.

## Investigation sequence

Create a generation ledger for open/create, duplicate or transfer, close, replacement, and every use. Correlate process or descriptor-table context, object type, rights, and timing. Inspect asynchronous tasks that store only the numeric value.

On Linux, account for `dup2` atomic replacement and the rule that retrying `close` after many reported errors can close a value already reused by another thread. Apply other platforms' close contracts independently.

## Constructed source example

```c
int saved = open_first_object();
close(saved);
int current = open_second_object();       /* may reuse saved's number */
write(saved, message, message_length);     /* can target second object */
```

The issue requires `current == saved`, successful opening of a different object, and the stale write path. The source shows feasibility rather than guaranteeing the allocator chooses that number; a trace or table transition must establish reuse for a concrete finding.

## Primitive and impact limits

The direct primitive is operation redirection to a replacement object with whatever rights the reused identifier carries. Consequences can include cross-request data exposure, unintended writes, authority confusion, or denial of service. Privilege impact requires the replacement object to confer greater effective authority.

## Related knowledge and primary sources

`reference-linux-descriptors-open-file-descriptions` and `reference-native-resource-lifetimes-results` distinguish numeric entries from underlying objects. This profile repeats generation and table-context requirements locally.

Reviewed 2026-10-09 against Linux [`open`](https://man7.org/linux/man-pages/man2/open.2.html), [`dup`](https://man7.org/linux/man-pages/man2/dup.2.html), and [`close`](https://man7.org/linux/man-pages/man2/close.2.html), Microsoft [`CloseHandle`](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle), and [MITRE CWE-672](https://cwe.mitre.org/data/definitions/672.html). The example is constructed.
