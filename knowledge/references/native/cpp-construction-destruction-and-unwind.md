---
id: reference-native-cpp-lifecycle-unwind
title: C++ construction phases, destructor variants and exceptional cleanup evidence
kind: reference
topics: [cpp, constructors, destructors, lifetime, exceptions, unwind, cleanup]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Distinguish lifecycle machinery from a lifetime bug

## Construction-phase dispatch is not completed-object dispatch
Reviewed 2026-10-02. In the C++ rules for a virtual call on the object being
constructed/destructed, dispatch from its constructor/destructor selects the
final overrider in that constructor/destructor's class, not a more-derived one.
The rule also covers indirect calls from those functions; it does not make
arbitrary cross-branch subobject calls valid. [1]

Constructed interpretation: a base-phase table store followed later by a
derived-phase table store can represent one successful construction. A later
base-phase store during destruction can also be legitimate. Repeated writes
to the vptr field are not by themselves evidence of corruption. Establish
which phase owns the receiver and whether an external callback can observe it;
an expected compiler store does not validate unrelated writes or unsafe
publication. Table identity alone is not proof of a live completed object.

## Itanium VTTs and destructor variants encode different responsibilities
In Itanium-style virtual inheritance, a VTT supplies construction-table pointers.
Itanium base destructors omit virtual-base destruction; complete destructors
include it; deleting destructors additionally deallocate. Mangling distinguishes
D2, D1 and D0 respectively. [2] This is not Microsoft destructor-flag encoding.

Investigative consequence: a D0 wrapper calling D1 then a deallocator is not
two frees merely because two destructor symbols appear. Identify the actual
release operation and allocation lifetime. Likewise, a VTT entry consumed as
a table pointer is not a callback target. Follow the load depth: table-selection
data and the table's callable entries occupy different roles. Missing symbols
require instruction evidence; a demangler's guessed variant is not proof of
which bases were destroyed. Variants may share code without sharing every role.

## A failed non-delegating constructor has partial cleanup obligations
C++ unwinding destroys completed subobjects when a non-delegating constructor
fails; destruction follows reverse completion order. It does not invoke the
failed object's complete destructor as if construction had succeeded. [3]

Constructed object D has members A then B. A finishes; B's constructor throws.
Cleanup destroys A, not a successfully constructed B or D. Completed subobjects
inside B can still require cleanup. Do not report the missing D destructor as
a leak without tracking resources acquired outside these completed subobjects.
Conversely, do not assume every acquisition belongs to a member with automatic
cleanup. Record the last successful construction step and each outstanding
resource at the throwing call. This example excludes delegating constructors.

## Delegating construction and allocation failure need separate paths
If a delegating constructor's target has completed and its subsequent body
throws, C++ invokes the object's destructor. For a failed new-initialization,
the matching deallocation function, if any, frees allocated storage under the
language's selection rules. [3] Deallocation is not completion of construction.

Investigative consequence: classify the constructor before applying the
partial-member cleanup rule. A complete destructor on the delegating-failure
path need not be double destruction. A deallocator following failed ordinary
construction need not imply a missing successful destructor. Trace member
cleanup, complete-object cleanup and storage release as different operations;
check placement/custom allocation contracts rather than assuming every failed
constructor calls ordinary operator delete.

## Itanium exception search and cleanup are different phases
Ordinary Itanium exception propagation searches for a handler before the
cleanup phase. Personality routines select language-specific actions; landing
pads can run cleanup before propagation continues. Forced unwinding is a
different path, not a universal two-phase copy of ordinary throwing. [4]

Investigative consequence: finding unwind metadata does not prove that every
exception path destroys every local object. Recover the personality, protected
instruction range, cleanup target and outgoing continuation. A cleanup-only
landing pad is not necessarily a catch that resumes normal execution. Do not
count a release once during handler search and again during cleanup merely
because both phases inspect the same frame. Preserve unhandled/termination
behavior as a separate uncertainty instead of inventing a successful catch.

## Windows funclets are not unrelated ordinary helper calls
LLVM describes Windows EH personalities using funclets that access the parent
frame; catch and cleanup bodies can have special entry conventions. Its
catchpad/cleanuppad constructs describe IR, not literal machine instructions.
The landingpad model separately represents exceptional continuations and can
resume propagation after cleanup. [5]

Investigative consequence: an apparent small function reading a parent-frame
offset may be a cleanup funclet, not an ordinary function with uninitialized
locals. Match the target's EH personality and metadata before assigning its
prototype. Do not infer that every Windows handler uses one fixed structure
or one historical __CxxFrameHandler version. Architecture unwind restoration
and language-level destructor selection answer different questions; the former
alone does not recover the latter.
For MSVC /EH modes, state-map coordinates and FH3/FH4 distinctions, see
`reference-windows-msvc-exception-cleanup-evidence`; SEH filters and vectored
callbacks are separately covered by `reference-windows-seh-vectored-handlers`.

## Two cleanup sites do not establish two releases on one execution
Constructed control flow: successful operation reaches cleanup N and returns;
a throwing operation reaches cleanup E and resumes propagation. Both release
the same acquired resource, but the two continuations are mutually exclusive
for that operation. This refutes only the alleged N-then-E path, not every
possible duplicate release. A cleanup that itself throws needs separate analysis.

To support a lifetime finding, identify one allocation/resource generation,
feasible predecessor conditions, ownership transitions and an actual repeated
release or post-release use. A decompiler listing two destructor calls lacks
that evidence. Use playbook-re-recover-cpp-lifecycle for the evidence packet and
reference-native-cpp-lifetime-move-decompiler for moved-from/ownership limits.

## A reconstructed stack is not a log of completed cleanup

For debugger evidence, keep a reconstructed frame distinct from a completed cleanup
action. A stopped destructor can still precede its release, and a missing frame can
reflect incomplete unwind evidence rather than absence of a call. Use
playbook-validation-debugger-evidence with the language/ABI rules above; identify
the actual operation before reporting a lifetime defect.

## Language and ABI sources

1. [C++ draft class.cdtor](https://eel.is/c++draft/class.cdtor), virtual calls during construction/destruction; rolling draft reviewed 2026-10-02.
2. [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html), sections 2.5.2, 2.6 and 5.1.4.3; rolling specification reviewed 2026-10-02.
3. [C++ draft except.ctor](https://eel.is/c++draft/except.ctor), completed subobjects, delegating construction and failed new-initialization; reviewed 2026-10-02.
4. [Itanium exception ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html), unwind process and personality interface; reviewed 2026-10-02.
5. [LLVM exception handling](https://llvm.org/docs/ExceptionHandling.html), Try/Catch, Cleanups, Windows Runtime and funclet sections; rolling implementation documentation reviewed 2026-10-02.
