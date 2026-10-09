---
id: vulnerability-lifetime-stale-view-after-mutation
title: Stale slice, span, view, iterator, or interior pointer after mutation
kind: vulnerability
topics: [lifetime, views, iterators, slices, mutation, invalidation]
platforms: [cross-platform]
architectures: [any]
---

# Stale slice, span, view, iterator, or interior pointer after mutation

## Definition and violated invariant

A stale-view vulnerability occurs when a nonowning slice, span, string view, iterator, or interior pointer is used after an operation invalidates its storage address, element identity, range, or generation. The owner can remain live while a mutation reallocates storage, shifts or erases elements, compacts a buffer, changes logical length, or replaces the represented object.

Validity is type- and operation-specific. An iterator, element reference, numeric index, owner pointer, and past-the-end value can have different invalidation rules for the same mutation.

## Conditions that establish the issue

Identify the view's owner, acquisition point, represented range or element, mutation, applicable invalidation contract, and later consuming operation. Prove the mutation occurs between acquisition and use on a feasible path and invalidates that kind of view. Then establish whether the later access uses expired storage, a different element, or a range no longer authorized by current length.

For concurrent mutation, also prove the required synchronization is absent or inadequate. Lifetime validity alone does not make mutable contents race-free.

## Evidence that is not sufficient

A view type, `data()` call, iterator, insertion, append, erase, or changed size is not sufficient. Spare capacity may avoid relocation, some containers preserve references during particular operations, and code may reacquire the view after mutation.

An unchanged numeric address does not prove stable logical identity after elements shift. Conversely, a numeric index is not automatically a dangling pointer, although it can select the wrong element after mutation.

## Investigation sequence

Classify each saved value as owner, iterator, reference, raw pointer, view, endpoint, or index. Recover size and capacity before mutation, the exact mutation result, and documented invalidation rule. Follow copies of the saved value and locate the first later dereference or identity-sensitive use.

In a stripped binary, corroborate container identity from allocation, size/capacity fields, element stride, mutation behavior, and library calls. Do not impose a familiar standard-container layout without target evidence.

## Constructed source example

```cpp
void update(std::vector<record>& records, record extra)
{
    if (records.empty())
        return;
    record *selected = &records[0];
    records.push_back(extra);
    authorize(selected->owner);
}
```

If `push_back` reallocates, `selected` is invalidated before the field read. If capacity was sufficient, this particular relocation claim is false, although insertion rules and concurrent mutation still require review. A binary can show the saved element address used after a growth helper returns a new data base; prove that the old base was not reacquired or retained by another owner.

## Primitive and impact limits

The direct primitive is a stale read, write, or object-selection operation. It can produce a UAF after relocation, use the wrong shifted element, or cross the owner's new logical range. Impact depends on replacement contents, access direction, and security-sensitive use.

## Related knowledge and primary sources

`reference-native-container-invalidation` provides operation-specific container rules. This profile repeats the view-kind, mutation, and later-use proof needed independently.

Reviewed 2026-10-09 against C++ [`vector` capacity](https://eel.is/c++draft/vector.capacity), [`vector` modifiers](https://eel.is/c++draft/vector.modifiers), [`string_view`](https://eel.is/c++draft/string.view.template), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The example is constructed.
