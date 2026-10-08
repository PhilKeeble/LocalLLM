---
id: reference-native-computed-dispatch-tables
title: Indirect dispatch, relative jump tables, selector guards and target-set evidence
kind: reference
topics: [control-flow, jump-tables, indirect-branches, switch, bounds, decompilers]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Computed control-flow evidence

## An address table can contain block labels rather than function pointers
Reviewed 2026-10-02. GNU C supports computed goto to labels in the current
function, using either label addresses or differences relative to a base label.
Its array lookup does not automatically check the index. [1] These are language
extension examples, not a claim that all compiler switches use that layout.

Investigation inference: distinguish a switch's internal labels, threaded
interpreter dispatch, callback table and virtual-call table from the consuming
transfer and surrounding state. A branch to an internal block need not create a
new ABI frame. Do not assign a normal function prototype to every table target
or treat a source-like switch in pseudocode as proof of original source syntax.

## Relative table entries require the actual load width and base
A label-difference table is a documented GNU C representation. [1] Actual binary
recovery must establish entry width, signedness, base, scale, relocation and any
pointer normalization from the instructions; none is universal across tables.

Constructed 64-bit address calculation: base=0x4000, entry bits=0xffffffe0,
signed 32-bit load, target=base+entry. The target is 0x3fe0. Zero-extending that
entry would instead produce 0x100003fe0. If the load is genuinely unsigned, do
not impose the signed interpretation merely because it yields a plausible label.
The base might be a table, instruction or separate anchor; reconstruct its
producer. Check the full entry read and final instruction boundary independently.

## Recover the selector guard before counting reachable table entries
Constructed 32-bit dispatch: j=(x-10) modulo 2^32; an unsigned j<=3 condition
guards a four-entry table. This accepts x=10..13, while x=9 becomes 0xffffffff
and is rejected. Replacing the unsigned guard with signed j<=3 invents access
to a negative index. This is arithmetic reasoning, not compiled output.

Record the guard's width, direction, tested value version and every incoming
path to the load. A dominating comparison does not help if the loaded selector
is different or later overwritten. Holes can map to a shared default target;
repeated entries do not by themselves corrupt a table. Separate selector domain,
table-read bounds and executable-target validity: passing one does not prove
the other two. Check multi-level index tables one stage at a time.

## A decompiler's indirect edge is a model, not an exhaustive target set
Ghidra raw p-code BRANCHIND derives its target from a varnode. CALL/CALLIND
provide call intent but do not themselves implement the full machine call;
additional recovered parameters appear during later analysis. [2]

Investigation inference: inspect the original instruction's complete effects,
target expression and return state before reclassifying an indirect branch as
a call. For unresolved targets, keep an explicit unknown edge; do not let an
empty recovered target list become proof that the sink is unreachable. A runtime
trace of two targets confirms those executions, not that no third target exists.
Record whether the set is exhaustive for a bounded selector domain or only an
observed subset, including the evidence for any bounds used in that claim.

## Sources and limits
Reviewed 2026-10-02. Constructed numeric examples do not execute target code.
The source pages are rolling tool/language documentation, not universal machine
ABI specifications. GNU label-difference syntax has target restrictions, notably
the documented AVR exception; it is not an instruction-emission guarantee.

1. [GCC labels as values](https://gcc.gnu.org/onlinedocs/gcc/Labels-as-Values.html): computed goto, bounds responsibility and label-difference tables. GCC 15.1-specific endpoint was unavailable.
2. [Ghidra p-code operations](https://ghidra.re/ghidra_docs/languages/html/pcodedescription.html): BRANCHIND, CALL and CALLIND semantics and recovered parameters.
