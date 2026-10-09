---
id: vulnerability-resource-algorithmic-complexity-denial-of-service
title: Algorithmic-complexity denial of service
kind: vulnerability
topics: [resource-exhaustion, algorithmic-complexity, cpu, denial-of-service]
platforms: [cross-platform]
architectures: [any]
---

# Algorithmic-complexity denial of service

## Definition and violated invariant

This vulnerability occurs when attacker-controlled structure drives lookup, sort, match, parse or traversal into worst-case work that exceeds the authorized CPU budget. The violated invariant is that processing cost must remain bounded by enforced input and work limits under adversarial, not only typical, inputs.

The issue is the growth relation and reachable adversarial structure. A slow operation with a fixed upper bound can be a capacity problem without an algorithmic-complexity vulnerability.

## Conditions that establish the issue

Recover the algorithm, input dimension, adversarial property, cost recurrence or operation count, maximum accepted input and work budget. Show the attacker can construct the property after all normalization and that the resulting work blocks, delays or consumes a shared service resource.

Examples include collision-heavy hashing, catastrophic backtracking, quadratic duplicate checking and repeated graph traversal. State whether randomization, memoization or library implementation changes the worst case.

## Evidence that is not sufficient

A nested loop, recursion, regular expression, hash table or superlinear benchmark is not sufficient. Loop bounds may be independent, the input may be small, a linear-time engine may implement the expression, hash seeds may prevent chosen collisions, or a timeout may bound the security effect.

Do not infer exponential behavior from decompiled control flow alone. Identify repeated states or branching and how attacker input sustains them.

## Investigation sequence

Define the input measure and count comparisons, state visits, backtracks, allocations or other dominant operations. Trace normalization and parsing that determine the effective symbols and keys. Establish the accepted maximum, timeout, cancellation and whether work occupies a shared thread or isolated quota.

At binary level, identify loop nests, restart points, collision chains and recursive transitions. Recover whether the implementation memoizes states, uses randomized hashing or switches algorithms at thresholds. Compare the observed primitive with the deployed implementation rather than a similarly named library.

## Constructed example

This hypothetical duplicate check performs all-pairs comparison:

```c
for (size_t i = 0; i < count; ++i)
    for (size_t j = 0; j < i; ++j)
        if (equal(items[i], items[j])) reject();
```

For `count` distinct attacker-selected items, the function makes `count * (count - 1) / 2` equality checks. A vulnerability still requires a harmful accepted count, costly comparisons, reachable execution and lack of a tighter work limit.

## Primitive and impact limits

Report the input measure, asymptotic and concrete operation counts, resource occupied, timeout and competing workload. The direct effect is CPU or latency exhaustion. A crash or memory corruption requires a separate defect in resource handling or arithmetic.

## Related knowledge and primary sources

Regex backtracking and recursive graph profiles provide specialized cases. This profile supplies the general adversarial-cost proof.

Reviewed 2026-10-09 against [MITRE CWE-407](https://cwe.mitre.org/data/definitions/407.html), [MITRE CWE-1333](https://cwe.mitre.org/data/definitions/1333.html) and the C++ standard's explicit complexity requirements for [library clauses](https://eel.is/c++draft/structure.specifications). The example is constructed; library complexity guarantees apply only to the selected operation and implementation contract.
