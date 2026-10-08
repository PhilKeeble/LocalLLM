---
id: reference-native-path-feasibility-guards
title: Feasible paths, dominating guards, correlated joins and solver evidence
kind: reference
topics: [control-flow, path-feasibility, guards, dominance, symbolic-execution, constraints]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Distinguish a graph path from a feasible violating execution

## Dominating a sink does not imply the accepted branch protects it
Reviewed 2026-10-02. A control-flow graph (CFG) records blocks and possible transfers
between them. Ordinary CFG dominance means every entry-to-B path passes
A; LLVM's MLIR documentation states this for SSACFG regions. [1] It is a graph
property, not a statement about which branch outcome or input contract holds.

Constructed CFG: a length check branches to either logging or a no-op; both
branches join at copy. The check block dominates copy, but an excessive length
can still reach it through logging. Credit a protective check only after showing
that the rejecting branch cannot reach the operation under the relevant state.
Also verify compared value, width, unit, object capacity and intervening writes.
A nearby check on one object does not validate another object's buffer. Missing
exceptional or indirect edges limit any dominance conclusion about the binary.

## Path predicates must refer to the same value version
Constructed unchanged integer n: a path requiring n<8 and n>=8 is infeasible.
If n is reloaded from mutable storage between the tests, constraints on n0 and
n1 are not contradictory without evidence that n0==n1. A call or callback is
not proof that the value changed, but it can require checking that possibility.

Keep predicates with instruction coordinates and reaching definitions. For a
state machine, state==OPEN followed by state==CLOSED needs either an intervening
transition or a rejected path hypothesis. Do not merge histories from different
requests or object generations merely because the decompiler reused one name.
Satisfiability is relative to all encoded formulas, not individual tests viewed
in isolation; see the solver-result distinction below. [4]

## Joined values retain predecessor correlation
In LLVM SSA, phi selects the incoming value associated with the predecessor
that actually executed. [2] It is not an independent choice of any listed value
at every use. Treat this as IR semantics, not a literal machine instruction.

Constructed branch A sets (length,capacity)=(4,8); branch B sets (16,32).
The joined pairs are (4,8) or (16,32), not the invented pair (16,8). A range-only
analysis combining maximum length with minimum capacity can report a spurious
overflow here. Keep the shared branch predicate or equivalent relation. This
refutes that pair combination only; independently changed capacity, wrong
allocation identity or a later length update requires a new analysis. Do not
erase path correlations solely because a decompiler prints separate variables.

## Loop visits and mutable state need distinct instances
Constructed loop: i starts at 0; while i<4, an operation uses i and then i is
incremented. Body values are 0,1,2,3; normal exit sees 4. Conditions i<4 in the
body and i>=4 on exit do not contradict each other across those visits.

Label iteration-specific values or establish an invariant and update relation.
A search exploring only two iterations does not refute a path that needs three.
Likewise, a path requiring a flag to be both clear and set may be feasible if
the body changes it, but a transition must be evidenced. Preserve wrapping
counter width, exit tests, exceptional exits and environment assumptions. This
is a constructed state model, not a guarantee that an unknown loop terminates
or that its recovered induction variable has the source type suggested by a name.

## Machine-width constraints can change feasibility
Z3 bit-vectors support fixed widths and distinct signed/unsigned operations;
integer-to-bit-vector conversion is modulo 2^width. [3] Mathematical integers
and machine-width arithmetic are not interchangeable models.

Constructed eight-bit unsigned addition: n=255 gives (n+1) mod 256=0, so the
test wrapped_result<=16 succeeds. Under unbounded integer arithmetic, 256<=16
fails. Omitting truncation can therefore remove a feasible binary branch.
Conversely, 0xff is below 16 in signed eight-bit comparison (-1<16), but not
unsigned comparison (255<16). Recover emitted widths, extensions and branch
conditions; do not infer signedness from a guessed decompiler type. LLVM
poison/source UB rules require their own representation, not blanket machine wrap.

## Exceptional continuations do not receive normal call results
LLVM invoke distinguishes normal and exceptional successors; its return value
is defined only on the normal edge. [2] A callee that unwinds supplies no normal
return value through that invocation. Binary EH requires the actual target ABI.

Constructed sequence: acquire() returns a pointer on success but can throw.
Using that success pointer as initialized on the throw edge invents a definition.
Conversely, excluding the unwind edge can hide cleanup or ownership problems.
Recover metadata-supported handlers, partial construction state and each exit's
resource obligations. Do not infer that an exception path runs every subsequent
normal-path release. Use reference-native-cpp-lifecycle-unwind for C++ cleanup
facts; unusual nonlocal transfers need their own contract, not an assumed ret.

## SAT, UNSAT and unknown answer a modeled question
Z3 check-sat reports satisfiable, unsatisfiable or unknown; a model after SAT
satisfies the assertions supplied to that solver. [4] It is not an observed
execution or confirmation that the assertions faithfully describe the binary.

Investigative consequence: SAT for a candidate path needs review of omitted
guards, ABI effects, memory identity, external inputs and environmental state.
UNSAT refutes the encoded constraints; it does not prove every path safe. Unknown
or a timeout is not UNSAT. Record the exact property being queried: satisfiable
reachability to a copy does not establish an out-of-bounds copy unless the query
also requires a violated bound for the same live object and length. Preserve
constraints and assumptions with a generated input so it can be checked against
instructions or an authorized bounded runtime observation.

## Concretized external behavior limits symbolic coverage
KLEE's documented all-external-call policy concretizes symbolic arguments for
external calls. Its entry-point and environment options also select the modeled
execution context. [5] This is tool configuration evidence, not an instruction
to run a specimen or a claim about every symbolic-execution engine.

Constructed investigation: an external decoder is evaluated for one concrete
mode while other input fields remain symbolic. No failure in that run does not
cover every decoder mode. A stub that always returns success can equally invent
paths unavailable with the real failure behavior. Record concrete substitutions,
unmodeled calls, search bounds, solver failures and excluded states. A larger
number of explored paths does not repair an incorrect boundary model. Retain
candidate versus reproduced behavior explicitly in the evidence packet.

## Recorded path coverage is neither exhaustive feasibility nor a behavior verdict

An observed execution supports that path under its recorded inputs, state and
interventions. A missing hit does not establish an impossible path; an unresolved
indirect edge or uncollected thread can also explain it. Separate collection
coverage from the satisfiability of recovered path constraints. Use
reference-validation-coverage-reachability for metric and negative-evidence limits.

For malware analysis, establish the conditions opening command dispatch and the
handler's actual effects. A satisfiable model or forced call can expose capability
without proving natural activation. Conversely, a failed handshake in a captured
run does not refute a statically supported path under other feasible peer state.
Keep those conditions with the claim instead of labeling the whole binary from
one taken or untaken branch.

## Sources and limits
1. [MLIR dominance](https://mlir.llvm.org/doxygen/classmlir_1_1DominanceInfo.html): SSACFG dominance definition; reviewed 2026-10-02. Other MLIR region kinds are not assumed to have this CFG interpretation.
2. [LLVM language reference](https://llvm.org/docs/LangRef.html): phi predecessor selection and invoke normal-edge result; reviewed 2026-10-02.
3. [Z3 bit-vectors](https://microsoft.github.io/z3guide/docs/theories/Bitvectors/): widths, signed predicates and modulo conversion; reviewed 2026-10-02.
4. [Z3 basic commands](https://microsoft.github.io/z3guide/docs/logic/basiccommands/): asserted formulas, check-sat and models; reviewed 2026-10-02.
5. [KLEE options](https://klee-se.org/docs/options/): external-call policy, entry point and environment; reviewed 2026-10-02.

Rolling primary documentation; no tool run or target reproduction is claimed.
Examples are constructed. Workflow: playbook-re-sensitive-data-flow.
