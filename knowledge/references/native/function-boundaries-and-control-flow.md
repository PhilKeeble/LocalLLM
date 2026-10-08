---
id: reference-native-function-boundaries-control-flow
title: Function starts, split ranges, callback edges, tail transfers and noreturn evidence
kind: reference
topics: [function-discovery, control-flow, callbacks, tail-calls, noreturn, unwind]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Function identity is not a byte-pattern classification

## Symbols describe entities but do not always provide complete extents
Reviewed 2026-10-02. ELF 4.3 DRAFT defines STT_FUNC for a function or other
executable code, STT_NOTYPE as unspecified, and st_size=0 as absent/unknown size.
[1] A zero-sized symbol is not evidence of a zero-byte function. Its next symbol
is not automatically the missing end: aliases, local labels and separate ranges
must be checked. Use `format-elf-structure-addresses` for symbol coordinates.

Investigation inference: retain entry candidates separately from established
instruction ranges and source-function identities. Associate bytes, valid mode,
incoming edges, symbols, relocations and matching debug/unwind records. Stripping
symbol information reduces evidence; it does not remove executable behavior.
An instruction-looking byte sequence alone establishes neither an entry nor a
reachable path. Treat metadata from a malformed file as a claim to validate.

## Split cold blocks and optional prologues defeat linear function carving
GCC 15.1 documents frame-pointer omission, path-dependent prologues through
shrink wrapping, and supported hot/cold block partitioning into separate
sections. [2] These are capabilities, not evidence that a specimen used GCC.

Constructed case: entry 0x1000 branches on error to 0x5000; both paths use the
same live frame and converge at its epilogue. The distant block need not be a
new source function. Conversely, adjacency alone does not establish shared
ownership. Trace frame state and incoming edges across both ranges before
excluding an error-path bounds check. A missing conventional push/move prologue
does not by itself show corrupted code, a tail fragment or a nonfunction.

## Windows x64 unwind records corroborate ranges, not all possible entries
Windows x64 permits eligible leaf functions without static function-table
entries, and dynamic code can register function tables. [3] The format and
parsing rules live in `abi-windows-x64`; do not apply them to every OS or ISA.

Investigation inference: a valid unwind-covered interval supports stack-state
reconstruction within that interval, not a complete inventory of callbacks or
all source functions. Missing .pdata coverage does not prove data. Correlate
the actual instruction position, chained/handler information and registered
dynamic ranges when available. A cleanup address requires its exceptional edge
and live-object conditions; metadata alone does not demonstrate its execution.

## An export can name data or a forwarder rather than a local body
In PE, an export-address-table entry can identify code/data or a forwarder
string, depending on its relation to the export-directory range. [4]
Resolve that distinction before adding a function at the entry's RVA. Coordinate
and range rules belong to `pe-headers-sections`. Mach-O re-exports and ELF symbol
resolution have separate contracts in their format references.

Constructed investigation: a named export resolves through another DLL. Absence
of a local disassembled body is not a missing implementation or an inert API.
Conversely, an exported data pointer does not become callable merely because a
tool lists it among exports. Record the resolved object, address kind and consumer.
An image entry point likewise is an initialization root, not proof of source main.

## No direct caller does not make an address-taken callback dead
For the documented qsort interface, the comparison function is supplied as a
pointer and is invoked with pointers to two elements; its integer result gives
their ordering. [5] An application-to-comparator direct CALL need not exist.

Constructed case: a function address is passed to qsort with reachable n=2.
Trace the pointer argument and library call edge before declaring the comparator
unreachable. Address-taking alone still does not prove invocation: n=0, rejected
registration, overwritten pointers or an unused table need separate paths.
For asynchronous callbacks, retain registration, dispatch, cancellation and
owner lifetime; do not transfer qsort's synchronous contract to event APIs.

## A tail transfer inherits a return path; a jump alone does not prove one
GCC documents sibling/tail-call optimization. [2] A tail-call hypothesis needs
the outgoing arguments, restored/reused caller state and inherited continuation,
not just an unconditional jump to an address labeled as a function.

Constructed case: function F restores its frame, prepares G's inputs and jumps
to G while preserving F's incoming return continuation. G can return directly
to F's caller. Inventing a new return address at F's jump misreconstructs the
stack. A shared epilogue, intra-function jump or range-extension stub can look
similar locally; distinguish them by state and target use. Machine-specific
link-register, stack and delay-slot rules remain in the selected ISA/ABI home.

## noreturn removes normal return, not every exceptional continuation
GCC 15.1's noreturn attribute does not forbid throwing or longjmp. [6] Therefore
normal fallthrough after a verified nonreturning call and exceptional transfer
to a handler are different edges. A disassembler's noreturn annotation is a
hypothesis about the target, not proof of that target's contract.

Constructed case: a helper always throws, and a caller's catch performs cleanup.
Deleting the catch path because the helper is noreturn can hide a release bug.
Conversely, inventing normal fallthrough after process termination creates a
fictitious path. Check the actual target and available exit mechanisms; correct
one call site's flow without globally imposing the same annotation on unrelated
indirect targets. Do not equate noreturn with nothrow or with unconditional exit.

## Sources and limits
Reviewed 2026-10-02. Factual contracts and constructed investigation cases;
no target execution or recovered source-function inventory is claimed.

1. [ELF symbol table, 4.3 DRAFT](https://gabi.xinuos.com/elf/05-symtab.html): st_size and symbol types.
2. [GCC 15.1 optimization options](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Optimize-Options.html): omit-frame-pointer, shrink-wrap, reorder-blocks-and-partition and optimize-sibling-calls.
3. [Microsoft x64 exception handling](https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170): function tables, leaf handling and dynamic registration.
4. [Microsoft PE format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format): export address table.
5. [Linux qsort(3)](https://man7.org/linux/man-pages/man3/qsort.3.html): comparator interface; no qsort_r portability claim.
6. [GCC 15.1 function attributes](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Common-Function-Attributes.html): noreturn versus nothrow.
