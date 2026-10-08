---
id: reference-windows-msvc-exception-cleanup-evidence
title: MSVC exception modes, C++ cleanup states and architecture-qualified unwind metadata
kind: reference
topics: [windows, msvc, cpp, exceptions, unwind, funclets, binary-layout, cleanup]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# MSVC exception modes, C++ cleanup states and architecture-qualified unwind metadata

## Scope: language cleanup metadata is not just machine stack restoration

Reviewed 2026-10-02 against Microsoft documentation, the C++ draft and installed
MSVC 14.37.32822 headers. Header observations are implementation evidence for
that version, not a stable cross-compiler ABI. Match target architecture,
runtime helper and encoding before reading offsets. Managed/CLR behavior and
other compilers' personalities require their own contracts.

Machine unwind data restores stack/register state; language metadata selects
catch and cleanup actions. A valid stack walk does not prove all resources were
destroyed or all exceptional edges recovered. Generic constructor/destructor
rules remain in `reference-native-cpp-lifecycle-unwind`; Windows SEH/VEH selection
is in `reference-windows-seh-vectored-handlers`. Keep shared facts in those homes
rather than applying one universal exception model to every binary.

## MSVC exception mode changes what catch-all and cleanup can promise

Under MSVC /EHs or /EHsc, catch(...) handles C++ exceptions, not asynchronous
structured exceptions such as access violations; asynchronous faults do not
receive the same automatic-object cleanup guarantee. /EHa supports both in
catch(...) with the corresponding unwind support, but does not make continuing
after corruption safe. With no /EHs, /EHsc or /EHa, default C++ unwind support
is partial: automatic objects outside try blocks need not be destroyed.

/EHc with /EHs assumes extern "C" functions do not throw C++ exceptions. /EHr
forces noexcept runtime termination checks otherwise eligible for optimization.
These are compiler assumptions/code-generation choices, not proof that a target
can never fault. A single helper symbol does not establish one compilation mode
for every linked object; inspect build evidence or actual protected ranges and
cleanup. Do not infer missing cleanup from source-level catch syntax alone.
[MSVC /EH model](https://learn.microsoft.com/en-us/cpp/build/reference/eh-exception-handling-model?view=msvc-170).

## C++ propagation skips ordinary continuation after the throwing call

In ordinary handled C++ propagation, applicable fully constructed automatic
objects are destroyed in reverse construction order before control enters the
selected catch. A raw pointer variable's scope ending does not itself delete
its pointee. Code after the throwing call is not reached as an ordinary return.
[C++ stack unwinding](https://learn.microsoft.com/en-us/cpp/cpp/exceptions-and-stack-unwinding-in-cpp?view=msvc-170).

Investigative inference: reconstruct each resource's completed acquisition,
ownership transfer and unwind release. A decompiler may display normal cleanup
and an outlined cleanup separately even though the paths are exclusive. Pair
the cleanup with its parent frame and protected state before claiming an
uninitialized local, missing destructor or duplicate free. For failed and
delegating constructors, use `reference-native-cpp-lifecycle-unwind`; a failed
object is not automatically a successfully constructed object needing its full
destructor. This section is not a guarantee for an unhandled or fatal path.

## noexcept and a second escaping unwind exception have termination paths

The reviewed C++ draft requires std::terminate when handler search exits a
nonthrowing function boundary, when no matching handler exists, or when an
object destructor invoked during unwinding exits by throwing. Merely throwing
and catching an exception entirely inside that destructor is not the latter
condition. Bare rethrow with no currently handled exception also terminates.

Before terminate for an unmatched exception, whether the stack unwinds is
implementation-defined. At a nonthrowing boundary, full, partial or no unwind
is implementation-defined. Do not claim every destructor necessarily ran before
a crash just because it would run on ordinary handled propagation.
[C++ draft except.terminate](https://eel.is/c++draft/except.terminate).

This is a language-level boundary, not permission to extrapolate one CRT's
observed exit behavior to every version or compiler option. Trace terminate
handling separately from SEH filters and Windows fail-fast paths; they are not
interchangeable synonyms for a catch block that returns an error.

## A structured-to-C++ translator is per-thread and can be invoked repeatedly

MSVC _set_se_translator installs a per-thread structured-exception translation
function and requires /EHa. New threads must install their own translator.
It returns the previous function for restoration; another component can replace
the setting. A process import is not proof translation is installed on the
faulting worker.

Microsoft advises the translator do no more than throw the typed C++ exception:
invocation count is platform-dependent and can reflect multiple try-bearing
frames. Logging, freeing or accounting inside it must not be assumed to happen
exactly once per fault. The function must be native; managed exceptions are not
generically routed through it.
[MSVC _set_se_translator](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/set-se-translator?view=msvc-170).

Investigative implication: bind registration, thread identity, replacement and
throwing site before recovering the catch type. Translation does not validate
corrupted state or make an access violation safe to ignore.

## FH3-style maps associate state, cleanup transition and catch selection

Installed MSVC 14.37.32822 `ehdata.h` defines signed exception states with -1
as the blank state. Its UnwindMapEntry associates current-state indexing with
toState and an action funclet; TryBlockMapEntry has tryLow, tryHigh, catchHigh,
catch count and handler-array reference. HandlerType describes catch type,
catch-object displacement and handler address. These are distinct roles, not
one list of destructor addresses.

The header has conditional pointer versus image-relative forms. In its relative
form, map/type/handler displacements resolve using the image base; catch-object
and frame displacements have different bases. Do not add the image base to every
integer merely because nearby fields are RVAs. IptoStateMapEntry maps code
positions to states on the architectures declared by the header.

Constructed logical map: state 2 -> 0 runs release B; state 0 -> -1 runs release A.
The model orders B then A, not every numerically intervening state. This is not
an emitted target map. Bind actual IP, state, protected range and parent-frame
objects before claiming those releases execute. The header definitions above
do not specify all private runtime algorithms.

## FH4 compressed metadata must not be memcpy-decoded as a C++ struct

Microsoft's 2019 x64 FH4 description changes FH3 fixed fields to conditional
fields and variable-length integers, uses function-relative data where possible,
and permits more sharing of metadata/catch funclets. __CxxFrameHandler4 therefore
requires its own decoder, not just a renamed FH3 helper. The article's launch
defaults are historical, not proof of a current target's chosen runtime.
[Microsoft FH4 design](https://devblogs.microsoft.com/cppblog/making-cpp-exception-handling-smaller-x64/).

Installed 14.37.32822 `ehdata4_export.h` distinguishes disk encoding from expanded
logical structures. Its FuncInfo4 flags select optional maps and separated-code
handling; dispFrame is present for catch funclets. Some values are still RVAs,
others compressed/frame/function-relative fields. Recover each coordinate and
presence condition; sizeof a logical struct is not the encoded record length.
Shared catch code does not prove two functions share all ownership obligations.
These observations are scoped to this header and the documented x64 design,
not every ARM64/x86 toolchain or an exhaustive compressed-integer parser.

## FH4 IP deltas and encoded states are two different transformations

In installed MSVC 14.37.32822 `ehdata4_export.h`, IP-to-state entries encode
function-relative instruction positions as deltas and state as EHstate+1.
Encoded state zero therefore denotes -1, not state 0. Separated-code maps also
identify the relevant function contribution; one global base is insufficient.
An unwind-map link uses its documented byte-offset encoding, not automatically
an FH3 toState field.

Constructed decoded-integer example, not variable-length byte decoding: deltas
4,6,12 accumulate to function offsets 4,10,22. Encoded states 0,2,3 correspond
to states -1,1,2. Treating 6 and 12 as absolute offsets or 0 as active state 0
would attach cleanup to the wrong instruction range. Preserve checked bounds,
base, encoding and state transition when rebuilding an exceptional CFG.
This arithmetic model does not establish instruction boundaries, runtime handler
selection or target vulnerability. Match the actual header/runtime version first.

## ARM64 .pdata is not the x64 three-RVA record

For Microsoft's Windows ARM64 unwind format, each .pdata record is eight bytes:
a 32-bit function-start RVA and a word selecting packed unwind information or
an aligned .xdata RVA through low flag bits. Eligible leaf functions without
local storage or nonvolatile-register saves can omit records and unwind through
LR. Unwind codes support partially executed prologues/epilogues; do not undo
operations that have not happened.
[Windows ARM64 exception handling](https://learn.microsoft.com/en-us/cpp/build/arm64-exception-handling?view=msvc-170).

The Windows x64 baseline instead has three 32-bit RUNTIME_FUNCTION fields,
described in `abi-windows-x64`. Neither format alone identifies which C++
destructor to call: recover the associated language handler and data. Match
PE machine type, range and flags before parsing; do not apply ARM64 packed
record logic to x64 or a historical x86 SEH chain. A missing static record alone
is not proof of unreachable code or an absence of exceptional control flow.

## A cleanup frame in a recovered stack does not prove release completed

Investigative inference: a stack naming a destructor or cleanup funclet establishes
at most the recovered current call chain, subject to context and unwind accuracy.
It does not prove that the release instruction ran, returned successfully or was
reached under the expected construction state. Capture the selected exception
context and actual PC, then connect the resource generation to the relevant action.

For a double-free or leaked-resource hypothesis, distinguish handler search,
cleanup entry, completed release and termination. /EH mode and the language's
termination rules above constrain which cleanup guarantees apply; a successful
stack walk is not a destructor-execution log. Context and saved-register limits:
reference-validation-windbg-context-memory. Broader workflow:
playbook-validation-debugger-evidence.
