---
id: vulnerability-type-object-type-confusion
title: Object type confusion from unchecked cast or stale type state
kind: vulnerability
topics: [type-confusion, casting, object-lifetime, dispatch, memory-safety]
platforms: [cross-platform]
architectures: [any]
---

# Object type confusion from unchecked cast or stale type state

## Definition and violated invariant

Object type confusion occurs when code accesses or dispatches through an object as a type whose layout, lifetime, or behavioral contract the actual object does not satisfy. Causes include unchecked downcasts, stale class state, incorrect registry metadata, reused storage, and producer/consumer disagreement about the constructed type.

The allocation's size and alignment do not prove that an object of the consumed type is live there. At binary level, identify the incompatible field or dispatch interpretation and its concrete effect rather than stopping at source-language undefined behavior.

## Conditions that establish the issue

Trace object construction and dynamic type, every cast or type-state update, lifetime transitions, and the consuming field access or indirect call. Prove a feasible path supplies an object of one type to a consumer requiring another without a successful runtime check or invariant that guarantees the relationship.

For C++ downcasts, account for base-subobject adjustment and the target ABI. A valid `static_cast` downcast still relies on the non-null source designating the appropriate base subobject of an actual target object.

## Evidence that is not sufficient

A decompiler cast, vtable load, adjusted `this` pointer, shared structure prefix, or same-sized allocation is not sufficient. Inheritance thunks, union variants, construction phases, or incomplete recovered types can explain those patterns.

An imported `dynamic_cast` helper is not proof every path checks the same object, and its failure must be handled before use.

## Investigation sequence

Build an object-state timeline from allocation and construction through registration, mutation, destruction, and access. Recover field offsets and dispatch tables for each candidate type independently. Locate the type check and bind it to the same immutable object generation used later.

At the consuming instruction, identify the expected field or callable slot, actual bytes supplied by the real type, and resulting read, write, or target. Preserve source-language and compiled-binary conclusions separately.

## Constructed C++ and assembly example

```cpp
struct base { uint32_t kind; };
struct callback_record : base { void (*callback)(base *); };

void invoke(base *object)
{
    callback_record *record = static_cast<callback_record *>(object);
    record->callback(object);
}
```

If `object` actually denotes only a live `base`, the downcast condition is not satisfied and the callback field is not part of that object. On a constructed 64-bit layout with the function pointer at offset eight, the binary can show `mov rax,[rcx+8]; call rax`. A real `callback_record` or a dominating kind/type guarantee would refute this path.

## Primitive and impact limits

The direct primitive can be an unintended field read/write or indirect dispatch through bytes with another meaning. Impact depends on object layout, value control, reachability, and control-flow defenses; a type error can instead fault or produce harmless data.

## Related knowledge and primary sources

`reference-native-type-confusion-object-validity` defines casting and live-object requirements, while ABI references cover subobject adjustment. This profile repeats the producer/consumer type proof locally.

Reviewed 2026-10-09 against C++ [`static_cast`](https://eel.is/c++draft/expr.static.cast), [`dynamic_cast`](https://eel.is/c++draft/expr.dynamic.cast), [object lifetime](https://eel.is/c++draft/basic.life), and [MITRE CWE-843](https://cwe.mitre.org/data/definitions/843.html). The layout, source, and assembly are constructed.
