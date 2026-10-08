---
id: reference-validation-breakpoint-watchpoint-evidence
title: Resolved breakpoints, watched memory accesses and observation limits
kind: reference
topics: [gdb, lldb, windbg, breakpoints, watchpoints, memory-writes, debugging, observation]
platforms: [windows, linux, macos, freebsd, android, ios, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Breakpoint and watchpoint evidence

Interpret an observation point by its resolved location, trigger condition and
capture scope. GDB, LLDB and WinDbg contracts below illustrate real differences;
their command names identify those semantics, not a required execution recipe.

## GDB source and function breakpoints need resolved machine locations

GDB break accepts source/function locations, while break *ADDRESS names an explicit
instruction address. A source location can resolve to multiple code locations;
an unresolved location can remain pending under the configured policy. info
breakpoints reports location and state. [6]

Investigative consequence: retain the requested specification and the actual
instruction addresses. Source lines, overloads and inline copies are not necessarily
one physical operation. Check module identity and byte-level instruction boundaries
before crediting a hit. A function-entry breakpoint does not establish that its
sensitive instruction executed or that it returned successfully.

## An LLDB logical breakpoint can have zero or multiple resolved locations

LLDB distinguishes a logical breakpoint from its locations. A specification can
exist with zero matching locations and remain pending; a known location becomes
unresolved when its image unloads. Options can apply to the logical breakpoint or
individual locations. Its recorded location list and state distinguish the
logical request from the instructions actually monitored. [1]

Investigative consequence: a created breakpoint is not proof that the desired
instruction was monitored. Preserve resolved addresses, module identity, enabled
state, conditions and ignore counts. An overload, inline instance or same-named
symbol can create multiple candidates; identify the actual hit. No hit at a pending,
disabled or incorrectly resolved location does not refute reachability.

## WinDbg bp and bu have different module-reload behavior

WinDbg bp normally binds an address; if unresolved at creation it converts to bu.
bu retains a symbolic reference and survives module unload/reload. bm matches a
symbol pattern and normally creates bu-style breakpoints; bm /d instead fixes
addresses. These are software breakpoints, not memory-access watches. [2]

Investigative consequence: retain how an observation point was bound, not merely
its numeric ID. A reloaded module or generated-code replacement can invalidate a
previous address. A symbolic breakpoint can also resolve to a different build;
recheck code identity. Do not place a software instruction breakpoint in data to
watch writes: the documented bp/bm mechanism can corrupt that data. Use an
appropriate supported access watch with an explicit range instead.

## GDB watch reports value changes, not every store to an address

GDB watch stops when the expression's value changes. rwatch observes reads and
awatch reads/writes; the latter two require hardware support in the documented
implementation. Hardware width/slot limits can reject a watch, including when
execution resumes. watch -location watches the evaluated storage location. [3]

Investigative consequence: a same-value write may not appear as a value change.
Watching a pointer variable is not watching its pointee; a fixed-location watch
does not automatically follow replacement allocation. Record watched address,
width, expression, implementation and installation result. A hit is an access or
change observation, not proof that the operation exceeded bounds or used a dead
object. Establish those contracts independently.

## GDB software watchpoints have timing and thread-coverage limits

GDB software watchpoints single-step and re-evaluate an expression. They can report
a change at a later statement rather than the changing instruction, and may miss
changes made by a non-current thread. Hardware watchpoints avoid this specific
software limitation, subject to actual target support and restrictions. [3]

Investigative consequence: preserve the mechanism actually installed. A watchpoint
stop does not justify assigning the displayed source line as the first bad write
without inspecting instructions and stop semantics. Instrumented timing may change
a race; a non-reproduction under single-stepping does not rule out concurrent use.

## LLDB watchpoint output specifies the watched range and filters

LLDB watchpoint set variable selects a variable's storage. watchpoint list reports
address, size, enabled state and access type; conditions and ignore counts can
restrict stopping. The command map also documents watchpoint set expression for
an explicitly addressed region. [1,4]

Investigative consequence: read the installed range rather than infer it from a
source name. Preserve whether the watch follows pointer storage or a pointed-to
range, and whether the object remains the same generation. A filtered hit count
and the number of visible stops need not be equal. Do not assume GDB's value-change
semantics or WinDbg's access letters apply to LLDB without checking its command.

## WinDbg ba r means read or write, not read-only

WinDbg ba is a processor breakpoint: r observes reads/writes, w writes and e
instruction execution. Supported widths and alignment depend on architecture;
documented x86 widths are 1/2/4 bytes and x64 adds 8, while e requires size 1.
Hardware slots are limited. Overlap behavior is processor-dependent; the documented
x86 case triggers when access and watched ranges overlap. [5]

Investigative consequence: retain access type, range, process/thread restrictions
and actual trigger. A ba r hit is not proof of a read. Do not transfer the x86/x64
width table to ARM64 or assume an access must begin at the watched address.
The stopped PC's relation to the triggering instruction also needs the target's
debug-event semantics. These live watches do not recover a dump's past writes.

## Sources and scope

Reviewed 2026-10-02. Living debugger manuals; support depends on architecture,
remote backend and debugger build. These are evidence interpretation rules, not
instructions to alter a shared target. Workflow: playbook-validation-debugger-evidence.

1. [LLDB tutorial](https://lldb.llvm.org/use/tutorial.html): logical/resolved breakpoints and watchpoint status/conditions.
2. [WinDbg bp, bu, bm](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/bp--bu--bm--set-breakpoint-): address/symbol binding, reload and software breakpoint caveats.
3. [GDB watchpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Watchpoints.html): expression/location, hardware/software, access and thread limits.
4. [LLDB command map](https://lldb.llvm.org/use/map.html#watchpoint-commands): variable and addressed-region watches.
5. [WinDbg ba](https://learn.microsoft.com/en-us/windows-hardware/drivers/debuggercmds/ba--break-on-access-): access types, widths, alignment and overlap.
6. [GDB breakpoints](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Set-Breaks.html): explicit addresses, multiple locations, pending policy and status.
