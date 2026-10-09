---
id: vulnerability-failure-fail-open-default-sentinel-state
title: Fail-open, unknown, default or sentinel state grants authority
kind: vulnerability
topics: [fail-open, authorization, authentication, sentinel, default-state, state-machine]
platforms: [cross-platform]
architectures: [any]
---

# Fail-open, unknown, default or sentinel state grants authority

## Definition and violated invariant

This vulnerability occurs when failure, timeout, unavailable policy, unknown enum/discriminator, default branch, sentinel, or out-of-range state is interpreted as authenticated, authorized, trusted, initialized, or successfully complete. The invariant is that a security decision may grant authority only from an affirmative result produced under the required policy; every other state must have explicit bounded semantics.

Fail-open behavior can be an intentional availability tradeoff. It is a vulnerability when it contradicts the security policy for the actor, operation, object, and failure condition in scope.

## Conditions that establish the issue

Enumerate the complete result domain and state transitions, including dependency failure, cache miss, timeout, parse error, unsupported version, default enum value, integer sentinel, and newly introduced values. Trace each into the final branch and protected effect. Prove a nonaffirmative or invalid state selects an allow/trust/success path and that the initiating actor benefits.

For cached decisions, establish expiry, key tuple, invalidation, and whether an error reuses an earlier decision for the same actor and object. For distributed policy, identify which component owns the authoritative result.

## Evidence that is not sufficient

A `default` case, catch-all exception, retry, cached result, or Boolean conversion is not sufficient. The default may deny, the exception may abort before an effect, the unknown value may be unreachable after validation, or the operation may be safe without the dependency. A failure response visible to the caller does not prove prior effects were rolled back or granted.

## Investigation sequence

Construct a truth table from raw return/status/state through conversions and branches to the operation. Include values outside source-level enums when bytes cross FFI, IPC, storage, or parser boundaries. Check timeout and cancellation races and all equivalent entry points. Determine whether a logged denial differs from the identity used at the actual resource access.

At binary level, inspect signed/unsigned comparisons, default jump-table targets, zero initialization, and error blocks that join success continuations. Preserve the source/API meaning of each constant instead of naming zero universally as false or success.

## Constructed example

```c
enum decision { DENY = 0, ALLOW = 1, UNKNOWN = 2 };
enum decision d = query_policy(request);
if (d != DENY)
    perform_sensitive_action();
```

The predicate grants both `ALLOW` and `UNKNOWN`. It is vulnerable only when `UNKNOWN` is reachable for a less-trusted request and policy requires denial or isolation in that state. Replacing `query_policy` with a total local policy or proving `UNKNOWN` cannot reach this branch would change the conclusion.

## Primary sources and scope

Reviewed 2026-10-09 against NIST SP 800-53 Rev. 5 controls [AC-3 Access Enforcement and SC-24 Fail in Known State](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), the C++ working draft [switch semantics](https://eel.is/c++draft/stmt.switch), and MITRE [CWE-754](https://cwe.mitre.org/data/definitions/754.html) as taxonomy. Product policy determines whether availability fallback is permitted; this profile does not impose one universal failure policy.
