---
id: abi-linux-syscall-boundaries
title: Linux syscall entry registers, raw errors, compatibility and vDSO evidence
kind: reference
topics: [syscalls, calling-conventions, errno, vdso, compatibility]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Linux kernel entry is not the C function ABI

## Identify the boundary before naming its arguments
Reviewed 2026-10-02. These are selected Linux interfaces, not generic ISA rules.
A call to libc syscall(number, ...) is a function call; the eventual trap has
the kernel's register assignment. A service-specific wrapper may add translation.
For native Linux x86-64 SYSCALL entry, RAX identifies the service; arguments are
RDI, RSI, RDX, R10, R8, R9. Hardware puts the return instruction address in RCX
and flags in R11; neither is a preserved input across the instruction. [1]

Constructed investigation: an apparent fourth argument is copied from RCX to
R10 before SYSCALL. This is ABI adaptation, not duplicate application data.
Reading RCX at kernel entry as the fourth argument would instead read a return
address. Separate the wrapper entry, trap entry and wrapper return snapshots.
Use source ID `abi-sysv-amd64` for ordinary calls, not to label raw trap inputs.

## Other Linux entry register maps are architecture-specific
Selected Linux entry forms and first six argument registers: [2]

| User ABI | Entry | Number | Arguments in order | Primary result |
| --- | --- | --- | --- | --- |
| i386 | INT 0x80 | EAX | EBX ECX EDX ESI EDI EBP | EAX |
| ARM EABI | SVC/SWI 0 | r7 | r0 r1 r2 r3 r4 r5 | r0 |
| AArch64 | SVC 0 | w8 | x0 x1 x2 x3 x4 x5 | x0 |
| RISC-V | ECALL | a7 | a0 a1 a2 a3 a4 a5 | a0 |

This is not an exhaustive clobber, extended-argument or fast-entry specification.
Do not infer OS identity or a service number's meaning from ECALL/SVC alone.
An ARM EABI r7 service selector is not the AArch64 w8 selector, nor an ordinary
function parameter. Match the user ABI even on a kernel supporting several ABIs.

## Raw x86-64 error values differ from libc errno returns
The inspected glibc Linux x86-64 wrapper tests the unsigned RAX representation
of the range -4095 through -1. Its errno-setting path negates the error into
thread-local errno and returns -1. Other wrapper macros deliberately omit errno
translation or return an error value directly. [3]

Constructed raw RAX=-13 therefore need not become a successful negative result
just because it is not -1. Conversely, a raw error test is not universally
equivalent to signed RAX<0. Recover the exact wrapper path before applying a
libc result contract. A raw trap does not itself perform glibc's thread-local
errno store. This section does not prescribe the error channel for MIPS, PowerPC,
FreeBSD or Darwin. Check each selected service's success-result domain as well.

## ARM EABI split values and x32 layouts require separate decoding
Linux ARM EABI little-endian readahead places its 64-bit offset in aligned
r2/r3 after fd in r0, leaving r1 as padding. The halves follow endianness.
Linux x32 uses an identifying syscall-number bit and has pointer/long/layout
differences from LP64; some services also have distinct table entries. [2]

Constructed ARM offset 0x1122334455667788 uses r2=0x55667788 and r3=0x11223344.
Treating r1 as the low half corrupts the recovered file position. An x86-64
instruction stream likewise does not justify eight-byte fields in every x32
user structure. Record the service-specific structure layout, not just the
kernel's machine width. Do not transfer the ARM split rule to all 64-bit operands.

## vDSO calls can be invisible to syscall-only tracing
Linux may supply operations such as time queries through a user-mapped ELF
vDSO. Its base is available through AT_SYSINFO_EHDR; symbols have versions and
use function calling conventions. A vDSO path completed without entering the
kernel is absent from syscall tracing and seccomp syscall evaluation. [4]
The Linux x86-64 entry source also identifies vDSO syscall fallback paths. [1]

Investigation inference: no clock syscall event does not prove that no time was
read. Follow the resolved vDSO symbol and the executed path, including fallback,
before concluding that instrumentation missed a kernel entry. Match the vDSO to
the user ABI and symbol version. Do not equate the historical x86 vsyscall mapping
with every modern vDSO function, or claim every vDSO call avoids a trap.

## MIPS o32 raw return a3 is an error flag, not a preserved fourth argument
Linux MIPS uses v0 for the service selector and primary result. o32 uses a0-a3
for its first four argument words and the user stack for further arguments;
n32/n64 use a0-a5 for the first six. [2] In the inspected o32 kernel path, extra
words are read at user-SP+16, +20, +24 and +28. Its normal error conversion sets
saved a3 to 1 and negates the internal negative error into positive v0. [6]

Constructed raw v0=13, a3=1 is therefore an error, not a successful 13-byte
transfer. A return-time a3 value also cannot reconstruct the original fourth
argument. Identify direct versus indirect syscall dispatch, ABI and snapshot
point; the inspected o32 indirect dispatcher shifts arguments. The exact flag
value here comes from implementation, not syscall(2)'s generalized boolean note.
Do not apply Linux's interface to an unknown MIPS firmware trap.

## PowerPC64 SC and SCV have different raw error contracts
The inspected Linux PowerPC64 interface uses r0 for the selector and r3-r8 for
up to six integer arguments. With SC, CR0.SO indicates error and r3 carries its
positive error value. With SCV 0, r3 in -4095 through -1 indicates an error.
SCV availability is reported by PPC_FEATURE2_SCV in AT_HWCAP2. [5]

Constructed SC result r3=13 with CR0.SO set must not be accepted as a successful
positive count. An SCV error instead uses the negative encoding; testing stale
CR0.SO is not its documented error test. Resolve the executed entry instruction
before interpreting registers. This is a Linux 64-bit contract, not an ISA-wide
or PowerPC32 rule. Low-level services such as rt_sigreturn can differ. The
inspected ptrace interface distinguishes these entry types in pt_regs.trap. [5]

## Sources and limits
Reviewed 2026-10-02. No target syscall execution is claimed. Android tags apply
to the Linux kernel boundary, not a claim that bionic has glibc's wrapper code.

1. [Linux v6.18 x86-64 entry](https://raw.githubusercontent.com/torvalds/linux/v6.18/arch/x86/entry/entry_64.S): entry_SYSCALL_64 register and hardware-entry comments.
2. [Linux syscall(2)](https://man7.org/linux/man-pages/man2/syscall.2.html): man-pages 6.19, architecture tables, ARM split example and x32 notes.
3. [glibc x86-64 syscall macros](https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/unix/sysv/linux/x86_64/sysdep.h): rolling source inspected; PSEUDO, NOERRNO, ERRVAL and error handler. Version-tag URLs were unavailable; no release-specific claim is made.
4. [Linux vdso(7)](https://man7.org/linux/man-pages/man7/vdso.7.html): mapping, versioning, calling convention and tracing sections.

## MIPS and PowerPC source scope
Reviewed 2026-10-02. Selected register interpretation, not full clobber tables,
transactional-memory behavior or service-specific structure layouts. Release-tag
endpoints were unavailable; the implementations below are rolling observations.
No target trap or libc wrapper was executed.

5. [Linux PowerPC64 system-call ABI](https://www.kernel.org/doc/html/latest/arch/powerpc/syscall64-abi.html): invocation, parameters, return value and ptrace sections.
6. [Linux MIPS o32 entry implementation](https://raw.githubusercontent.com/torvalds/linux/master/arch/mips/kernel/scall32-o32.S): handle_sys stack-word loads, saved PT_R7 error flag, result conversion and sys_syscall argument shift; rolling source.
