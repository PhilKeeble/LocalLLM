---
id: abi-windows-x64
title: Windows x64 calling convention, shadow space, returns and unwind evidence
kind: reference
topics: [abi, calling-convention, shadow-space, arguments, return-values, unwind]
platforms: [windows]
architectures: [x64]
---
# Windows x64 ABI

## Scope and contract selection

This reference covers the ordinary Microsoft Windows x64 ABI. It does not
describe System V AMD64, Windows x86, ARM64EC, vectorcall or preserve_none.
Select the convention from the actual caller/callee interface before assigning
names to register values. Private optimized functions can require additional
call-site analysis. OS system-call interfaces are separate contracts. [1]

## Windows x64 argument positions

For the ordinary Windows x64 ABI, argument positions 1..4 select RCX/RDX/R8/R9
for integer/pointer values or XMM0/XMM1/XMM2/XMM3 for floating values. Positions
are shared, not separate integer and floating counters. Narrow integer
arguments occupy the low bits; do not infer their signedness from unused bits.
ABI-eligible trivial aggregates of size 1, 2, 4 or 8 bytes use integer positions;
other sizes are indirect. C++ nontrivial call types need their additional rules.
Vararg/unprototyped floating arguments in these positions also occupy the
corresponding integer register. [1]

Constructed example: for `f(void *p, double d, unsigned n, void *q, size_t z)`,
inspect RCX, XMM1, R8D, R9 and the fifth stack slot respectively. Reading RDX as
`d` in an ordinary prototyped call would be an ABI interpretation error.
Confirm the actual prototype and any hidden arguments before applying this map.

## Windows x64 aggregate arguments may be pointers to caller temporaries

ABI-eligible trivial 1/2/4/8-byte structs/unions use integer-class argument positions;
other sizes use pointers to caller temporaries, aligned to 16 bytes. __m128
arguments are indirect even though __m128 results use XMM0. No ordinary argument
is split between two registers. [1]

Clang 21.1.0's Microsoft ABI passes x64 records indirectly when its language-ABI
canPassInRegisters eligibility fails, irrespective of the small-size rule. [4]
This is distinct from return eligibility; do not apply a POD-size shortcut to
a parameter with nontrivial copy/destruction semantics. An indirect argument
can be a by-value temporary rather than a pointer explicitly declared in source.

## Windows x64 C++ record-return eligibility is not a sizeof-only test

For ordinary Windows x64 global/static C++ returns, a 1/2/4/8-byte record is not
automatically eligible for RAX. Microsoft's eligibility rule excludes
user-defined construction/destruction/copy assignment, bases, virtual functions,
reference members and private/protected nonstatic members; nested members must
qualify. A modern is_pod test is not a substitute for this documented ABI rule.
[1] Constructed contrast: a plain two-int record can return in RAX; a same-sized
record with a disqualifying constructor needs caller-provided storage. Recover
the type contract, not only sizeof, before interpreting the first pointer.

## Windows x64 variadic floating values

For ordinary Windows x64 varargs, floating values in the first four positions
appear in both corresponding XMM and integer registers. Address-taking can
cause the callee to home register values; this is not proof every slot was
initialized. [1] Constructed call f(tag, 2.5, 7): tag uses RCX, double bits use
XMM1 and RDX, integer uses R8. Duplication is the same value's representation,
not conversion of 2.5 to integer 2. Extra hidden arguments shift these positions.

## Windows x64 stack coordinates and shadow space

The caller reserves 32 bytes for register home slots even with fewer than four
arguments. Reservation does not mean the register values were stored there.
At ordinary callee entry, before the prologue changes RSP: return address is at
`[RSP]`, home slots at `[RSP+8]` through `[RSP+0x20]`, and argument five at
`[RSP+0x28]`. The callee can repurpose home slots. [2]

Track every push, subtraction, dynamic allocation and frame-register setup
before using those offsets later in the function. Ordinary call sites align
RSP to 16 bytes; entry after CALL includes the pushed return address. Prologue,
epilogue and leaf-function exceptions matter. Windows x64 provides no System V
128-byte red-zone contract below RSP. [2]

Investigation: stale bytes in an unused home slot do not prove an uninitialized
argument was consumed. Evidence must identify the actual consuming load.

## Windows x64 hidden return storage and result values

Ordinary integer/pointer results use RAX; floating results use XMM0. Eligible
small C++ return objects use RAX, but size alone does not establish eligibility.
For the documented global/static function hidden-return convention, the
caller supplies result storage in RCX, shifting explicit argument positions;
the result pointer returns in RAX. C++ member/thunk interfaces require their
actual compiler contract. [1]

The System V AMD64 MEMORY-return rule uses RDI, not this Windows x64 RCX
contract; see `abi-sysv-amd64`. Identify the ABI before interpreting a hidden
return buffer or shifting the apparent input arguments.

Constructed investigation: an apparent buffer parameter in RCX may instead be
caller-owned result storage. Check its allocation, writes through the pointer,
callee return and post-call use. Do not report missing validation until the
pointer's role and source are established.

## Microsoft C++ instance-method result evidence

Clang 21.1.0's MicrosoftCXXABI::classifyReturnType implements instance-method
record returns indirectly and places the result-storage parameter after this.
Under the ordinary Windows x64 register convention, that means this in RCX and
result storage in RDX, before explicit arguments. [4] This is a pinned compiler
implementation observation, not a universal rule for vectorcall, custom thunks,
different languages or optimized private interfaces.

Constructed investigation: stores through RDX plus a caller-allocated object
can support hidden-result recovery even when RCX clearly points to a receiver.
Do not apply the global/static hidden-RCX rule to this member interface. Verify
the caller, return type and compiler behavior before propagating the prototype.

## Windows x64 nonvolatile registers constrain cross-call data flow

For the baseline register set, RBX, RBP, RDI, RSI, RSP and R12..R15 are nonvolatile;
XMM6..XMM15 preserve their 128-bit state, not upper YMM/ZMM portions. Other
general argument/scratch registers are call-clobbered. [1]

Nonvolatile means the callee must restore the caller-visible value, not that the
register cannot change inside the callee. When tracing an input across a call,
separate the preserved register value from the lifetime or contents of any object
it points to. A preserved pointer does not imply preserved pointee data.

## Windows x64 unwind metadata adds recovery and exception-path evidence

Windows x64 RUNTIME_FUNCTION entries describe function start/end and unwind
information with image-relative addresses. Unwind codes describe stack and
nonvolatile-register recovery. Chained entries and language handlers can add
edges absent from ordinary branch analysis; leaf functions can lack entries.
JIT functions can register tables dynamically. [3]

For a cleanup finding, correlate unwind records with instructions and object
ownership. An unwind entry is not proof that an exception path executed; a
missing static entry is not proof that a byte range is data.

## Windows x64 unwind parsing boundaries

For the documented baseline format, a RUNTIME_FUNCTION has three 32-bit
image-relative fields: begin, end, unwind-info address. UNWIND_INFO includes
version/flags, prologue length, unwind-code count, frame register/offset and
variable records. Codes may occupy multiple slots; array padding and flags
determine the following handler data or chained function record. [3]

Use the actual version and range before decoding. An instruction stop inside
the prologue requires only operations already executed to be unwound; an
epilogue can require instruction recognition. Treat newer unwind formats,
including APX-related formats, as separate contracts. A parser assuming fixed
length per logical unwind operation can mistake metadata for a handler address.

## Microsoft x64 __chkstk is a special prologue helper
Microsoft's x64 prologue description passes the stack-allocation size in RAX
to __chkstk, then subtracts the unchanged RAX from RSP. The documented helper
preserves argument/nonvolatile registers and can change R10, R11 and condition
codes. [5] Do not apply the ordinary RCX-first argument rule to this helper.

Constructed trace: mov RAX,0x6000; call __chkstk; sub RSP,RAX. The size is not
the incoming RCX value, and treating all ordinary volatile registers as newly
unknown after this verified helper loses live function arguments. Identify the
actual target first; a same-named custom routine need not honor this contract.
The probe supports stack growth, not bounds validation for a later copy into
one local buffer. No universal compiler emission threshold is inferred here;
record the observed frame size and probe call. This is Microsoft x64 scope,
not x86, System V or an arbitrary stack-check routine.

## Sources and verification scope

Reviewed 2026-10-02 against Microsoft Learn; documentation review, not a target
execution. Baseline ABI only; newer register extensions need their own contract.

1. [x64 calling convention](https://learn.microsoft.com/en-us/cpp/build/x64-calling-convention?view=msvc-170): argument positions, varargs, returns, preservation.
2. [x64 stack usage](https://learn.microsoft.com/en-us/cpp/build/stack-usage?view=msvc-170): home-slot ownership, alignment and frame types.
3. [x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170): RUNTIME_FUNCTION, UNWIND_INFO and dynamic tables.
4. [Clang 21.1.0 MicrosoftCXXABI.cpp](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-21.1.0/clang/lib/CodeGen/MicrosoftCXXABI.cpp): classifyReturnType, getRecordArgABI and isSRetParameterAfterThis.
5. [Microsoft x64 prolog and epilog](https://learn.microsoft.com/en-us/cpp/build/prolog-and-epilog?view=msvc-170): __chkstk purpose, RAX input/preservation and register effects; reviewed 2026-10-02.

Related: `pe-headers-sections` for RVA mapping; `abi-sysv-amd64` for the different
System V convention; `playbook-debugging-windows-native-validation` for runtime
evidence collection.
