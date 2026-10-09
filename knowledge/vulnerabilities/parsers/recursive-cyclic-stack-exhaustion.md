---
id: vulnerability-parser-recursive-cyclic-stack-exhaustion
title: Recursive nesting, cyclic graph, or stack-exhaustion parsing
kind: vulnerability
topics: [parsers, recursion, cycles, graphs, stack-exhaustion, resource-exhaustion]
platforms: [cross-platform]
architectures: [any]
---

# Recursive nesting, cyclic graph, or stack-exhaustion parsing

## Definition and violated invariant

A recursive or graph-parsing vulnerability occurs when attacker-controlled nesting, references or aliases cause unbounded or policy-exceeding call depth, work-stack growth, repeated traversal or nontermination. The parser must bound depth, unique objects, total edges or items, repeated visits and aggregate work according to the actual representation and availability requirement.

Depth, breadth, unique nodes and traversal paths are different measures. A depth limit does not bound exponential revisits of shared nodes, and cycle detection does not bound a very large acyclic graph.

## Conditions that establish the issue

Recover the recursive call cycle or explicit work stack, per-level live state, depth-check position, input-controlled child/reference count, identity model, visited or memoization key, cycle behavior, aggregate limits and failure cleanup. Prove a feasible input exceeds a security-relevant stack or work budget before rejection and affects service availability or state.

For memoization, verify the key includes every context that changes the result. Node identity alone can be wrong when permissions, path or mutable state affect processing.

## Evidence that is not sufficient

A recursive function, nested format, back-reference, alias, deep sample, stack-overflow exception or graph walk is not sufficient. Tail-call elimination, iterative parsing, early depth checks, cycle rejection or effective input limits may bound it.

The phrase stack overflow here means exhaustion from call depth, not an out-of-bounds stack-buffer write or automatic code-execution primitive.

## Investigation sequence

Annotate each descent with the input cursor or node identity, depth before the call, frame/work-item size, and limits checked before allocation or recursion. Separately count unique nodes, edges and revisits. Construct the smallest cycle or shared-subgraph pattern that violates progress under the actual algorithm.

Trace error unwinding and partially built object cleanup because rejection can still leak or retain accumulated state.

## Constructed late-depth-check example

```c
void visit(node *current, unsigned depth)
{
    for (node *child : current->children)
        visit(child, depth + 1);
    if (depth > maximum_depth)
        fail();
}
```

The check occurs after recursive descent, so it cannot prevent deeper frames from being created. If aliases can form a cycle and there is no visited-state rule, even a small graph can recurse indefinitely. The finding still requires attacker control over the graph and proof that another precheck or parser limit does not bound the descent.

## Primitive and impact limits

The direct result can be call-stack exhaustion, heap work-stack growth, excessive CPU, nontermination or failure cleanup pressure. This is primarily an availability primitive unless error handling or partial objects create a separate memory or logic defect.

## Related knowledge and primary sources

`reference-parser-algorithmic-work-graph-bounds`, `reference-parser-yaml-tags-construction-aliases`, and container references cover graph identity and limits. This profile repeats depth, node, edge, revisit and progress accounting locally.

Reviewed 2026-10-09 against CBOR [nesting and indefinite containers](https://www.rfc-editor.org/rfc/rfc8949.html), OpenType [composite glyph depth](https://learn.microsoft.com/en-us/typography/opentype/spec/maxp), and [MITRE CWE-674](https://cwe.mitre.org/data/definitions/674.html). The source is constructed.
