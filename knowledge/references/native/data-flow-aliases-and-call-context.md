---
id: reference-native-data-flow-alias-call-context
title: Value flow, aliases, memory versions and interprocedural call context
kind: reference
topics: [data-flow, taint, aliases, memory, ssa, call-graphs, globals]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Preserve value identity across memory and calls

## Input influence is not equality or unrestricted attacker control
Reviewed 2026-10-02. Value flow tracks the value reaching a use; taint tracking
tracks influence, potentially through transformations that change the value.
Keep the recovered transformation rather than replacing it with a taint label.
For example, CodeQL distinguishes value-preserving flow from taint flow,
which can include transformations of influenced data. Its global analysis
includes cross-function and object-property edges. [1] This describes that
analysis framework, not a proof that a binary has any particular flow.

Constructed eight-bit input x: y=x&15 remains input-dependent but can only be
0..15. Treating tainted y as an arbitrary integer invents values; treating the
mask as removing all influence loses possible index choices. A bound suitable
for a 16-entry index is not necessarily authorization to select every entry.
Keep the mathematical relation, width, range and security property separate.
A taint label alone proves neither an invalid operation nor a value-preserving
copy. Use instruction evidence for each transform before connecting source
influence to the sink's exact operand.

## A loaded value is not the address used to load it
Ghidra p-code LOAD separates memory-space identity, address offset and output
value; output size determines the access width. STORE separately identifies
address and stored value. Spaces can have non-byte addressable units. [2]

Constructed byte-addressed case: q=B+8; n=load32(q); allocate(n). Backward
tracing n requires definitions of four bytes at q, not merely the arithmetic
that produced q. Input control of n does not establish control of q, and input
control of q does not specify the bytes found there. Retain address flow and
content flow as separate edges. For each edge record memory space, normalized
byte range, endianness and lifetime; do not equate equal numeric offsets in
different address spaces or different loaded modules.

## Aliasing depends on access ranges, not just pointer equality
LLVM alias analysis distinguishes possible aliasing from known overlap and
same-start accesses; memory-location sizes matter. [3] These are results under
an analysis model, not dynamic proof that a write happened.

Constructed little-endian four-byte field at B+8 initially holds 0x11223344.
A two-byte store of 0xabcd at B+10 changes a later four-byte load at B+8 to
0xabcd3344. Unequal addresses did not make the accesses disjoint. Conversely,
an actual store confined to [B+12,B+14) does not overlap [B+8,B+12).
Preserve the unaffected bytes for partial overwrites. If q merely may alias
the field, retain both affected and unaffected possibilities; do not claim a
confirmed overwrite or discard the alias possibility without evidence.

## Memory-analysis joins are not concrete writes
LLVM MemorySSA is intraprocedural. Its MemoryPhi joins possible reaching
memory definitions, and liveOnEntry can represent memory defined before entry
or undefined memory. [4] Neither node is an executed store instruction.

Constructed investigation: a load of a caller-initialized field reaches
liveOnEntry in the callee. That is not by itself an uninitialized read; follow
caller initialization. A MemoryPhi merging two branch stores does not mean
both stores ran in sequence. Use predecessor conditions and alias refinement
to identify the bytes reaching the actual load. Do not treat MemorySSA alone
as whole-program alias resolution or as a lifetime guarantee for the loaded
pointer. Unknown initialization remains unknown until a producer is established.

## Call summaries need memory effects and path-specific outputs
LLVM Mod/Ref analysis conservatively describes whether an operation may read
or modify a location. [3] Ghidra raw p-code CALL implements a transfer hint,
not an entire high-level call contract; recovered parameters are later analysis. [2]

Constructed helper parse(input,&length) returns a status and writes length
only on success. A summary containing only the return register loses a memory
definition; a summary always assigning length invents initialization on failure.
Track status-dependent writes, pointer aliases, widths, ownership transfers,
escapes and exceptional exits. For an unresolved call, unknown effects are not
equivalent to either no effects or a proven arbitrary write. Retain the missing
contract and the specific effect needed for the candidate finding. A familiar
function name is not enough to install a trusted sanitizer summary.

## Match a callee return to its own invocation
Constructed ordinary synchronous calls: untrusted a enters identity(a), whose
result goes to logging; a separate identity(8) supplies a later copy length.
Merging all entries and exits of identity can invent an a-to-copy path. The
second invocation returns its own argument, not the first invocation's a.

Preserve call-site identity, argument binding and return continuation when
joining forward and backward slices. Recursion requires distinct activation
contexts; callbacks and shared-memory writes need explicit connecting edges.
This is a local counterexample to context-insensitive graph reasoning, not a
claim that the program has no other flow. If an indirect target set is incomplete,
state that gap rather than treating the currently discovered callees as complete.
ABI/prototype facts remain in reference-native-prototype-argument-evidence.

## Globals and heap fields can connect otherwise separate calls
Constructed sequence: set_length(input) writes a shared field; later use_length()
loads it for a copy. No return-value edge is needed for this flow. A callback
between checking that field and reloading it can also change which value is
consumed. Establish the actual writer, ordering, alias and object generation.

Conversely, a shared symbol name or reused address does not establish one live
storage object across modules or sessions. Distinguish a scalar snapshot from
a saved pointer to mutable storage: copying a pointer does not copy its pointee.
Use reference-concurrency-cancellation-completion-shutdown and the relevant
lifetime references for ownership; the existence of a data-flow edge does not
extend a resource lifetime. This section is investigative reasoning, not a
claim that every callback writes all reachable memory.

## Source and representation limits
1. [CodeQL data-flow concepts](https://codeql.github.com/docs/writing-codeql-queries/about-data-flow-analysis/): local/global flow, taint and alias challenges; reviewed 2026-10-02.
2. [Ghidra p-code reference](https://ghidra.re/ghidra_docs/languages/html/pcodedescription.html): LOAD, STORE and CALL, raw versus analyzed operations; reviewed 2026-10-02.
3. [LLVM alias analysis](https://llvm.org/docs/AliasAnalysis.html): location sizes, alias categories and Mod/Ref; reviewed 2026-10-02.
4. [LLVM MemorySSA](https://llvm.org/docs/MemorySSA.html): intraprocedural scope, MemoryPhi and liveOnEntry; reviewed 2026-10-02.

These are rolling primary tool descriptions. Their analysis nodes are not CPU
instructions. Examples are constructed, not observations of a target binary.
Workflow: playbook-re-sensitive-data-flow. Path conditions:
reference-native-path-feasibility-guards.
