---
id: vulnerability-kernel-heap-out-of-bounds-write
title: Kernel heap out-of-bounds write
kind: vulnerability
topics: [memory-safety, out-of-bounds-write, kernel, heap, drivers]
platforms: [windows, linux, android, freebsd]
architectures: [x86, x64, arm, arm64]
---

# Kernel heap out-of-bounds write

## Definition and invariant

A kernel heap out-of-bounds write occurs when kernel-context code writes outside the intended extent of a dynamically allocated kernel object. If an allocation requests `N` bytes, accesses through that object must remain within `[base, base + N)` unless an API contract explicitly grants a different usable extent.

Allocator rounding does not silently enlarge the semantic object. The allocator may reserve a larger backing block, but writing into that extra space is still outside the requested object unless the relevant allocator contract explicitly permits and exposes it. This issue is distinct from a kernel stack overwrite, use-after-free, double free, or a write into an undersized caller-owned output buffer.

## When it is a security problem

The issue is security-relevant when a less-privileged principal can reach the kernel path, influence the destination offset or write extent, and cause a write beyond the allocated object's boundary. The boundary may be a system call, device request, compatibility interface, filesystem operation, network protocol, hypercall, shared-memory protocol, or data supplied by a peripheral.

Confirm both authority and memory evidence: who can open or invoke the interface, which request fields are captured, the requested allocation size, the complete write range, and whether the kernel actually performs the write. A kernel-context fault establishes availability impact more readily than privilege escalation.

## What does not establish the issue

A kernel crash, heap-allocation call, user-copy helper, large length, allocator diagnostic, or adjacent privileged object is not sufficient by itself. The length may already be bounded, the copy may stop or fail, a request may be inaccessible to the relevant principal, and a decompiler may assign the wrong integer width or structure layout.

Do not treat slab or pool adjacency as stable without runtime evidence. Allocator class, per-CPU or per-node behavior, quarantine, randomization, object lifetime, and competing allocations can change placement. Likewise, remaining inside a rounded allocation bucket does not make an object-level overrun valid.

## Investigation workflow

Recover the request boundary first: dispatch operation, caller authority, access checks, buffer-transfer model, compatibility translation, and capture or probing semantics. Track the exact width, signedness, units, and provenance of every length, offset, and element count through validation and conversion.

Identify the allocation API and requested size, then calculate every write as a complete half-open range. Check addition and multiplication before allocation, differences between declared and captured lengths, partial-copy return conventions, loop termination, terminators, and whether validation dominates every write. Keep lifetime and synchronization defects separate unless the same path also permits the object to be freed or resized.

## Constructed source example

This platform-neutral pseudocode assumes the request fields and payload pointer have already been captured into stable kernel-owned state, and that `copy_from_captured` copies exactly the requested count or reports failure:

```c
int handle_request(const struct captured_request *request)
{
    size_t allocation_size = request->declared_length;
    size_t copy_size = request->payload_length;
    unsigned char *destination = kernel_alloc(allocation_size);

    if (destination == NULL)
        return NO_MEMORY;
    if (copy_from_captured(destination, request->payload, copy_size) != 0) {
        kernel_free(destination);
        return COPY_FAILED;
    }
    process_record(destination, allocation_size);
    kernel_free(destination);
    return SUCCESS;
}
```

If an accessible caller can make `copy_size > allocation_size`, the shown path writes beyond the requested object. Real user-copy APIs have platform-specific fault and residual-count conventions; those contracts must replace the pseudocode assumption during an investigation. The later processing and cleanup do not repair a write that has already crossed the boundary.

## Constructed x86-64 representation

This abbreviated System V AMD64 example uses `RDI` for the request pointer. The hypothetical captured structure stores `declared_length`, `payload_length`, and `payload` at offsets 0, 8, and 16. An omitted prologue preserves the nonvolatile `RBX` register:

```asm
mov  rbx, rdi
mov  rdi, [rbx]          ; requested allocation size
call kernel_alloc
test rax, rax
je   allocation_failed
mov  rdi, rax            ; destination
mov  rsi, [rbx+10h]      ; captured payload
mov  rdx, [rbx+8]        ; copy size
call copy_from_captured
```

The allocation and copy consume different request fields, and the excerpt contains no comparison between them. That is a lead, not complete proof: a dominating check or request-construction invariant may relate the fields. Confirm the structure layout, calling convention, preserved registers, helper semantics, and all predecessor paths in the actual binary.

## Object range and allocator effects

Let the requested object size be `N`, the write offset be `O`, and the write length be `M`. The write is valid only when the arithmetic is representable and `[O, O + M)` is contained in `[0, N)`. For the constructed example, `O` is zero, so any `M > N` crosses the object boundary.

If the allocator supplies a backing block of size `B >= N`, bytes in `[N, B)` may be physically mapped while remaining outside the requested object's extent. A write ending within `B` can silently corrupt padding or allocator-reserved space; a write beyond `B` may reach metadata, another object, a guard region, or unmapped memory. The actual consequence requires target-specific allocator and runtime evidence.

## Primitive and impact conditions

The direct primitive is a kernel-context write beyond a live heap object's end. Record the controllable offset, maximum extent, byte values, repeatability, execution context, and whether corrupted state is subsequently read, freed, dispatched, or checked.

A demonstrated kernel fault supports denial-of-service impact for the reachable caller. Privilege escalation requires an unprivileged path plus evidence that controlled corruption reaches security-relevant data or develops into a stronger read, write, or control primitive. Remote impact additionally requires a remotely reachable boundary and the necessary configuration. Do not equate kernel memory corruption with arbitrary write, controlled instruction flow, or privilege escalation without that chain.

## Platform-specific evidence boundaries

On Windows, relate the path to the device object's access policy, IOCTL access bits and transfer method, captured buffer, pool allocation contract, requestor mode, and execution level. On Linux and Android, establish the file-operation, syscall, netlink, ioctl, Binder, or other entry contract together with user-copy and allocator semantics. Other kernels require equivalent boundary, allocation, and copy contracts.

Keep the generic object-bounds conclusion separate from platform implementation details. Names, allocator internals, and mitigation behavior change; the required proof remains caller reachability, requested object extent, actual write range, and a justified consequence.

## Related knowledge contracts

- `reference-native-bounds-objects-terminators` owns requested object extent and full-range reasoning.
- `reference-native-integer-size-buffer-arithmetic` covers size arithmetic, conversions, and allocation/use mismatch.
- `playbook-specialist-kernel-boundary` owns generic request authority, user-copy, synchronization, and lifetime analysis.
- `reference-windows-driver-ioctl-buffer-access` owns Windows IOCTL access and buffer-transfer semantics.
- `reference-windows-driver-irql-pool` owns Windows kernel pool and execution-level constraints.
- `reference-linux-kernel-interface-representations` and `playbook-linux-kernel-request` own Linux interface representation and request tracing.
- `playbook-vr-evidence-and-chaining` separates the memory defect from exploitability and final impact.

## Scope and primary sources

This profile defines cross-platform proof obligations for a kernel heap overwrite. Its source and assembly are constructed examples, not code from a particular kernel or a signature for a specific compiler.

Primary references reviewed for this draft:

- MITRE CWE-122, *Heap-based Buffer Overflow*: <https://cwe.mitre.org/data/definitions/122.html>
- Linux kernel documentation, *Memory Allocation Guide*: <https://docs.kernel.org/core-api/memory-allocation.html>
- Linux kernel documentation, *Memory Management APIs*: <https://docs.kernel.org/core-api/mm-api.html>
- Microsoft, *ExAllocatePool2 function*: <https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-exallocatepool2>
- Microsoft, *Buffer Descriptions for I/O Control Codes*: <https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/buffer-descriptions-for-i-o-control-codes>
