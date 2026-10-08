---
id: abi-windows-arm64ec-boundaries
title: Windows ARM64EC register context, signature thunks, variadic calls and checker boundaries
kind: reference
topics: [abi, arm64ec, thunks, varargs, register-context, call-checkers, mixed-architecture]
platforms: [windows]
architectures: [arm64, x64]
---
# ARM64EC ABI evidence at a mixed-code boundary

## ARM64EC is not classic ARM64 or an x64 instruction stream

ARM64EC runs ARM instructions while interoperating with emulated x64 code on
Windows 11 on Arm. It uses x64-compatible data conventions, but classic ARM64
is a different ABI. [1] Use reference-windows-arm-hybrid-images for module/view
identification; use abi-aarch64-platform-conventions for classic ARM64.

Recover the code range and boundary type before assigning argument registers.
Data-layout compatibility does not imply that each ARM instruction uses x64
register rules. A thunk, ordinary function and runtime checker can have different
contracts even inside one image. The existing abi-windows-x64 reference describes
the x64 side, not every ARM64EC callee.

## SDK register context overlay is not a function argument map

Inspected Windows SDK 10.0.22621.0 winnt.h, ARM64EC_NT_CONTEXT: the x64-compatible
storage overlay maps X0/1/2/3 to RCX/RDX/R8/R9, X8 to RAX, SP to RSP and PC to
RIP. X19..22 map R12..15; X25/26/27 map RSI/RDI/RBX. LR, X6/X7, X9..12 and X15 use
parts of the x87 save region; V[0..15] overlays XMM storage. [2]

These are saved-state correspondences, not the assignment of every source-level
parameter. In particular, X8's RAX correspondence does not turn an ordinary ARM
integer return into an X8 return. Locate whether the stop is in an EC body,
entry/exit thunk or emulated x64 code. The SDK definition is version-scoped;
do not substitute classic ARM64_NT_CONTEXT's contiguous register array.

## Blocked registers and preservation across thunks

ARM64EC disallows X13, X14, X23, X24, X28 and V16..V31. X18 retains the platform
TEB role. X19..22, X25..27, FP and SP are nonvolatile. V6/V7 are volatile;
V8..V15 preserve their low 64 bits, not their full 128 bits. Entry thunks bridge
the difference from x64's full XMM6..XMM15 preservation. [3]

Investigation: a save/restore sequence around the body may implement ABI
adaptation rather than application state management. An alleged clobber needs
the preservation contract at that exact boundary. A disallowed-register use
is reason to recheck decoder/range/ABI identification, not alone proof that the
whole image is corrupt. Names in a decompiler do not override instruction bytes.

## Entry and exit thunks depend on the function signature

Entry thunks adapt x64 callers to ARM64EC; exit thunks adapt EC calls to x64.
Microsoft describes signature-specific conversion, including type-dependent
parameter placement. [4] One register-renaming rule cannot replace that work.

Constructed ordinary signature `int f(int a,double b,int c,double d)`:
the EC body receives a/c in W0/W1 and b/d in D0/D1; the x64 side uses
ECX/R8D and XMM1/XMM3. This follows the corresponding platform argument rules,
not the saved-context overlay. Recover hidden result pointers and aggregates
separately. A shared thunk for matching signatures does not mean its callers
are the same function or operate on the same object.

## ARM64EC indirect-call checkers are not synonymous with CFG enforcement

For EC indirect calls, the checker resolves target architecture even when CFG
is disabled. The documented sequence supplies target in X11 and exit thunk in
X10; the checker can replace X11 before the following call. The symbols
__os_arm64x_check_icall and __os_arm64x_check_icall_cfg distinguish requested
checking paths, not proof of runtime CFG enforcement. [4]

Investigative consequence: a call through the changed register may enter an
adapter rather than the original target directly. Preserve both addresses and
the final destination in the call graph. Do not model the checker as an ordinary
user function that consumes or destroys the normal argument registers. Runtime
architecture adaptation does not authorize the requested application operation.

## Variadic calls use four general argument registers, not eight

LLVM 19.1.7's ARM64EC variadic convention bit-transfers floating arguments to
integer carriers, uses W/X0..3, and assigns remaining scalar carriers eight-byte
stack slots. Its classic Windows ARM64 variadic convention instead delegates
to the eight-register scheme. [5] This is compiler implementation evidence
corroborating the Microsoft ABI, not execution on an Arm target.

Microsoft additionally specifies X4 as the address of stack argument five and
X5 as stacked-argument byte size; separately spilled by-value aggregates do not
count in that area. For register-passed aggregates, exact sizes 1/2/4/8 are direct;
other sizes use an address of temporary storage. [4]

Inference: X4/X5 can be ABI machinery, not two extra application arguments.
A variadic double's general-register bits are not an integer conversion.
Do not apply classic ARM64's X0..7 model to an ARM64EC varargs callee.

## LLVM thunk conventions are distinct from normal EC functions

LLVM 19.1.7 defines separate Arm64EC_Thunk and Arm64EC_Thunk_Native conventions.
Both carry an extra destination pointer in X9; the former models x64 argument
placement with ARM register names, while the latter delegates ordinary argument
placement to AArch64 after that destination. Its x64-side scalar integer return
mapping starts at W8/X8. [5]

Inference: an X9 indirect branch target inside this adapter is not necessarily
a missing user-supplied parameter. Follow its producer and the matched signature
before assigning a prototype. Internal LLVM calling-convention names describe
compiler IR/lowering; they are not numeric values stored in a Windows PE field.

## Stack and cookie helpers have EC-specific variants

Microsoft names __chkstk_arm64ec and __security_check_cookie_arm64ec separately
from the x64 helpers. For the EC stack probe, X15 gives the requested byte count
divided by 16. [4] Treat this as a special helper contract, not a normal first
argument in X0. Probe size units are not an application buffer length.

Investigative inference: a helper may preserve otherwise volatile arguments so
the surrounding prologue can continue. Do not delete its edge merely because
it has no obvious application result. Nor does the presence of a cookie/probe
prove that every memory operation is safe. Recover the actual fault and object
extent independently.

## EC compatibility does not erase memory-ordering differences

Microsoft warns that ARM64EC interoperability does not resolve x64-versus-Arm
memory-model differences. [3] Its MSVC migration guidance gives /volatile:ms as
the default for x86, x64 and ARM64EC, while ordinary Arm defaults to /volatile:iso;
these are compiler options, not ISO C++ synchronization guarantees. [6]

For an investigation, identify the actual compiler options and emitted atomics,
barriers and ownership protocol. A working emulated x64 path does not prove a
recompiled EC path has the same unsynchronized timing behavior. Conversely, an
Arm instruction stream alone does not prove a missing barrier. Shared facts
live in architecture-memory-ordering-barrier-evidence and
reference-concurrency-memory-order-atomic-invariants.

## Sources and scope: ABI and inspected SDK

Reviewed 2026-10-02. Windows 11 ARM64EC only, not Apple's arm64e ABI or classic
ARM64. No ARM64EC executable was run locally.

1. [ARM64EC overview](https://learn.microsoft.com/en-us/windows/arm/arm64ec): compatibility scope.
2. Installed Windows SDK 10.0.22621.0, um/winnt.h, ARM64EC_NT_CONTEXT and associated offset assertions, inspected locally. SHA256 021274FD3F3602D0D4661E87D4DAE25BABEF018A99F2568D5F7CB387C77BAF63. This supports the scoped context overlay, not an emulation reproduction.
3. [MSVC ARM64EC ABI conventions](https://learn.microsoft.com/en-us/cpp/build/arm64ec-windows-abi-conventions?view=msvc-170): register restrictions, preservation, thunks and memory-model warning.

## Sources and scope: calls and compiler behavior

4. [Understanding ARM64EC ABI](https://learn.microsoft.com/en-us/windows/arm/arm64ec-abi): signature transitions, call checkers, varargs addenda and special helpers.
5. [LLVM 19.1.7 AArch64CallingConvention.td](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-19.1.7/llvm/lib/Target/AArch64/AArch64CallingConvention.td): CC_AArch64_Arm64EC_VarArg, thunk/native-thunk, return and checker definitions; not a claim that every target was built with LLVM.
6. [MSVC Arm migration issues](https://learn.microsoft.com/en-us/cpp/build/common-visual-cpp-arm-migration-issues?view=msvc-170): volatile option defaults and synchronization limits only. Its broad historical instruction examples are not substituted for ISA-specific references.
