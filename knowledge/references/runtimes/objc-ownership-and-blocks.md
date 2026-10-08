---
id: reference-objc-ownership-blocks
title: Objective-C ARC, autorelease, bridging and block callback lifetime
kind: reference
topics: [objective-c, arc, ownership, autorelease, blocks, callbacks, use-after-free]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Objective-C ownership and callback lifetime

## Reference ownership is responsibility, not a pointer-copy count

In Cocoa reference counting, an owner keeps an object alive and must eventually
relinquish that ownership. Retain acquires ownership; release relinquishes it.
Destruction invokes dealloc, which can release further resources. [1]

Track acquisition, transfer and release on each feasible path. A raw pointer copy
does not acquire ownership. A final release can execute cleanup code: inspect
callbacks and shared-state changes before using a previously borrowed pointer
again. Manual reference counting and compiler-managed ARC can coexist across
binary boundaries; missing source-level retain calls do not prove missing owners.

## ARC strong, weak and unsafe_unretained have different lifetime effects

Clang ARC strong storage owns its referent. Supported weak storage does not keep
the referent alive; a weak read safely acquires it for the full expression or
produces nil. unsafe_unretained lacks that protection. Some classes do not support
weak references. [2]

Do not interpret objc_loadWeakRetained as an ordinary unprotected pointer load.
Conversely, copying a weak value into unmanaged storage does not preserve its
protection indefinitely. Object lifetime protection does not lock mutable fields
or make a check-then-use sequence atomic.

## Autorelease pools defer release, not arbitrary asynchronous lifetime

An autorelease schedules a release when the enclosing autorelease pool drains.
Several autoreleases schedule several releases; draining may destroy the object.
Nested pools and per-thread pools determine the applicable boundary. Long loops
accumulating autoreleased temporaries can increase peak memory. [3]

A later callback needs a valid owner independent of the producer's pool. Inspect
pool-pop and callback-registration paths when a pointer survives an event-loop
iteration. Do not infer every non-owning return is physically in a pool: ARC's
return-value optimization permits avoiding actual autorelease operations. [2]

## bridge, bridge_retained and bridge_transfer describe ownership transfer

For Clang ARC, __bridge converts between retainable and non-retainable pointer
types without transferring ownership. __bridge_retained supplies a +1 ownership
responsibility to the non-ARC recipient. __bridge_transfer gives ARC responsibility
for consuming an existing owned reference. [2]

These casts do not validate the pointed-to object's type or turn arbitrary bytes
into an Objective-C object. For a native callback context, match the transfer to
its cleanup on success, registration failure and cancellation. A second consuming
transfer can over-release; never consuming transferred ownership can leak.

## Blocks capture values; copying a block does not deep-copy raw buffers

A block combines executable code with captured state and may reside in stack,
global or heap storage. Ordinary automatic variables are captured by value;
__block variables permit shared mutation. Block_copy and Block_release manage
block storage under their applicable ownership model. [4]

A captured C pointer is still a pointer to the original allocation, not a copy of
its bytes. Establish both block lifetime and pointee lifetime before treating an
asynchronous callback as safe. __block does not itself provide mutual exclusion.
Use ARC ownership rules for ARC object captures, not historical garbage-collection
or manual-mode examples from the older Blocks language specification. Under ARC,
__block alone does not make an object reference non-owning; its ownership
qualifier still matters. [2]

## Block invoke, copy/dispose helpers and byref forwarding are different edges

In the documented Apple Blocks ABI, an invoke function receives the block pointer
before explicit parameters. The descriptor's copy/dispose helpers and signature
are conditional on flags. A captured __block cell uses a forwarding pointer so
accesses can follow storage moved from stack to heap. [5]

Do not mistake a copy helper for the callback's behavior or assume all descriptor
fields are present. Follow capture initialization into invoke, and cleanup into
dispose. Shared byref indirection can explain an apparently stale stack address;
it must be decoded before alleging a use-after-return. The documented layout is
an Apple ABI contract, not every closure representation in every language.

## Primary sources and scope

Reviewed 2026-10-02: Clang living ARC specification and Apple Blocks ABI document,
plus archived Cocoa reference-counting guides (2012). No fixed retain-counter
layout or one-to-one emitted helper sequence is assumed. Dispatch evidence:
`reference-objc-dispatch-type-evidence`; Swift opaque references:
`reference-swift-ownership-native-boundaries`.

1. [Apple: Memory Management Policy](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/mmRules.html): ownership and dealloc.
2. [Clang: Automatic Reference Counting](https://clang.llvm.org/docs/AutomaticReferenceCounting.html): ownership semantics, weak reads, unretained returns and bridged casts.
3. [Apple: Autorelease Pool Blocks](https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/mmAutoreleasePools.html): deferred release and pool scope.
4. [Clang: Blocks Language Specification](https://clang.llvm.org/docs/BlockLanguageSpec.html): storage, value captures and __block; historical object/GC examples are not modern ARC rules.
5. [Clang: Apple Block Implementation Specification](https://clang.llvm.org/docs/Block-ABI-Apple.html): invoke/descriptor and byref forwarding, ABI.2010.3.16 distinctions.
