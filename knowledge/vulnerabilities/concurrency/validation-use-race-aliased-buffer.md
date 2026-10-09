---
id: vulnerability-concurrency-validation-use-race-aliased-buffer
title: Validation/use race on an aliased buffer or nested pointer
kind: vulnerability
topics: [concurrency, validation, aliasing, shared-memory, nested-pointers]
platforms: [cross-platform]
architectures: [any]
---

# Validation/use race on an aliased buffer or nested pointer

## Definition and violated invariant

A validation/use race occurs when code validates bytes, object state, or a referenced payload and later consumes an alias that can change independently before or during the operation. The consumed bytes and referenced objects must remain the validated snapshot for every property on which the operation relies.

This profile differs from a simple double fetch of one scalar: the stale relationship can involve a validated buffer whose contents later change, a copied header whose pointer still names shared storage, or two aliases to the same mutable object.

## Conditions that establish the issue

Recover the validated byte ranges and semantic properties, every alias and nested pointer, the later reads, writers able to mutate or remap the storage, synchronization or pinning, and the final consumer. Prove a feasible mutation produces bytes or an object not covered by the original validation and reaches a security-relevant effect.

Validation of pointer value, mapping, length and content are separate. Pinning pages can stabilize mapping or physical backing under a specific API while leaving contents writable; copying a pointer does not copy its pointee.

## Evidence that is not sufficient

A pointer passed to both validator and consumer, a callback between them, shared memory, or a copied header is not sufficient. The storage may be immutable for the interval, the callback may not reach a writer, the consumer may use a private copy, or it may repeat the necessary checks.

A changed byte after validation is irrelevant unless that byte affects a property the consumer trusts.

## Investigation sequence

Build an alias map from the original boundary through copied headers, slices, views and nested objects. Mark which ranges each check establishes and which ranges each later operation reads. Identify mutation and remapping capabilities for the exact interval, including callbacks, other threads, processes, guests and devices.

Construct a schedule that changes one validated property while preserving reachability to the consumer, then follow the changed bytes through parsing, dispatch, memory access or authority selection. Account for any copy-on-use, locks, reference acquisition, page pinning or version retry.

## Constructed shared-buffer example

```c
uint8_t *payload = request->payload;
size_t length = request->length;
if (!validate_command(payload, length))
    return;
notify_observer(request);
dispatch_command(payload[0], payload + 1, length - 1);
```

Constructed schedule: `validate_command` accepts a length of at least one, opcode 1 and its operands; `notify_observer` invokes code able to modify the shared payload through another alias; the outer function then reloads bytes from the same storage and dispatches opcode 7 without revalidation. The finding requires actual aliasing and mutation reachability; a private immutable payload copy or a callback unable to access it refutes this schedule.

## Primitive and impact limits

The direct result is consumption of unvalidated bytes or object state. Consequences can include parser confusion, unauthorized operation selection, out-of-bounds access, stale-object use, or device/guest boundary violation, depending on the changed property.

## Related knowledge and primary sources

`reference-concurrency-mutable-validation-double-fetch`, `reference-native-ownership-release-dangling`, and boundary-specific buffer references cover snapshot and lifetime contracts. This profile repeats alias, byte-range, writer, and consumer binding locally.

Reviewed 2026-10-09 against Microsoft [ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread), Linux kernel [user-space memory access](https://docs.kernel.org/core-api/mm-api.html#user-space-memory-access), and the C++ [data-race rules](https://eel.is/c++draft/intro.races). The source and schedule are constructed.
