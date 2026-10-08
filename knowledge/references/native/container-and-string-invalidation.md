---
id: reference-native-container-invalidation
title: C++ container iterator, reference and string-buffer invalidation
kind: reference
topics: [cpp, containers, iterators, invalidation, vector, string, small-string, lifetime]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Container and string invalidation

## Scope and evidence identity

These are standard-library contracts, not universal layouts for containers in
stripped binaries. Identify the library/version, element type, operation and
allocator before applying a rule. Distinguish an iterator, element pointer,
reference, numeric index and pointer to the container itself. One can remain
valid when another does not. Debug-iterator layouts can differ from release
builds; recognizers must be checked against accesses and operations.

## vector size, capacity and reallocation

vector reserve can increase capacity without changing size. Capacity therefore
does not establish a count of constructed elements. Reallocation invalidates
element pointers, references and iterators, including the past-the-end iterator.
reserve reallocates when its requested capacity exceeds the current capacity;
shrink_to_fit is a nonbinding request, not a promise of relocation. [1]

Constructed investigation: code retains a pointer to element zero, then calls
push_back. Establish old size/capacity and whether growth reallocates on the
feasible path. If there was spare capacity, pointer invalidation from reallocation
alone is unproven; the saved end iterator still needs the insertion rule. If a
vector has size 0 after reserve(32), capacity 32 does not make index 0 a valid
element access. Allocation-level sanitizers may not see this logical boundary.

## vector insertion and erasure without reallocation

When vector insertion does not reallocate, references/pointers/iterators before
the insertion point remain valid; those at or after it, including old end, are
invalidated. Erase invalidates iterators and references at or after the erased
position. [2] A stable allocation address does not establish stable element
identity when elements are shifted.

Constructed scenario: retain an iterator to element 4, erase element 1, then use
the old iterator. Check the documented invalidation and what machine object now
occupies that position. An unchanged address may select a different logical
record, not merely cause a crash. A numeric index also needs rebinding after
insert/erase even though it is not a C++ iterator object.

## Other containers have different stability contracts

For std::list, insertion preserves existing iterators/references; erasure
invalidates only those to erased elements. [3] For std::deque, insertion at an
end invalidates iterators but preserves element references; middle insertion
invalidates both. Erasure rules depend on whether an end or middle is erased. [4]
Do not apply vector's contiguous-storage model to either container.

Standard unordered-container rehash invalidates iterators and changes buckets/
ordering, but preserves element pointers and references. [5] Investigate whether
code holds an iterator or an element reference across insertion/rehash. A report
that all references dangle after every rehash contradicts this contract; custom
flat/open-addressed containers need their own rules and may relocate elements.

## Strings, views and small-string transitions

basic_string mutations can invalidate character pointers, references and
iterators under its operation-specific rules. Non-const accessors such as
operator[], at, data and begin are exceptions to the broad mutation rule. [6]
A string_view does not protect the underlying storage from owner mutation or
destruction; see `reference-native-ownership-release-dangling`.

Small-string optimization is implementation detail: implementations can keep
short data inside the string object and longer data in separate storage. Layout,
capacity threshold and discriminator differ across libraries/builds. [7]
Constructed investigation: test a retained data pointer across growth, move,
swap and destruction. An inline character array can die with a stack owner;
a heap representation can become stale after reallocation. Do not require a
visible free call to establish invalidation, or invent one common SSO threshold.

## Investigation acceptance check

Record the acquisition operation and element identity, intervening mutation,
applicable invalidation rule, actual later use and feasible input/state. Separate
library-contract violation from the observed binary effect. Check alternative
owners, copies and reacquisition after mutation before concluding stale use.
If container identification is uncertain, describe the observed relocation or
shift and pending library hypothesis rather than asserting a standard type.

## Sources and verification scope

Reviewed 2026-10-02; current C++ working-draft clauses and Microsoft's 2023
implementation explanation. No particular target layout or growth factor tested.

1. [vector capacity](https://eel.is/c++draft/vector.capacity).
2. [vector modifiers](https://eel.is/c++draft/vector.modifiers).
3. [list modifiers](https://eel.is/c++draft/list.modifiers).
4. [deque modifiers](https://eel.is/c++draft/deque.modifiers).
5. [Unordered-container requirements](https://eel.is/c++draft/unord.req): rehash stability.
6. [String requirements](https://eel.is/c++draft/string.require).
7. [Microsoft: inside STL strings](https://devblogs.microsoft.com/oldnewthing/20230803-00/?p=108532): comparative implementation layouts, not ABI guarantees.
