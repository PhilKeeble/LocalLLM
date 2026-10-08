---
id: reference-concurrency-refcounts-reuse
title: Reference acquisition, destruction, ABA and recycled identity
kind: reference
topics: [concurrency, refcounts, lifetime, aba, object-identity]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Reference acquisition, destruction, ABA and recycled identity

## Scope and lifetime invariant
Reviewed 2026-10-02. Refcount names do not define a universal protocol. Recover
initial count, owning references, borrowed aliases, lookup/removal synchronization,
zero transition, release callback and storage reclamation. Linux kref/refcount_t
facts below are explicitly kernel-specific. A nonzero integer at an address is
not proof that the address still belongs to the same live object.

The required investigation invariant is that every use is covered by a valid
lifetime guarantee and every owned reference is released according to contract.
An atomic count can prevent lost increments yet leave unsafe acquisition,
incorrect ownership accounting, resurrection or payload races.

## Acquire before handoff, not after reclamation
Linux kref guidance requires a valid reference to cover a handoff to another
execution context. If both sender and receiver retain ownership, the receiver's
reference must be acquired before handoff. Alternatively, the sender can transfer
its existing reference and relinquish its own use; that does not require an extra
increment/decrement pair. Acquiring from a lookup without an owned reference needs
protection against final release. kref_get_unless_zero requires valid storage and
a checked return value. [1]

Constructed unsafe sequence: A finds pointer P and leaves lookup protection;
B removes P and frees it; A atomically increments P's count. Atomicity does
not repair the already invalid access. Increment-unless-zero alone cannot
protect already freed memory. Recover the actual protection interval around
lookup and acquisition, not merely the presence of a refcount helper.

## Release, resurrection and memory ordering
Linux kref_put calls the release function on the final decrement. After giving
up its reference, a caller cannot assume the object remains alive because its
own decrement was not final: another thread can release the remaining one. [1]
The release callback may defer reclamation; distinguish logical death from
storage reuse and identify which operations remain legal in between.

For custom counters, check whether zero-to-one acquisition is prohibited or
part of an explicitly protected reinitialization protocol. An unconditional
increment after destruction starts can create a positive count without restoring
the destroyed object's invariants. Count atomicity and payload publication are
different obligations. Linux refcount_* and atomic_* operations can have different
memory-order guarantees; replacing one with the other is not generally semantics
preserving. [2] Prove initialization visibility and final-release ordering under
the actual primitive, not a generic assumption that all atomics are full barriers.

## Overflow, underflow and saturation
For a custom fixed-width counter, recover arithmetic width, signedness, initial
count, increment paths, decrement tests and failure behavior. Constructed 8-bit
wrapping counter: 255+1 becomes 0. Whether that enables early destruction depends
on subsequent tests and reachable operations; it is not automatically a UAF.
An extra release can underflow rather than free immediately, producing a leak
or a later incorrect transition. Source signed overflow and emitted arithmetic
must not be conflated.

Linux v6.18 refcount_t implements saturation behavior intended to prevent
wraparound-induced premature release, unlike a plain generic counter. Its source
documents implementation/racing-update assumptions; this is not an unconditional
proof for arbitrary batched or custom counters. [3] Check the exact target
implementation. Saturation may preserve storage instead of reclaiming it;
that does not establish bounded resource use or correct ownership accounting.

## ABA and reused addresses
Constructed ABA: A reads head=P and successor=Q; B removes P, changes the list,
then installs a different node at address P; A's CAS comparing only head==P
succeeds with stale successor Q. Equal address bits do not prove unchanged
object identity or intervening state. ABA can also involve value reuse without
freeing memory. A successful CAS validates only its compared representation,
not all earlier observations; this follows from the comparison contract. [4]

Separate ABA from use-after-free: deferred reclamation can keep an address
readable without making an old logical state current. Preserve allocation or
object generations, not just pointer values, in traces. Not every A-to-B-to-A
sequence is harmful; demonstrate the invariant that depends on unchanged history.

## Generation counters and reclamation protocols
Constructed generation scheme: compare (slot, generation) to reject completion
for a recycled slot. The check must cover the generation captured at submission
and the current object used at commit, without an unprotected reuse interval.
Finite generations can wrap: state the reuse rate and maximum outstanding
lifetime before claiming wrap is feasible or impossible. Restart/reconnect
can reset counters independently of numeric wrap.

Hazard pointers, epoch/RCU schemes and retained references have different rules;
their mere presence is not sufficient. Identify reader entry/exit, protected
object, publication/recheck, retirement and the condition allowing reuse.
Linux kref's RCU example specifically retains refcount storage through the
required grace period. [1] Do not generalize this to every RCU API, pointer
lookup or custom epoch implementation without inspecting that contract.

## Primary sources
Reviewed 2026-10-02. Kernel documentation as served; saturation implementation
pinned to Linux v6.18. C++ comparison source is the living draft.

1. [Linux kref ownership and lookup examples](https://docs.kernel.org/core-api/kref.html).
2. [Linux refcount_t versus atomic_t ordering](https://docs.kernel.org/core-api/refcount-vs-atomic.html).
3. [Linux v6.18 refcount.h](https://raw.githubusercontent.com/torvalds/linux/v6.18/include/linux/refcount.h).
4. [C++ compare-exchange operations](https://eel.is/c++draft/atomics.types.operations).
