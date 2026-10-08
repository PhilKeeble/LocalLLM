---
id: playbook-validation-allocation-lifetime-trace
title: Trace allocation generations, ownership transfers, mutation, release and later use
kind: playbook
topics: [lifetime, allocation, ownership, use-after-free, double-free, realloc, callbacks, windbg]
platforms: [windows, linux, macos, freebsd, android, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Reconstruct a resource's lifetime through the consuming operation

## Define the object and the disputed lifetime claim

Start with the suspect access, release, disclosure or retained resource, using
existing authorized captures and static evidence. Identify the process instance,
allocator/runtime, resource type and operation. A memory address, OS handle,
borrowed view and underlying object require different identity records.

Assign an analytical generation to each evidenced acquisition or replacement.
Generation means one lifetime in this investigation, not necessarily a counter
stored by the target. Preserve unknown acquisition history as unknown; do not
invent a generation merely because a snapshot shows readable memory. Address
reuse and handle-number reuse can make a stale value refer to a different object.
Use reference-native-ownership-release-dangling and
reference-native-resource-lifetimes-results for the relevant contracts.

## Record acquisition, mutation and release as distinct events

For each event retain its evidence source, process/thread, location, ordering
information, object generation and whether it was attempted or completed.

| Event | Information needed to interpret it |
| --- | --- |
| Acquire | Allocator/heap, requested size or resource parameters, actual result, returned base/handle, initial owner |
| Publish or borrow | Receiving field/queue/callback, owner retained or transferred, range and permitted lifetime |
| Mutate or resize | Old/new extent, changed fields/bytes, return status, alias updates, initialized length |
| Release or retire | Matching release contract, owner/reference surrendered, outcome, pending users, reclamation condition |
| Consume | Actual access or operation, width/range, object generation, available lifetime protection |

An API-entry breakpoint proves arrival with arguments, not successful allocation
or release. Pair calls and outcomes by invocation, including thread, recursion,
exception exits and callbacks. A guessed return register from a different frame
is not the result. Use playbook-validation-debugger-evidence for context selection.

## Follow allocator wrappers without counting one allocation twice

Distinguish application object, wrapper user region, backing allocation and virtual
memory reservation. A wrapper and the allocator it calls can describe two layers
of the same acquisition; a custom arena can serve many objects from one block.
Record parent-child extents rather than adding every nested allocator event to
an independent outstanding-allocation count.

Trace custom free lists, arena reset and bulk teardown when those are the actual
release paths. An OS allocator breakpoint can miss object creation or reuse inside
an existing arena. Conversely, releasing backing storage does not demonstrate
that application destructors or non-memory cleanup ran. For a candidate leak,
separate intentional cache/arena retention from unreachable or unbounded retained
resources. Do not equate process memory usage with the sum of live payload sizes.

## Recover ownership edges, not just pointer copies

Classify each assignment or handoff as ownership transfer, added ownership, borrow,
interior view or unknown. Inspect the actual operation and contract: copying a
raw pointer does not itself retain its pointee, and std::move alone is a cast,
not a release or transfer. A later free in another component can be correct when
the ownership transfer and matching deallocator are established.

For callbacks and asynchronous operations, track registration, submission,
completion, cancellation and teardown separately. Determine which owner protects
the context during a callback, and what establishes that no remaining callback
can use it. A request to cancel is not proof that storage can already be reclaimed.
Use reference-concurrency-refcounts-reuse and the particular callback/I/O contract;
do not substitute a generic refcount model for a platform's actual protocol.

## Treat resize results as state transitions, including failure

Preserve old base/extent, requested extent, API flags, actual result, new base and
updates to every owner/view. A successful shrink can invalidate a previously
in-range access even without numerical address movement. A failed resize can
leave the old resource alive while application metadata has already changed.

GNU libc realloc with valid non-NULL input and nonzero size preserves the old block
on allocation failure; its documented zero-size behavior is a separate case.
Windows HeapReAlloc also preserves the original block on failure, but has distinct
input and exception-mode rules. Do not merge the two API contracts. Use
reference-native-ownership-release-dangling and
reference-windows-heap-allocation-contracts. On success, establish alias validity
under the actual contract rather than treating equal address bits as sufficient.

## Establish cross-thread order and lifetime protection

Identify synchronization that orders publication, lookup, reference acquisition,
removal and final release. Collector arrival order or timestamps alone may not
establish program order across threads. API entry/exit timestamps bound an interval;
they do not automatically locate the internal moment at which ownership changes.
Mark overlapping or unordered events instead of inventing one exact sequence.

For a use-after-free candidate, connect an actual later access through the stale
alias to an ended lifetime. For double release, show two releases of the same
generation on one feasible path; mutually exclusive cleanup blocks are insufficient.
A refcount read or atomic increment after lookup is not automatically protection
against intervening destruction. Conversely, retained ownership or a valid
reclamation protocol can refute the proposed ordering. Preserve that counterevidence.

## Interpret heap history only within its recorded scope

Distinguish a containing allocation recovered from current heap metadata from
recorded allocation/free events. Historical stacks require that the relevant
instrumentation captured them and that the needed data survived acquisition.
Retain allocator identity, diagnostic configuration, capture coverage and actual
decoded evidence. Windows-specific decoder contracts and limits live in
reference-windows-heap-identity-diagnostics.

A containing block now is not proof that the earlier object at that address was
alive then. Missing allocation/free stacks are not proof that no acquisition or
release occurred. A dump cannot retroactively supply unrecorded events. GDB, LLDB
and WinDbg watchpoints likewise observe their installed ranges, not an object's
entire past; see reference-validation-breakpoint-watchpoint-evidence. Separate
the pointer-storage watch from a watch on pointee fields or the refcount.

## Link bytes and authority to effects in malware investigations

Track where meaningful bytes enter storage, which transformations change them,
which range is actually consumed and which external operation receives it.
Keep allocation capacity, initialized bytes and logical payload length separate.
Data left in freed or reused storage can be residual; its presence alone does
not establish use by the current owner or successful communication.

For handles, connect acquisition authority, duplication/inheritance, process
ownership, use and closure. Closing one reference does not prove all copies are
gone; closing a Windows process handle does not terminate that process.
Use reference-windows-handle-authority-transfer. Allocation churn, refcount helpers
or copied strings alone establish neither a vulnerability nor malicious intent;
the relevant conclusions need a violated invariant or evidenced behavior.

## Report the smallest supported lifetime chain and its gaps

Provide the acquisition/ownership evidence, state changes, release or retirement,
consumer and reason the operation violates the specific contract. State whether
this is a witnessed sequence, a feasible static path or an unresolved candidate.
If capture began after allocation, the missing prefix remains a limitation. If
events were filtered or lost, absence of a release is not proof of a leak.

Constructed example: callback context points to object A; shutdown frees A; a new
object B occupies the same address; the queued callback reads through A's retained
alias. A snapshot showing B cannot establish that the callback legitimately acquired
B. Prove the stale handoff and ordering; without them, address equality alone does
not establish either safe use or a use-after-free. Further live observation, when
needed, requires separate authorization and isolation, not changes to a shared target.

## Source basis and scope

Reviewed 2026-10-02. Investigative synthesis using the linked local contracts;
platform tags do not imply uniform allocator, language or handle semantics.

- [C++ object lifetime](https://eel.is/c++draft/basic.life): object lifetime versus retained storage and construction/destruction qualifications.
- [GNU libc realloc](https://sourceware.org/glibc/manual/latest/html_node/Changing-Block-Size.html): nonzero failure and zero-size distinctions.
- [Windows HeapReAlloc](https://learn.microsoft.com/en-us/windows/win32/api/heapapi/nf-heapapi-heaprealloc): result, resize and exception mode.
- [WinDbg !heap](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-heap): containing-block and recorded page-heap information.
- [Windows CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle): resource-specific closure and execution lifetime.
