---
id: vulnerability-information-stale-buffer-cross-context-disclosure
title: Stale buffer contents disclosed across security contexts
kind: vulnerability
topics: [information-disclosure, stale-data, buffer-reuse, cross-tenant]
platforms: [cross-platform]
architectures: [any]
---

# Stale buffer contents disclosed across security contexts

## Definition and violated invariant

This vulnerability occurs when storage reused after pooling, free, remapping, reset or ownership transfer retains data from one security context and exposes it to another. Reuse is not itself unsafe: the violated invariant is that bytes visible to the new owner or recipient were neither initialized for that context nor authorized for it.

The old and new contexts may be processes, users, tenants, virtual machines, privilege levels, protocol requests or trust domains. Establish the actual isolation boundary; reuse within one authorized context may be a confidentiality hygiene issue without crossing a security boundary.

## Conditions that establish the issue

Show a feasible lifecycle connecting the same physical or logical storage generation to a protected write by context A, release or reuse without complete sanitization, and a read or transfer observable by context B. Track byte ranges: a partial clear only protects the bytes it covers, while a full overwrite before exposure can refute the stale-data path.

The observer need not receive raw bytes if a comparison, compression result, error, checksum or other repeatable signal reveals them. For direct disclosure, establish the returned base and count. For derived disclosure, state the query model and what can actually be inferred.

## Evidence that is not sufficient

A pool allocator, free-list reuse, missing explicit clear or reused virtual address is not sufficient. The allocator, operating system, hypervisor or device may zero storage before the new context can observe it; the object may be fully overwritten; or both uses may share authority. A use-after-free is a different root cause unless invalid lifetime access is the path that exposes the stale bytes.

Do not infer cross-tenant leakage merely from equal addresses in separate address spaces. Establish shared backing, actual reuse or a transfer between them.

## Investigation sequence

Identify the storage object, backing allocation or mapped pages and define context A and context B. Trace allocation, protected writes, release, pool return, reset, reassignment, initialization and first exposure. Compare the protected interval with every clear or overwrite using exact offsets and lengths.

At binary level, distinguish allocation from initialization and logical length from capacity. Follow allocator flags, page-fault or mapping behavior, device completion, DMA ownership and error paths. Confirm that the suspected old bytes reach an output readable by context B rather than remaining inaccessible capacity.

## Constructed lifecycle example

Assume a service maintains a 4096-byte response pool. Request A writes a 2000-byte confidential response and returns the buffer to the pool. Request B obtains the same buffer, writes a 40-byte error header and sends all 4096 bytes. Bytes 40 through 1999 retain A's data if no pool or allocation step cleared them.

This establishes disclosure only after confirming the same backing storage, the missing overwrite, the 4096-byte transfer and B's lack of authority to read A's data. If the pool zeroes on checkout, the allocator supplies zeroed pages or the transport sends only 40 bytes, the constructed path is refuted.

## Primitive and impact limits

Characterize exposed offsets, quantity, selection control, reuse probability, repetitions and whether the attacker can influence the prior occupant. A one-time fragment and a repeatable cross-tenant read are materially different primitives. State whether the contents include demonstrated secrets, pointers or merely unspecified prior data.

Stale disclosure does not itself grant memory modification or execution. A freed object later interpreted as live control data may instead support a use-after-free primitive and should be analyzed under that root cause as well.

## Related knowledge and primary sources

`reference-windows-response-structures-initialization` explains exact outbound-range and last-write analysis. This profile adds the cross-context storage lifecycle that distinguishes stale reuse from first-use uninitialized memory.

Reviewed 2026-10-09 against [NIST SP 800-53 Revision 5 control SC-4](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), which requires preventing information transfer through shared resources, and [MITRE CWE-226](https://cwe.mitre.org/data/definitions/226.html), which describes sensitive information remaining in a reused resource. These sources define the security condition; target allocator, mapping, transport and device contracts still determine whether a particular path exposes residual bytes.
