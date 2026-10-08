---
id: reference-validation-gdb-lldb-context-memory
title: Debugger process identity, selected frames, registers and memory evidence
kind: reference
topics: [gdb, lldb, debugging, registers, memory, threads, stack-frames, symbols]
platforms: [windows, linux, macos, freebsd, android, ios, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Debugger context and memory interpretation

The scoped contracts below interpret evidence produced by GDB or LLDB. They do
not require either product or imply that other exposed debugging capabilities
use the same identifiers, defaults or register-recovery rules.

## GDB inferior numbers and thread numbers are not operating-system IDs

An inferior is GDB's representation of an execution, not necessarily a live process.
Its debugger number is distinct from process information and executable identity.
GDB thread identifiers can use inferior.thread syntax; debugger-numbered thread
selection is distinct from target system identifiers. [1,2]

Investigative consequence: record the mapping to the actual process/thread and
current stop. Do not insert a PID or OS thread ID where a debugger index is required.
An inferior can represent a core or an exited execution; a row in the list is not
proof of a live task. A reused PID/address does not preserve object or run identity.

## LLDB thread selection and stop reason constrain subsequent inspection

LLDB distinguishes the displayed thread index, selected stack frame and process
state. More than one thread can have an interesting
stop reason when control returns to the debugger. [3]

Investigative consequence: preserve target/process identity before selecting a
thread. Distinguish the thread being inspected from the thread responsible for the
event. A prompt or selected frame does not by itself establish a new coherent
capture. Retain stop reason, frame index and program counter with each operand
record; do not combine values from different stops into an apparent single call.

## GDB outer-frame registers are reconstructed values, not past snapshots

GDB normally reports registers relative to the selected frame. frame 0 selects
the innermost frame for actual stopped hardware-register contents. Unwinding may
recover saved registers, but an outer frame's call-clobbered register can be
unavailable or fail to represent its value before the call. info registers omits
floating-point/vector registers; info all-registers includes them. [4]

Investigative consequence: selecting a caller does not restore every argument as
it was at call entry. Reconstruct volatile arguments from instructions or captured
call-entry evidence instead of reporting guessed debugger values as observed input.
A displayed source variable likewise depends on its location at the selected PC;
unavailable is not proof of an uninitialized read.

## Read explicit byte ranges before trusting typed displays

GDB x/nfu specifies repeat count, display format and unit size. Its b/h/w/g units
are 1/2/4/8 bytes; a w unit is not the target's pointer width. Defaults can carry
over between commands. [5] LLDB memory read has explicit size, format and count
options; register read --all requests all register sets. [6]

Investigative consequence: preserve start address, total byte extent, architecture
and byte order. Use byte views for encoded data, then decode its actual format;
a native integer display does not change a wire field's endianness. A typed cast
or pretty-printed object does not prove the declaration matches the binary.
Check each access against the established object and initialized range, not merely
whether the debugger can display a mapped page.

## Module lookup provides association, not authentication

GDB info files identifies executable/core/symbol sources and section information;
info sharedlibrary reports shared-library information. LLDB image list and
image lookup --address associate images and locations. [6,7]

Investigative consequence: preserve module load addresses, matched debug artifacts
and code bytes. A familiar symbol or basename does not establish build identity.
Use format-debug-information-build-matching for PDB, build-ID and dSYM contracts;
format-disk-versus-loaded-image for file offsets versus loaded addresses. Generated
or modified code can need a separate captured code version and address map.

## GDB non-stop mode does not freeze all threads

In GDB non-stop mode, one thread can stop while others continue. Commands such as
continue normally affect the current thread; the all-thread variant is distinct.
Availability depends on the target. [8]

Investigative consequence: successive memory reads may observe different states
if another thread or external agent can mutate them. Record which execution agents
were stopped and when. Even stopping every thread of one process does not freeze
shared memory owned by another process or a device. An inconsistent display can be
a collection artifact; it is not automatically evidence of a target data race.

## Sources and scope

Reviewed 2026-10-02. Living manuals. Named commands identify interpretation rules,
not a required command sequence or permission to attach/run. Support varies with debugger build,
target backend and dump format. Workflow: playbook-validation-debugger-evidence.

1. [GDB inferiors](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Inferiors-Connections-and-Programs.html): execution representation, listing and selection.
2. [GDB threads](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Threads.html): debugger IDs, system IDs and selection.
3. [LLDB tutorial](https://lldb.llvm.org/use/tutorial.html): process status, thread selection and frame selection.
4. [GDB registers](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Registers.html): selected-frame restoration and unavailable volatile values.
5. [GDB memory examination](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Memory.html): units, formats and retained defaults.
6. [LLDB command map](https://lldb.llvm.org/use/map.html): register/memory inspection and image lookup.
7. [GDB files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Files.html): executable, core, symbols and libraries.
8. [GDB non-stop mode](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Non_002dStop-Mode.html): per-thread execution and target support.
