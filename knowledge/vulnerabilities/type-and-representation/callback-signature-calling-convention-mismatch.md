---
id: vulnerability-type-callback-signature-calling-convention-mismatch
title: Function-pointer, callback-context, or calling-convention mismatch
kind: vulnerability
topics: [function-pointers, callbacks, calling-convention, abi, type-confusion]
platforms: [cross-platform]
architectures: [any]
---

# Function-pointer, callback-context, or calling-convention mismatch

## Definition and violated invariant

A callable-interface mismatch occurs when an indirect target is invoked with a function type, calling convention, hidden arguments, return convention, or context role incompatible with what the target consumes. Register and stack placement, argument widths, variadic state, receiver adjustment, preservation, stack cleanup, and result storage must agree at both sides.

A cast can silence a source diagnostic without adapting the machine interface. Thunks can legitimately translate interfaces, so recover the actual target set and any adapter before assigning the mismatch.

## Conditions that establish the issue

Recover the registration or table type, callback and context fields, selected target, caller-supplied machine arguments, callee-consumed arguments, and return handling. Prove a feasible target receives incompatible values or stack state and that the disagreement reaches a read, write, call, cleanup, or security decision.

For C++ member callbacks, include receiver adjustments and the target ABI's member-pointer representation. For variadic calls, apply default promotions and ABI-specific metadata.

## Evidence that is not sufficient

An indirect call, function-pointer cast, differing decompiler prototype, extra live register, or thunk is not sufficient. Unused arguments, compatible machine representations, private conventions, and adapters can be valid.

One call site cannot establish every target's signature when the target set is incomplete.

## Investigation sequence

Compare each feasible target with the caller at machine level: argument locations and widths, hidden result or receiver, stack alignment and cleanup, preserved registers, return channels, and semantic roles. Use multiple callers and callee entry uses to correct decompiler hypotheses.

Then follow the first mismapped value into its consumer. Separate language-level call incompatibility from the concrete built-binary effect.

## Constructed Windows x64 example

```c
typedef void (*callback)(void *context, const uint8_t *data, size_t length);
void handler(const uint8_t *data, size_t length);

register_callback((callback)handler, context);
```

When invoked under the registered type, Windows x64 places `context` in `RCX`, data in `RDX`, and length in `R8`. `handler` instead interprets `RCX` as data and `RDX` as a numeric length. A call fragment loading those three arguments then `call callback_target` is unsafe if the cast target is reached without an adapter; a thunk that discards context and shifts arguments would change the conclusion.

## Primitive and impact limits

The direct result can be invalid memory access, stack imbalance, corrupted return storage, wrong callback object, or unintended target behavior. Impact depends on mismapped values, ABI, target body, and mitigations.

## Related knowledge and primary sources

`reference-native-prototype-argument-evidence` defines interface recovery, and architecture ABI references define placement. This profile repeats the two-sided machine-interface proof locally.

Reviewed 2026-10-09 against C++ [function call compatibility](https://eel.is/c++draft/expr.call), the [Windows x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention), and [MITRE CWE-686](https://cwe.mitre.org/data/definitions/686.html). The example is constructed.
