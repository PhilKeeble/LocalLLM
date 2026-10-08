---
id: playbook-recover-service-boundary
title: Recover a syscall or native-service boundary without importing the wrong ABI
kind: playbook
topics: [syscalls, calling-conventions, error-handling, trust-boundaries]
platforms: [linux, android, windows, macos, ios, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover a service boundary

## Establish which boundary the evidence describes
Reviewed 2026-10-02. This is a verification workflow, not a universal register map.
Record OS/kernel build, executable user ABI, machine mode, compatibility layer,
module identity and code address. Classify each snapshot as caller-to-wrapper,
raw trap, kernel argument frame, kernel return or wrapper-to-caller return.
Instruction names such as SYSCALL, SVC and ECALL do not establish the service ABI.

Find the actual wrapper/stub and entry path. Label a guessed service number or
prototype as a hypothesis until it matches the target's headers, symbols, table
or disassembly. For firmware, an ECALL may belong to a firmware/environment
interface rather than an OS; require that interface's specification. Do not
silently substitute the Linux table when the environment is unknown.

## Recover operands and result translation separately
Trace selector, argument registers, stack words and pointed-to structures at the
chosen boundary. Account for direct/indirect dispatch, hidden selectors, split
64-bit values, padding, compatibility sizes and wrapper transformations. Record
which registers contain addresses versus scalar values; trace length units and
the actual capture/use of each buffer.

Independently recover raw result words, flags/status fields, wrapper conversion,
errno/last-error writes and output-validity conditions. Distinguish ordinary
error from restart, pending work, partial output and special return restoration.
A correct service name does not establish a correct error predicate. Preserve
instruction evidence when a decompiler models flags or extra return registers
poorly; repair the model before reporting a missing check.

## Distinguish a defect from ordinary boundary translation
Compare the recovered success, ordinary-failure and relevant partial/restart
paths with the specific service contract. Use instructions, wrapper definitions
and available authorized observations to establish what each path consumes and
returns. Missing runtime evidence leaves a target hypothesis; it is not a reason
to execute an unknown binary merely to fill an evidence field.

Ask whether the apparent wrong argument is a wrapper-to-trap register move;
the apparent positive success is an error plus carry; the missing errno write
belongs to a raw interface; the missing trace event is a user-mode helper; or the
apparent trusted Windows pointer still comes from a user request. Conclude with
input provenance, violated condition, reachable use and demonstrated consequence,
not merely an unfamiliar stub pattern or missing opcode.

## Reference routing and evidence to retain
Use these reviewed homes instead of merging their conventions:

- `abi-linux-syscall-boundaries`: Linux maps, raw versus wrapper errors, split
  ARM values, x32 and vDSO visibility.
- `windows-native-service-boundaries`: Nt/Zw, PreviousMode, WOW64 and NTSTATUS.
- `abi-darwin-freebsd-service-evidence`: scoped Darwin ARM64 and FreeBSD AMD64
  dispatch, carry errors, trap-frame normalization and restart evidence.

Retain the target stub bytes, source version, entry/return snapshots, selected
prototype, argument-layout mapping and exact predicate used by the caller. A
reference route is not evidence that an unlisted OS/architecture combination has
been covered. Consult the target's own contract for such combinations.

## Sources and limits
Reviewed 2026-10-02. Workflow synthesis from the linked local references and
their inspected primary sources, not an observed case study or executed test.
Representative primary anchors:

1. [Linux syscall(2)](https://man7.org/linux/man-pages/man2/syscall.2.html): boundary and architecture distinctions.
2. [Microsoft PreviousMode](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/previousmode): trust-context distinction.
3. [Apple ARM BSD services](https://raw.githubusercontent.com/apple-oss-distributions/xnu/xnu-11417.121.6/bsd/dev/arm/systemcalls.c): separate argument and return handling.
