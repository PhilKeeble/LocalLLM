---
id: vulnerability-lifetime-use-after-scope-borrowed-storage
title: Use after scope of temporary, borrowed, mapped, or arena storage
kind: vulnerability
topics: [lifetime, borrowed-storage, temporaries, mappings, arenas]
platforms: [cross-platform]
architectures: [any]
---

# Use after scope of temporary, borrowed, mapped, or arena storage

## Definition and violated invariant

Use after scope occurs when a nonowning pointer, view, slice, iterator, mapping pointer, or arena object is used after the lifetime boundary supplied by its owner or API. The boundary can be function scope, temporary destruction, next API call, mapping removal, arena reset, buffer return, transaction end, or callback duration.

Storage remaining allocated does not preserve the logical object or borrowed contents. Conversely, closing a backing descriptor need not invalidate an independently living mapping; apply the selected platform contract.

## Conditions that establish the issue

Recover owner, borrow acquisition, documented validity interval, invalidating operation, aliases, synchronization, and later access. Prove the borrow crosses its actual boundary and is not replaced, copied, retained, or reacquired before use.

For arenas and pools, identify generation and reset/return behavior. Same-address reuse can select a different object without a conventional free.

## Evidence that is not sufficient

A view type, mapping, arena allocation, temporary expression, or missing explicit free is not sufficient. The borrow may be confined to the valid scope, the owner may remain alive, or the API may return stable storage.

Do not transfer one library's next-call or iterator rule to another implementation without provenance.

## Investigation sequence

Create an owner/borrow ledger with the exact invalidation event. Trace all exits, resets, unmaps, pool returns, and callbacks between acquisition and use. At the consuming instruction, bind the address to its current generation and object.

Inspect wrappers for hidden copies or reference-count increments. In stripped code, infer invalidation from allocator, mapping, and mutation evidence before assigning a high-level view type.

## Constructed example

```c
const char *saved;

void remember_name(struct arena *arena, const char *input)
{
    saved = arena_copy(arena, input);
}

void reset_and_use(struct arena *arena)
{
    arena_reset(arena);
    log_name(saved);
}
```

The use is stale if `arena_reset` ends the copied object's lifetime and `log_name` dereferences `saved`. A reset that preserves live objects by contract or a copied `saved` value in separate owned storage would change the conclusion.

## Primitive and impact limits

The direct primitive is a read, write, or call through a borrow outside its validity interval. Impact requires current contents, access direction, observability, and attacker influence; a stale view may simply fault.

## Related knowledge and primary sources

`reference-native-resource-lifetimes-results` distinguishes mappings and descriptors, while `reference-native-ownership-release-dangling` covers borrowed storage. This profile repeats owner and invalidation proof locally.

Reviewed 2026-10-09 against C++ [object lifetime](https://eel.is/c++draft/basic.life), C++ [`string_view`](https://eel.is/c++draft/string.view.template), Linux [`mmap` and `munmap`](https://man7.org/linux/man-pages/man2/munmap.2.html), and [MITRE CWE-416](https://cwe.mitre.org/data/definitions/416.html). The arena example is constructed and does not assert one universal arena API.
