---
id: reference-validation-signal-origin-fault-precision
title: Linux signal origin, fault addresses and synchronous versus asynchronous MTE reports
kind: reference
topics: [crash-analysis, signals, siginfo, sigsegv, sigbus, mte, fault-address, arm64]
platforms: [linux]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Signal origin and fault-location precision

## Linux signal number alone does not identify a faulting instruction

Linux siginfo_t.si_code explains signal origin; it is a value, not a bit mask.
SI_USER denotes kill, SI_QUEUE sigqueue, and SI_TKILL tkill/tgkill. Other fields
can share union storage and are meaningful only for the corresponding signal
and origin. [1]

Investigative consequence: SIGSEGV delivered by another process is not proof of
a memory access at the interrupted PC. Decode origin before treating si_addr or
sender information as meaningful. Preserve the raw signal, code, context and
source of the report. A crash-report label may omit that information; do not fill
it in from the signal name. These Linux values are not Windows exception codes
or universal numeric constants across operating systems.

## Mapping, permission, alignment and object errors are distinct classifications

Linux defines SEGV_MAPERR for an unmapped address and SEGV_ACCERR for an invalid
permission on a mapped object. SIGBUS codes distinguish alignment (BUS_ADRALN),
nonexistent physical address (BUS_ADRERR) and object-specific hardware error
(BUS_OBJERR). [1]

Investigative consequence: classify the reported mechanism, then recover the
actual instruction and operand. A signal name does not distinguish an out-of-bounds
access, stale pointer, intentionally raised signal or backing-resource failure.
Neither mapping nor permission evidence establishes a C/C++ object's boundary.
Use allocation/ownership and input-flow evidence to select among candidate causes;
do not equate every SIGBUS with alignment or every SIGSEGV with a buffer overflow.

## Saved signal context and siginfo fault address have different roles

For a Linux SA_SIGINFO handler, the third argument points to ucontext_t containing
saved signal context. siginfo contains event details. Some hardware exceptions do
not supply meaningful values for all relevant siginfo fields; the man-page caveat
includes an x86 forbidden int case yielding zeroed fields. [1]

Investigative consequence: recover PC/registers from the correct target context,
not from an assumed siginfo layout or the crash reporter's current registers.
Do not call a zero address a null-pointer dereference without an access instruction
and a meaningful address field. Architecture-specific register layouts and field
validity must match the target. An unknown address is not a known access to zero.

## AArch64 Linux synchronous MTE reports identify a prevented access

For supported AArch64 Linux MTE tag checking in synchronous mode, the kernel
reports SIGSEGV with SEGV_MTESERR and the fault address; the memory access is not
performed. [2]

Investigative consequence: preserve the actual mode, tagged pointer, object/tag
evidence and attempted operation. A tag mismatch is not by itself a complete
lifetime or bounds diagnosis. The prevented access does not prove earlier accesses
were valid or that its intended data value was written. Do not apply this precise
location guarantee to an asynchronous report merely because both use SIGSEGV.

## AArch64 Linux asynchronous MTE reports can combine multiple earlier faults

In asynchronous mode, AArch64 Linux reports SIGSEGV with SEGV_MTEAERR after one or
more tag-check faults, with si_addr=0 because the address is unknown. Asymmetric
mode handles reads synchronously and writes asynchronously. [2]

Investigative consequence: the reported stop PC need not be the access that first
mismatched a tag. si_addr=0 is not evidence of a null dereference in this case.
Preserve the interval and available trace rather than invent one exact prior
instruction. Any separately authorized change to a diagnostic mode produces new
evidence under new conditions; it does not retroactively make the original report
synchronous or guarantee the same schedule.

## Sources and scope

Reviewed 2026-10-02. Linux user-space reporting contracts; MTE sections apply only
to supported AArch64 Linux configurations. Other operating systems need their own
exception and signal-reporting contracts. Workflow:
playbook-validation-first-fault-cause.

1. [Linux man-pages sigaction(2)](https://man7.org/linux/man-pages/man2/sigaction.2.html): siginfo origins, union fields, signal codes, saved context and incomplete hardware-fault details.
2. [Linux kernel AArch64 MTE documentation](https://docs.kernel.org/arch/arm64/memory-tagging-extension.html): synchronous, asynchronous and asymmetric reporting.
