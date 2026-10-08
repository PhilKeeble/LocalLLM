---
id: reference-parser-algorithmic-work-graph-bounds
title: Algorithmic complexity, hash collisions, graph traversal and progress bounds
kind: reference
topics: [parsers, algorithmic-complexity, hash-collisions, recursion, graphs, livelock, resource-exhaustion]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Algorithmic work and graph bounds

## Worst-case cost is distinct from malformed input or memory corruption

CWE-407 describes attacker-triggerable inefficient worst-case algorithmic behavior
that harms performance. [1] Memory-safe, structurally valid processing can still
exhaust an availability budget; a slow operation alone does not establish that
an attacker can select the necessary inputs or affect another user's service.

Analytical convention: name each independent size variable and counted operation.
O(N) means an asymptotic upper bound proportional to N, not a duration; O(N*N)
describes a quadratic upper bound, not proof that every input takes that much work.
For a finding, recover a reachable costly path, effective limits, scheduling and
the unavailable service/resource. Distinguish input-sensitive growth from fixed
but expensive work, leaked resources and requests merely queued for I/O.

## Repeated prefix scanning and exact-size copying can accumulate quadratic work

Constructed model: on each one-byte append, a wrapper scans the complete prefix
of lengths 1,2,...,N. It examines N*(N+1)/2 bytes in total. Reallocating and copying
each growing prefix also has quadratic total copying if every append moves all
prior bytes. The conclusion depends on those operations occurring, not on a realloc
name alone; spare capacity or in-place growth changes the cost.

In a binary, recover the scan's start/end and which offsets persist between calls.
Nested loops are not sufficient evidence: an inner cursor that advances across
the input once can keep total work linear. Conversely, multiple top-level calls
can repeatedly revisit the same region without any nested loop in one function.
Compiler unrolling and vectorization also change visible loop shape; use
reference-native-compiler-transformations.

## Hash-table average constant lookup is not a worst-case guarantee

The C++ unordered-container requirements give find average constant complexity
but worst-case linear complexity in container size. [2] PEP 456 documents keyed
hashing as a response to hash-collision denial of service for CPython strings and
bytes; its historical algorithm choices are not universal runtime guarantees. [3]

Investigative model: in a chained table, many keys selecting one bucket can make
lookup traverse many entries. Confirm the actual hash, seed source, bucket/probe
algorithm, equality function, resize policy and attacker-selectable key domain.
A seed literal does not by itself prove feasible collisions. A keyed string hash
does not describe arbitrary user-defined key types. Count hashing/comparison cost
as well as probes: long keys or expensive callbacks can dominate the operation.

## Depth, unique graph nodes and repeated visits measure different costs

Constructed graph model: each non-leaf references the next shared child twice, across
D levels. There are only D+1 unique nodes, but a traversal that re-expands both
references at every visit has 2^D leaf visits. This model requires no cycle.
A cycle creates a different nontermination risk if traversal never detects it.

Investigative inference: recover whether the consumer walks identity-preserving
references, copies subtrees or memoizes results. A recursion-depth limit does not
bound breadth or repeated visits; a unique-node limit does not necessarily bound
all path-sensitive work. Memoization needs a valid key: node identity alone is
insufficient when results depend on path, permission context or mutable state.
See reference-parser-yaml-tags-construction-aliases for a concrete shared-object
representation. Do not infer this graph behavior from textual nesting alone.

## Recursive stack exhaustion and iterative heap growth are different failures

Constructed model: one recursive call per nesting level with positive per-call
stack cost consumes more stack as depth grows. Tail-call elimination, explicit
work stacks and parser-specific limits can change that model. An iterative parser
avoids that particular call-stack growth but can still accumulate heap work items.

Recover the actual call cycle, live frame/work-item size and where depth is checked
relative to descent or allocation. A counter after recursion is not a prior guard.
Bound sibling counts and outstanding work separately from depth. Distinguish an
evidenced stack-limit failure from an out-of-bounds stack write; neither the name
stack overflow nor a deep call graph alone establishes exploitable corruption.

## Big-integer conversion can be expensive before a value-range check

CPython documents non-linear conversion between large binary integers and decimal
or other non-power-of-two text bases. Its configurable digit limit rejects excessive
affected conversions with ValueError; power-of-two conversions and int.from_bytes
are not covered by that particular limit. [4]

Investigative inference: a range check after conversion does not bound work already
spent parsing digits. Follow input-length checks, the selected numeric type/base,
effective conversion limit and error handling. Output conversion matters too:
formatting a large integer for a log or error response can fail or add work after
the main operation. Do not transfer CPython's rule to fixed-width strtol-like
functions, another language's bignum library or all numeric conversions.

## Retry and resynchronization loops need an evidenced progress measure

Constructed parser model: each iteration must consume input, reduce a bounded work
queue, produce bounded output, change to a state that enables progress, or return
to await new input. An error branch that retries the same operation with identical
state and no remaining retry bound may make no progress. Zero consumed bytes alone
is not proof: a legitimate state transition or output flush can be useful work.

For recovered loops, track cursor, state, counters, queue contents and dependencies
across the back edge. A retry bound can still multiply expensive work; checked
arithmetic and termination do not establish an affordable maximum. Distinguish
livelock, where execution continues without useful progress, from blocking on a
dependency. Use reference-concurrency-locks-waits-reentrancy for wait graphs.

## Sources and limits

Reviewed 2026-10-02. Complexity equations and graph/loop examples are constructed
analytical models, not claims about every parser. API facts are scoped below.

1. [CWE-407](https://cwe.mitre.org/data/definitions/407.html): inefficient algorithmic complexity, CWE 4.20.
2. [C++ living draft unordered-container requirements](https://eel.is/c++draft/unord.req.general): find complexity.
3. [PEP 456](https://peps.python.org/pep-0456/): CPython 3.4 hashing design and collision-DoS rationale.
4. [Python 3.14.8 integer-string conversion limits](https://docs.python.org/3/library/stdtypes.html#integer-string-conversion-length-limitation).

Workflow: playbook-re-algorithmic-resource-boundary.
