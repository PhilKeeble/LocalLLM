---
id: abi-darwin-freebsd-service-evidence
title: Darwin ARM64 and FreeBSD AMD64 syscall argument, error and restart evidence
kind: reference
topics: [syscalls, calling-conventions, carry-flag, trap-frames, restart]
platforms: [macos, ios, freebsd]
architectures: [arm64, x64]
---
# Selected Darwin and FreeBSD service boundaries

## Scope: inspected implementations, not one BSD syscall ABI
Reviewed 2026-10-02. Darwin facts below are scoped to selected Apple XNU
xnu-11417.121.6 source paths on ARM64. FreeBSD facts describe selected native
AMD64 paths in the rolling main source inspected on this date; the attempted
14.3 release URLs were unavailable. Neither set establishes every supported
release, compatibility ABI, CPU entry mechanism or public API guarantee.

Investigative use: identify the binary's OS, user ABI and boundary first. An
instruction set shared with Linux does not imply Linux service numbering or error
semantics. References `abi-linux-syscall-boundaries` and
`windows-native-service-boundaries` hold those platforms' separate evidence.
The examples below are constructed applications of source rules, not live traces.

## Darwin ARM64 service selection and BSD versus Mach dispatch
Apple's inspected ARM64 trap macro loads the selector in x16, then executes
SVC with SWI_SYSCALL. [1] Its ARM64 handler separates a platform-specific trap,
negative-number Mach dispatch (including special time traps), and nonnegative
Unix/BSD dispatch. [2] This is not Linux AArch64's w8 service-selection rule.

Investigation inference: an SVC preceded by a negative selector is not evidence
of a negative file descriptor or a failed prior operation. Resolve the dispatch
family before applying a service prototype or return test. A Mach trap is not
automatically a BSD syscall just because both cross the same instruction boundary.
The source-selected paths do not establish that all services on all Apple OS
releases use a stable selector value; match the target stub and kernel release.

## Darwin ARM64 BSD direct and indirect inputs differ
In the inspected XNU ARM64 BSD argument-copy path, direct calls copy argument
words starting at x0. For the indirect selector-zero path, x0 supplies the service
number and argument copying begins at x1. The count comes from the selected
sysent entry. Separate compatibility munging is conditional on the configuration
and task. [3]

Constructed investigation: labeling x0 as a file descriptor at an indirect BSD
entry misidentifies the service number as data and shifts every argument. Recover
the selector mode and sysent prototype before tracing a pointer/count pair.
Do not substitute the ordinary variadic function's stack layout for these kernel
registers: the user wrapper and kernel entry are different observation points.

## Darwin ARM64 BSD errors use carry, not Linux's negative range
The inspected XNU ARM64 BSD path clears carry for ordinary success. On an ordinary
error it writes the error to x0, clears x1 and sets carry for the runtime's error
handler. ERESTART instead backs up the saved PC by four; EJUSTRETURN leaves the
saved return state alone. [3]

Constructed raw x0=13 with carry set is therefore not a successful positive
byte count. A later libc -1 result and errno store can represent the same error
at a different boundary. Inspect the post-SVC condition-code branch before
judging error handling absent. Do not apply this BSD carry rule to Mach return
values, or report internal restart/just-return control values as ordinary results
delivered to the caller.

## FreeBSD AMD64 trap-frame RCX can contain the caller's R10
In FreeBSD's inspected native AMD64 fast_syscall entry, user R10 is saved into
the trap frame's tf_rcx slot as argument four; hardware RCX is saved as the return
instruction address. [4] The argument fetcher reads the contiguous frame fields
RDI, RSI, RDX, RCX, R8, R9. [5][6]

Thus the user trap arguments are RDI, RSI, RDX, R10, R8, R9, despite the C frame
member being called tf_rcx. This is an inference from both entry assembly and
frame consumption, not an instruction to read live user RCX as argument four.
When a kernel debugger and a user debugger appear to disagree, record which
representation each displays. Do not transfer this normalization to a different
trap path without checking that path's frame construction.

## FreeBSD AMD64 indirect calls and extra stack arguments
The inspected FreeBSD native AMD64 fetcher takes the direct service number from
saved RAX. SYS_syscall and SYS___syscall instead take it from saved RDI, shifting
the available argument registers. Where the selected service needs more words
than remain in registers, the fallback copies the remainder from user RSP plus
one register-sized slot. [5]

Investigation inference: a stack read for an extra syscall argument is not an
ordinary function's argument-seven rule without first accounting for indirect
dispatch. Resolve direct versus indirect service selection, required word count
and the user stack extent. The exact stack copy can fail; identifying argument
locations does not establish that the kernel successfully obtained the values.

## FreeBSD AMD64 error and restart paths are distinct outcomes
In the inspected native return implementation, success places return words in
RAX/RDX and clears carry. Ordinary error places the error number in RAX and sets
carry. ERESTART rewinds RIP by the recorded entry-instruction size, restores R10
from the argument-bearing frame RCX and requests full context restoration;
EJUSTRETURN does not replace the saved result. [7]

Constructed raw RAX=13 with carry set is an error, not a short successful read.
Do not decode this with Linux x86-64's -4095..-1 test. A repeated service entry
can be a restart rather than a second source-level operation; correlate the
instruction address, restart state and wrapper control flow before inferring
duplicate effects. This does not prove arbitrary non-idempotent work is safe to
repeat or that a user-visible interruption will always be automatically restarted.

## Apple sources
Reviewed 2026-10-02, XNU xnu-11417.121.6. Selected definitions and functions only;
no target kernel or stub execution. The BSD argument/error rules share one source.

1. [ARM trap macros](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.121.6/osfmk/mach/arm/syscall_sw.h): ARM64 kernel_trap.
2. [ARM64 exception handling](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.121.6/osfmk/arm64/sleh.c): handle_svc.
3. [ARM BSD services](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.121.6/bsd/dev/arm/systemcalls.c): arm_get_u64_syscall_args, arm_get_syscall_number, arm_prepare_u64_syscall_return and carry clearing.

## FreeBSD sources
Reviewed 2026-10-02, rolling main; match a target revision before extrapolating.
No release-number equivalence or compatibility-layer equivalence is claimed.

4. [AMD64 entry assembly](https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/amd64/amd64/exception.S): fast_syscall_common frame construction.
5. [AMD64 argument fetch](https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/amd64/amd64/trap.c): cpu_fetch_syscall_args and fallback.
6. [x86 trap frames](https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/x86/include/frame.h): AMD64 initial six register fields.
7. [AMD64 return handling](https://raw.githubusercontent.com/freebsd/freebsd-src/main/sys/amd64/amd64/vm_machdep.c): cpu_set_syscall_retval.
