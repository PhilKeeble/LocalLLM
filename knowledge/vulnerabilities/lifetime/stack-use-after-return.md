---
id: vulnerability-lifetime-stack-use-after-return
title: Stack use after return and escaped local address
kind: vulnerability
topics: [use-after-return, stack, lifetime, callbacks, closures]
platforms: [cross-platform]
architectures: [any]
---

# Stack use after return and escaped local address

## Definition and violated invariant

Stack use after return occurs when an address or reference to automatic storage escapes beyond that object's lifetime and is later dereferenced. A captured-by-reference local, callback context, deferred work item, returned pointer, or retained span can outlive the invocation even when the stack bytes remain mapped.

The relevant boundary is object lifetime, not whether the same stack address is still readable. Later calls, interrupts, exceptions, or stack reuse can replace its contents.

## Conditions that establish the issue

Identify the automatic object, acquisition of its address, escape destination, function exit or lifetime end, and later use. Prove the consumer is not completed synchronously before return and that no copy or heap-promoted closure owns equivalent state.

For compiler-generated closures and coroutines, recover whether captured state resides in a heap frame, runtime object, or the original stack. Source syntax alone does not establish placement.

## Evidence that is not sufficient

Taking a local address, passing stack storage to a callee, or seeing a callback registration is not sufficient. The callee may consume it synchronously, copy it, or retain an owning transformed representation.

An unchanged value during one run does not extend lifetime or prove safe reuse.

## Investigation sequence

Track the pointer from stack-coordinate formation through return, queueing, storage, and callback entry. Recover frame unwind and every exit path. Distinguish a pointer to caller-owned output that remains live from a callee local.

At the later use, calculate the original stack range and determine what now occupies it. Keep the lifetime violation separate from the concrete disclosure, write, or indirect-call effect.

## Constructed example

```c
void schedule_reply(void)
{
    struct reply_context context = { .status = 1 };
    queue_callback(send_reply, &context);
}
```

If `queue_callback` can invoke `send_reply` after `schedule_reply` returns without copying `context`, the callback receives an expired pointer. A synchronous invocation or documented copy refutes the example. In a binary, a context address derived from the old frame followed by a later field load supports the chain only after callback timing is established.

## Primitive and impact limits

The direct primitive is access through an expired stack object. Results range from stale-data disclosure and incorrect state to a controlled indirect call if stack reuse and timing permit; return-address overwrite is not implied.

## Related knowledge and primary sources

`reference-native-ownership-release-dangling` supplies general lifetime rules, and runtime-specific callback references define whether closures copy or borrow captures.

Reviewed 2026-10-09 against C++ [object lifetime](https://eel.is/c++draft/basic.life), C++ [lambda capture lifetime](https://eel.is/c++draft/expr.prim.lambda.capture), and [MITRE CWE-562](https://cwe.mitre.org/data/definitions/562.html). The example is constructed.
