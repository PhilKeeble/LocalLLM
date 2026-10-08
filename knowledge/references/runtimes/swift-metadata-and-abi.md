---
id: reference-swift-metadata-abi
title: Swift metadata, value and protocol witnesses, resilience and calling conventions
kind: reference
topics: [swift, type-metadata, witness-tables, generics, abi, mangling, type-recovery]
platforms: [macos, ios, linux, windows]
architectures: [x64, arm64]
---
# Swift metadata and ABI evidence

## ABI stability does not freeze every Swift type's private layout

Swift 5 introduced stable runtime ABI on Apple platforms. Module stability concerns
compiler consumption of module interfaces; library evolution permits compatible
changes to separately distributed libraries. These are different contracts.
Library evolution is opt-in; @frozen exposes additional struct/enum representation
details and restricts compatible changes. [1]

Do not use an Apple runtime compatibility statement as a universal layout promise
for every Swift platform, library or compiler-private artifact. A .swiftinterface
is build-interface evidence, not a dump of live instance memory. At a resilient
library boundary, recover field-access and layout machinery rather than imposing
the field offsets observed in a different build.

## Type metadata and value witnesses describe how to operate on a value

Swift type metadata describes a runtime type. Its value witness table supplies
operations such as copying and destroying values, together with size, alignment
and stride information. Generic type metadata can carry argument-type metadata
and protocol-conformance witnesses. [2]

A call through a value witness can be ordinary value management, not an
application command dispatch. Separate the type description from the address of
an instance. Follow which concrete type supplies the operation before assigning
a buffer size or destructor to a type-erased value.

## Protocol existentials can contain inline values or owned side allocations

A Swift existential represents a value through an abstract type such as a
protocol or Any. The documented opaque container has a value buffer, type
metadata and required protocol witnesses; size and alignment determine whether
the value fits inline or needs side storage. Class-constrained existentials have
a different representation. [3]

A protocol witness table describes a conformance, unlike a value witness table's
copy/destroy/layout role. Follow the relevant witness and actual contained type
to recover a protocol call. Do not assume every existential has one fixed size
or that its first word is an object pointer.

## Swift size, stride and enum tags are not C structure assumptions

In the documented Swift layout model, size is the occupied value extent and
stride includes spacing needed between consecutive values; tail padding can be
reused inside an enclosing aggregate. Enum representations can use spare bits
or extra inhabitants (bit patterns unused by the payload type), rather than a
separate integer tag at a universal offset. [3]

Recover array stepping independently from a single value's copied byte count.
For an enum/Optional branch, identify the actual case discriminator before
interpreting a pointer test as an application validation check. Resilience and
the concrete target representation still constrain any inferred offset.

## Partially initialized metadata is not a trustworthy layout snapshot

Swift metadata initialization distinguishes abstract, layout-complete and complete
states. Layout-complete metadata has meaningful value witnesses; a raw field
inspection does not establish that state. Initialization synchronization occurs
at a higher level, and a partially initialized witness table can contain a
meaningless size. The ABI describes state-aware metadata access/checking. [2]

During runtime initialization analysis, recover the returned state and required
state rather than trusting a non-null metadata pointer. This is not evidence that
ordinary fully initialized generic calls routinely lack valid metadata.

## Swift native calls, Objective-C thunks and C calls need separate prototypes

LLVM provides Swift-specific calling conventions. A native Swift address is not
automatically callable with a superficially similar C prototype. [4] For the
documented macOS/iOS Swift convention, special roles include:

| Role | x86-64 | ARM64 |
| --- | --- | --- |
| self/context | r13 | x20 |
| Error return | r12 | x21 |
| Async context | r14 | x22 |

These are convention roles, not proof that every function uses all three. [5]
An interoperability thunk is adapter code: recover the convention on each side.
Look for indirect results and metadata/context inputs before counting apparent
application arguments. Do not apply this Apple-specific register table unchanged
to other platforms or mistake async context for an ordinary source parameter.

## Swift mangled metadata names can contain non-text symbolic references

Compiler-emitted Swift metadata names may include symbolic references whose byte
payload contains NUL. Treating every name as a plain null-terminated text string
can truncate it. The mangling specification requires interpreters of potentially
uncontrolled input to reject symbolic references, rather than dereference them
as trusted compiler metadata. [6]

When analyzing a malformed binary, bound the name and referenced target within
the relevant image mappings. A demangled name suggests a type or function role;
it does not establish reachability, input validation or malicious intent.

## Async continuation state is different from an ordinary call's arguments

Swift's task ABI source distinguishes a task's resume function from its resume
context. A continuation represents suspended program state; checked-continuation
APIs require exactly one resumption, and never resuming can leave a task suspended.
[7][8]

Recover the actual resume edge, saved values, context ownership and completion
path before counting apparent callback arguments or declaring code unreachable.
An await is a potential suspension, not proof that the task always suspends.
Task helpers do not supply an application authorization decision. Private frame
offsets, executor defaults and one-to-one emitted helper sequences are not assumed.

## Primary sources and scope

Reviewed 2026-10-02. Swift project main-branch ABI documentation is implementation
guidance; match detailed encodings to the target before using offsets. Language
and ownership evidence: `reference-swift-ownership-native-boundaries`.

1. [Swift: Library Evolution](https://www.swift.org/blog/library-evolution/): ABI/module/library distinctions and @frozen (2020).
2. [Swift: Type Metadata](https://raw.githubusercontent.com/swiftlang/swift/main/docs/ABI/TypeMetadata.rst): value witnesses, generic metadata and completion states.
3. [Swift: Type Layout](https://raw.githubusercontent.com/swiftlang/swift/main/docs/ABI/TypeLayout.rst): size/stride, enums and existential variants.
4. [LLVM Language Reference](https://llvm.org/docs/LangRef.html): swiftcc/swifttailcc.
5. [Swift: Calling Convention Summary](https://raw.githubusercontent.com/swiftlang/swift/main/docs/ABI/CallingConventionSummary.rst): macOS/iOS special register roles.
6. [Swift: Mangling](https://raw.githubusercontent.com/swiftlang/swift/main/docs/ABI/Mangling.rst): embedded symbolic references and untrusted-input restriction.
7. [Swift Task.h](https://github.com/swiftlang/swift/blob/main/include/swift/ABI/Task.h): ResumeTask/ResumeContext roles, inspected 2026-10-08; no offsets adopted.
8. [Swift CheckedContinuation](https://github.com/swiftlang/swift/blob/main/stdlib/public/Concurrency/CheckedContinuation.swift): opaque state and resumption contract; [SE-0296](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0296-async-await.md): potential suspension; inspected 2026-10-08. Earlier source review retained.
