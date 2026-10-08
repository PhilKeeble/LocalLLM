---
id: reference-jit-guards-specialization
title: JIT speculation, shape guards, inline caches and representation assumptions
kind: reference
topics: [jit, speculative-optimization, guards, inline-cache, type-confusion, v8]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# JIT guards and specialization evidence

## Speculative optimization relies on assumptions that must remain valid

A just-in-time compiler generates native code during execution. V8's Maglev
description shows specialization using types and object shapes observed by
earlier execution. A shape check can guard a subsequent fixed-offset field
load. [1] This is compiler speculation about program behavior, not evidence
of processor transient execution or a Spectre vulnerability.

For an apparent unsafe fast path, name its assumption, the guard or dependency
maintaining it, and the operation that consumes it. Profile history is evidence
used to choose an optimization, not proof that future inputs have the same type.
A correct guard failure can be normal execution rather than an exploitable error.

## A missing nearby check may be covered by a guard or runtime dependency

Maglev can reuse an already established shape fact. It can also register a runtime
dependency instead of emitting repeated checks; mutation invalidates dependent
optimized code. Its documentation distinguishes stable dependencies from facts
invalidated by intervening effects. [1]

Investigative consequence: look backward through every incoming path and forward
through intervening calls, stores and callbacks. A dominating guard is one that
every path to the use passes through. Ask whether the guarded object/value is
still the one used. Absence of a second comparison is insufficient evidence of a
missing check; a finding needs a feasible invalidating change with no effective
recheck, dependency invalidation or fallback before use.

## V8 Maps describe object shape, not an immutable source-language class

V8 HiddenClasses, internally Maps, describe object structure and support optimized
property access. Named properties can live inside an object, in a separate fast
property store or in dictionary storage; indexed elements are separate. [2]

Recover the storage mode before treating a constant displacement as a declared
field offset. Objects with the same printed constructor name need not have the
same shape. Map equality is evidence about an engine representation, not caller
identity, authorization or the complete semantics of a source-language class.
Do not transplant private Map offsets from another build.

## Inline caches remember observed cases, not all permitted future values

V8 describes inline caches (ICs) as recording cases seen at operations such as
element access. A monomorphic operation has observed one case; polymorphic code
handles multiple observed cases with corresponding checks. [3]

An IC miss means the cached case did not handle this input; follow the miss path
before claiming failure. The path may update feedback, invoke generic runtime
logic or trigger another code tier. Monomorphic feedback is not a declaration
that callers cannot supply another shape. Recover the receiver, operation and
cache site together rather than labeling all similarly named calls identical.

## Field representation and array elements kind are different assumptions

V8 tracks named-field representations separately from indexed-element kinds.
Representations distinguish small integers, doubles, heap objects and general
tagged values. Element backing stores likewise distinguish tagged elements from
unboxed doubles and packed from holey arrays. [4] Tagged storage carries type
information with the value; unboxed storage holds the raw numeric payload.
Packed elements have no missing indices; holey storage supports such gaps.

For a suspected type-confused load/store, identify the selected storage, element
width, tag handling and representation transition. A JavaScript numeric value
does not imply one universal heap format. Conversely, integer machine arithmetic
does not by itself prove a compiler bug: recover conversions, range assumptions,
overflow handling and the language-visible result.

## A JavaScript array hole is an absent property, not an undefined value

V8's holey-array paths account for missing indexed properties and prototype-chain
lookup. Reading beyond an ordinary array's length can also require prototype
lookup rather than a native out-of-bounds read. [3]

Distinguish missing elements, explicitly stored undefined, a source-level index
beyond length, and a physical backing-store overread. Only the last is directly
a native memory-safety claim. Do not generalize ordinary-array lookup behavior
to TypedArrays or Wasm linear memory. A prototype change or accessor may be
relevant to the semantic path even when the physical backing store is unchanged.

## Primary sources and scope

Reviewed 2026-10-02. V8 is an implementation example, not a contract for every
JIT. Historical descriptions establish mechanisms, not current private layouts,
tiering thresholds or an assertion that every optimization remains unchanged.
Workflow: playbook-re-jit-generated-code.

1. [V8 Maglev](https://v8.dev/blog/maglev), 2023-12-05: feedback, shape checks and dependencies.
2. [V8 fast properties](https://v8.dev/blog/fast-properties), 2017-08-30: HiddenClasses and property storage.
3. [V8 elements kinds](https://v8.dev/blog/elements-kinds): IC cases, holes and prototype lookup; includes a 2025 update, so historical one-way-transition wording is not a universal rule.
4. [V8 field representations and elements kinds](https://chromium.googlesource.com/v8/v8.git/+/refs/heads/main/docs/objects/fields-and-elements.md): living implementation documentation; no fixed bit layout imported.
