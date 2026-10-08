---
id: reference-validation-windbg-context-memory
title: Windows debugger process, exception and frame context for memory evidence
kind: reference
topics: [windbg, debugging, threads, exception-context, registers, memory, pdb, symbols]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Windows debugger context and memory interpretation

The contracts below are WinDbg-specific interpretations of recorded context,
indices and displays. They are not a required toolstack or a command sequence;
other debugging capabilities may expose the same evidence differently.

## WinDbg process and thread indices differ from Windows identifiers

In user-mode debugging, |s selects a debugger-numbered process and ~Ns selects
thread index N. The ~ listing shows debugger thread numbers separately from
Windows process/thread IDs. Its dot marks the current thread; # identifies the
exception thread or the thread active at attach. In kernel mode ~ denotes a
processor, not a user-mode thread selector. [1,2]

Investigative consequence: bind the index to the OS identity and current capture
before interpreting stack or operands. Do not pass an OS TID as if it were an
index. The # marker at attach does not establish that the thread caused a crash.
A kernel investigation requires its own process/address and register contexts;
user-mode command syntax is not a universal thread selector.

## Address space, register context and local frame answer different questions

WinDbg separates process/address context, saved register context and local stack
frame. .frame selects local scope. .cxr and kernel .trap/.thread can select saved
register contexts; this retrieves recorded state rather than writing CPU registers.
Only saved values are recoverable. The effective machine mode must agree with
the context. Execution or process/thread changes can reset selected contexts. [3]

Investigative consequence: record context-record address, architecture and frame
with the output. A plausible stack in the wrong context is not evidence about the
faulting thread. For mixed x86/x64 inspection, establish which mode the saved code
and registers represent rather than merely choosing the host's bitness. Changing
local scope is not a historical replay of every register at that call site.

## .exr exception details and .ecxr saved registers are distinct evidence

.exr ADDRESS displays an exception record; .exr -1 selects the most recent exception.
In the documented user-mode minidump case, .ecxr selects the associated exception
register context for subsequent register and stack inspection. [4,5]

Investigative consequence: preserve both the record and the context. The exception
code/parameters describe the event; the saved PC, registers and code describe the
operation. A dump captured later in error reporting may initially show a different
stack. Do not assume an exception stream exists in every dump or apply .ecxr as a
universal kernel trap-frame command. Failed context recovery leaves an evidence gap.

## WinDbg memory units and question marks need literal interpretation

db displays bytes, dw 2-byte units, dd 4-byte units and dq 8-byte units. dp uses
target pointer-sized units. Omitting a range can continue from the previous
display. Unavailable/invalid-address display can contain question marks. [6]

Investigative consequence: name address space, start, extent and unit explicitly.
Question marks are not zero bytes, an empty string or proof that a target load
would necessarily fault; dump coverage and selected context also matter. A pointer
display does not establish object type, owner or lifetime. For encoded buffers,
preserve raw bytes before interpreting multibyte fields or terminators.

## lm symbol status is not a complete PDB or code-integrity verdict

WinDbg lm reports module information and symbol status; verbose output includes
available image and symbol metadata. Missing/paged-out headers can limit it. [7]

Investigative consequence: verify module base/range, executable identity and PDB
association before using names, field offsets or source lines. Modern RSDS/PDB
matching requires the correct GUID and age, not merely a filename; details live
in format-debug-information-build-matching. Symbol success does not prove loaded
code is unmodified. Preserve forced/mismatched symbol loading as a limitation,
not a way to turn guessed types into target facts.

## Sources and scope

Reviewed 2026-10-02. The main workflow is Windows user mode; kernel distinctions
are included to prevent applying user-mode context rules to a different target.
Commands do not authorize live attachment or state changes. Workflow:
playbook-debugging-windows-native-validation and playbook-validation-debugger-evidence.

1. [WinDbg |s](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-s--set-current-process-) and [~s](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-s--set-current-thread-): current process/thread selection.
2. [WinDbg thread status](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/---thread-status-): IDs, indices and markers.
3. [WinDbg changing contexts](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/changing-contexts): address, register, machine and frame scopes.
4. [WinDbg .exr](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-exr--display-exception-record-): exception record and -1 selection.
5. [WinDbg .ecxr](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/-ecxr--display-exception-context-record-): saved exception registers and documented target scope.
6. [WinDbg display memory](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/d--da--db--dc--dd--dd--df--dp--dq--du--dw--dw--dyb--dyd--display-memor): units, ranges and unavailable bytes.
7. [WinDbg lm](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/lm--list-loaded-modules-): image metadata and symbol status.
