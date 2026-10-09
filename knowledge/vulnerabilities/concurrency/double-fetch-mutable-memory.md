---
id: vulnerability-concurrency-double-fetch-mutable-memory
title: Double fetch of mutable user, guest, shared, or device-controlled memory
kind: vulnerability
topics: [concurrency, double-fetch, shared-memory, drivers, validation]
platforms: [cross-platform]
architectures: [any]
---

# Double fetch of mutable user, guest, shared, or device-controlled memory

## Definition and violated invariant

A double-fetch vulnerability occurs when trusted code reads security-relevant data from mutable external memory for validation and later fetches the same logical field or related fields again for consumption without ensuring they belong to the validated snapshot. The values used for the operation must be the values whose bounds and semantics were checked.

The mutable source can be user memory, guest memory, a shared ring, mapped IPC, DMA-visible storage, or a device register. Two reads are not inherently unsafe if the second is revalidated or a protocol makes the source stable.

## Conditions that establish the issue

Identify both physical loads or API transfers, their addresses, widths and aliases, the validation derived from the first value, actors able to mutate the source, the feasible mutation interval, and the consumer of the later value. Prove the changed value escapes equivalent validation and violates a bound, type, state, ownership, or authorization invariant.

A private header copy helps only when validation and use consume that same copy. Nested pointers or payloads can remain externally mutable, and a non-atomic multi-field copy can capture a mixed state unless a coherent snapshot protocol exists.

## Evidence that is not sufficient

Repeated decompiler expressions, two source reads, a user pointer, or `ProbeForRead` is not sufficient. The compiler may emit one load, the memory may be captured by the OS, the producer may be unable to mutate it, or the second value may be checked again.

Atomicity of each field prevents tearing under its contract but does not make several fields one consistent request snapshot.

## Investigation sequence

Start from the machine loads or transfer helpers and map them to the same allocation and logical field. Locate every validation result and determine which exact loaded value it constrains. Identify the writer and show that its access can overlap the interval under the platform's mapping and synchronization rules.

Follow the second value through arithmetic, allocation, copy, dispatch, or authority decisions. If a version-counter or ownership protocol is present, verify its ordering, retry, wrap and reuse rules rather than assuming the counter makes the snapshot coherent.

## Constructed x86-64 driver example

Assume `RDI` holds a request in memory that the caller can modify concurrently and offset `+8` contains a 32-bit length.

```asm
mov  eax, dword ptr [rdi+8]   ; first fetch
cmp  eax, 100h                ; validate length <= 256
ja   reject
mov  edx, dword ptr [rdi+8]   ; second fetch after the check
mov  rcx, rbx                 ; fixed 256-byte destination
call copy_from_shared
```

If the caller changes the field from 16 to 4096 between the two loads and `copy_from_shared` trusts `EDX`, the consumed count was never bounded by the shown comparison. Establishing the finding still requires that the source remains writable during this interval and that no hidden validation or bounded-copy contract constrains the call.

## Primitive and impact limits

The direct result can be out-of-bounds access, wrong allocation/copy relationship, variant confusion, or authorization based on a different value than the one used. Impact depends on the consumer and the trust boundary crossed by the mutable memory.

## Related knowledge and primary sources

`reference-concurrency-mutable-validation-double-fetch` and platform driver or shared-ring references define capture and access contracts. This profile repeats the two-fetch, mutable-window, and changed-consumer proof locally.

Reviewed 2026-10-09 against Microsoft [ProbeForRead](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-probeforread), Linux kernel [user-space memory access](https://docs.kernel.org/core-api/mm-api.html#user-space-memory-access), and [MITRE CWE-367](https://cwe.mitre.org/data/definitions/367.html). The assembly is constructed and uses an internal register convention rather than an OS callback ABI.
