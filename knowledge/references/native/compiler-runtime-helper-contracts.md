---
id: reference-native-compiler-runtime-helpers
title: Compiler runtime arithmetic helpers, return encodings and instrumentation boundaries
kind: reference
topics: [compiler-runtime, libgcc, compiler-rt, arithmetic, helpers, instrumentation]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Preserve the real contract of compiler-generated calls

## Helper calls can implement ordinary arithmetic or memory operations
Reviewed 2026-10-02. GCC can emit libgcc calls for operations unsuitable for
inline implementation, including arithmetic and exception support. It can also
introduce libc memcpy/memset calls. Its runtime manual prototypes use illustrative
C types for machine modes, not the target's ordinary C type widths. [1]

Investigative consequence: a helper call does not establish an explicit source
API call. Recover the operation and target ABI before inferring intent. In
particular, the manual's displayed long for a DImode operand is not permission
to truncate that operand to a target's 32-bit C long. Preserve register pairs,
hidden outputs and mode width as observed. Do not discard arithmetic data flow
because the decompiler places it behind a runtime-looking function name.

## Compiler runtime identity does not uniquely identify the compiler
Clang supports compiler-rt and, on supported targets, libgcc as compiler runtime
choices. Runtime selection and C++ standard-library selection are separate
toolchain choices. [2]

Investigative inference: seeing a libgcc helper does not prove every containing
translation unit was compiled by GCC. Likewise, a libc++ or libstdc++ name is not
an exact compiler-version fingerprint. Keep compiler, linker, runtime library,
standard library, ABI and local patches as distinct provenance hypotheses.
Mixed evidence can reflect a supported toolchain combination rather than
corruption. Confirm a security-relevant helper's actual implementation and
caller interface before replacing it with a remembered contract.

## Integer comparison helpers can return 0, 1 and 2
GCC's __cmpdi2/__cmpti2 compare signed operands; __ucmpdi2/__ucmpti2 compare
unsigned operands. Their result encodes less/equal/greater as 0/1/2. [3]
This is not strcmp's negative/zero/positive contract or a Boolean equality test.

Constructed helper result r: r==1 means equality; r<1 means less; r!=0 means
equal or greater. For operands 5 and 5, r=1, so interpreting a nonzero result
as inequality reverses the conclusion. Keep the consumer comparison exactly
as emitted. Verify helper identity and operand mode first; an assigned symbol
alone does not establish that a stripped routine implements this encoding.
Unsigned and signed variants can give different results for the same high-bit
bit patterns even though their result encoding is the same.

## Quotient return and remainder output are separate data-flow edges
GCC __udivmoddi4/__udivmodti4 return the unsigned quotient and store the remainder
through their output-pointer argument. [3] Recover the actual target mode and
calling convention rather than copying the manual's illustrative C widths.

Constructed nonzero-divisor example: 17 divided by 5 returns 3 and writes 2 to
the remainder destination. If a caller subsequently loads that destination,
its value is not necessarily the return register's 3. A summary that models
only the return loses a memory definition and can fabricate an uninitialized
read or the wrong allocation length. Trace the pointer's alias, access width
and whether the call returned on the relevant path. This example supplies no
division-by-zero or signed-overflow behavior for an unidentified implementation.

## Trapping arithmetic and zero-input bit counts have distinct domains
GCC documents signed-overflow trapping helpers such as __addvdi3 as calling
abort on overflow. It documents __clzdi2's result as undefined for zero. [3]
These are helper contracts, not generic rules for all machine ADD/CLZ opcodes.

Constructed analysis: do not propagate an ordinary wrapped sum down the normal
return edge after an overflowing call to a verified trapping helper. Conversely,
absence of a trap in an unrelated add instruction does not refute that helper's
contract. For a zero leading-bit-count input, do not substitute the operand
width merely because a different instruction defines that result. Inspect the
actual implementation if zero is reachable; undefined contract input does not
by itself prove what the shipped bytes do or establish a vulnerability.

## Atomic and sanitizer helpers add effects, not application intent
Clang can lower unsupported or unsuitable atomic operations to __atomic_*
runtime calls. Sanitizer instrumentation can add runtime calls that maintain
diagnostic state and report problems. [2]

Investigative consequence: absence of an inline atomic instruction does not
prove absence of atomic behavior; identify the helper, width and memory-order
contract. A sanitizer report stub is not automatically application error
handling, and finding one does not establish that all accesses were checked.
Trace the actual call and build instrumentation. Do not classify runtime code
as effect-free solely to simplify data flow; preserve writes, possible failure,
unwind and callback behavior required by the identified contract.

## Windows probes and cookies answer different questions
For Microsoft x64 stack probing and its special register contract, use
abi-windows-x64. A stack-range probe is not an application buffer-capacity check.
MSVC /GS uses a security cookie checked on relevant exits/unwinding and can
terminate on a mismatch; Microsoft explicitly limits its protection. [4]

Constructed investigation: a recognized cookie-check helper occurs after an
unchecked copy. That later detection does not make the preceding out-of-bounds
write valid or prove all damaged state was covered. Nor is a cookie comparison
evidence that a user was authenticated. Separate instrumentation, operation
preconditions and application authorization. Record the first invalid operation
before interpreting a later runtime termination. This section does not specify
cookie layout or protection coverage for every compiler, architecture or build.

## Runtime sources
1. [GCC low-level runtime](https://gcc.gnu.org/onlinedocs/gccint/Libgcc.html): implicit calls and machine-mode prototypes; rolling manual reviewed 2026-10-02.
2. [Clang toolchain](https://clang.llvm.org/docs/Toolchain.html): compiler runtime, atomics, sanitizer and standard-library choices; rolling documentation reviewed 2026-10-02.
3. [GCC integer runtime routines](https://gcc.gnu.org/onlinedocs/gccint/Integer-library-routines.html): comparison encoding, unsigned quotient/remainder, trapping arithmetic and bit-count input domain; reviewed 2026-10-02.
4. [Microsoft /GS](https://learn.microsoft.com/en-us/cpp/build/reference/gs-buffer-security-check?view=msvc-170): cookie checking and limits; reviewed 2026-10-02.

Examples are constructed contract checks, not execution of any target runtime.
Attribution workflow: playbook-re-validate-library-attribution.
