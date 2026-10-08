---
id: reference-swift-ownership-native-boundaries
title: Swift weak and unowned references, unsafe buffers, Unmanaged and actor reentrancy
kind: reference
topics: [swift, arc, ownership, unsafe-pointers, callbacks, exclusivity, actors, reentrancy]
platforms: [macos, ios, linux, windows]
architectures: [x64, arm64]
---
# Swift ownership and native-boundary evidence

## Weak, unowned and unowned(unsafe) fail differently

Swift weak references do not keep an instance alive and become nil when it is
deallocated. Safe unowned references do not keep it alive either, but accessing
one after deallocation produces a runtime error. unowned(unsafe) removes that
safety check and can expose invalid memory. [1]

Distinguish a checked lifetime trap from an unchecked use-after-free. A weak nil
result can still alter authorization or cleanup control flow. For an escaping
callback, identify which reference actually keeps each object alive until use;
an unowned capture is a lifetime assertion, not ownership.

## Closure retention cycles are not evidence that all captured data survives

A Swift object holding a closure that strongly captures that object can form a
strong-reference cycle; weak/unowned capture lists change the ownership graph. [1]
Inspect the object-to-closure and closure-to-object edges separately from raw
pointer captures. Breaking a cycle can expose an incorrect callback-lifetime
assumption; retaining the closure does not make arbitrary native storage safe.

For an availability finding, establish repeated reachable retention and resource
growth rather than reporting every cycle as exploitable. Runtime release or
closure helper symbols alone reveal neither the retained data's sensitivity nor
what the callback does with it.

## Unmanaged and opaque pointers do not validate or automatically own objects

Swift Unmanaged.passRetained supplies an unbalanced retain; passUnretained does
not. takeRetainedValue consumes an existing ownership responsibility;
takeUnretainedValue does not consume one. toOpaque/fromOpaque convert representation
without changing reference counts. [2]

Match the native API's real transfer contract. An opaque pointer is not proof of a
live object of the claimed class. When native code stores callback context, trace
registration failure, repeated callbacks, cancellation and final teardown.
Consuming the same transferred ownership on every callback can over-release;
passing unretained context requires some independent owner until callbacks finish.

## Array unsafe-buffer pointers are scoped borrows, not durable exports

Array.withUnsafeBufferPointer exposes contiguous storage only for the duration of
the call; storing or returning that pointer for later use violates its contract.
Array.withUnsafeBytes likewise limits its raw-buffer argument to the closure. [3]

A native callee that queues work must not retain this temporary pointer merely
because the Swift array variable remains in scope. Recover whether it copies the
bytes synchronously or uses them later. Keep element counts distinct from byte
counts and establish initialized extent, alignment and mutation permissions for
the actual native operation. A raw pointer passed to C does not carry the buffer's
extent or impose bounds checks on the callee.

## Exclusive access protects Swift mutation, not an entire security transaction

Swift's memory-access rules reject conflicting overlapping accesses to the same
storage when modification requires exclusive access. inout parameters keep an
access open for the call; two such arguments aliasing the same value can conflict.
Some conflicts are diagnosed statically and others at runtime. [4]

Do not rename access-management helpers as application locks. Recover the access
interval and storage identity, including callbacks during the interval. Absence
of an exclusivity failure does not establish native-pointer safety, correct
authorization or synchronization for every external resource.

## Actor isolation allows state changes between await-separated segments

Swift actors serialize access to their isolated mutable state. An await marks a
possible suspension point, allowing other work before resumption. Consequently,
an actor method spanning await is not automatically one indivisible transaction. [5]

For a check-then-act investigation, record the state checked before suspension,
what another actor operation may change, and what the resumed code assumes.
Revalidate or reserve the relevant state before the effect when the contract
requires it. This is a logical race hypothesis even if individual memory accesses
are data-race-free. Actor isolation is not a permissions check on external inputs.

## Primary sources and scope

Reviewed 2026-10-02 against official Swift book and standard-library main-branch
sources. Language/API contracts are separated from private object layout; exact
runtime helper sequences can vary or be optimized away. Objective-C bridge casts
are in `reference-objc-ownership-blocks`; native ABI reconstruction is in
`reference-swift-metadata-abi`.

1. [Swift language guide: ARC](https://raw.githubusercontent.com/swiftlang/swift-book/main/TSPL.docc/LanguageGuide/AutomaticReferenceCounting.md): weak/unowned safety and closure cycles.
2. [Swift standard library: Unmanaged](https://raw.githubusercontent.com/swiftlang/swift/main/stdlib/public/core/Unmanaged.swift): retain transfers and opaque conversions.
3. [Swift standard library: Array](https://raw.githubusercontent.com/swiftlang/swift/main/stdlib/public/core/Array.swift): withUnsafeBufferPointer and withUnsafeBytes lifetime.
4. [Swift language guide: Memory Safety](https://raw.githubusercontent.com/swiftlang/swift-book/main/TSPL.docc/LanguageGuide/MemorySafety.md): exclusive access and inout conflicts.
5. [Swift language guide: Concurrency](https://raw.githubusercontent.com/swiftlang/swift-book/main/TSPL.docc/LanguageGuide/Concurrency.md): suspension and actor isolation.
