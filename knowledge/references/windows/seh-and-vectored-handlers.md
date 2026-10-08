---
id: reference-windows-seh-vectored-handlers
title: Windows SEH filters, termination handlers, vectored callbacks and exception records
kind: reference
topics: [windows, seh, veh, exceptions, filters, cleanup, control-flow]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows SEH filters, termination handlers, vectored callbacks and exception records

## Scope: recognition, unwinding and safe recovery are different claims

Reviewed 2026-10-02 against Microsoft Win32/MSVC contracts. This reference covers
native Windows structured exceptions and related handlers, not POSIX signals,
CLR exception policy or every language's finally construct. API-level facts do
not imply identical x86, x64 and ARM64 metadata layouts. See
`reference-windows-msvc-exception-cleanup-evidence` for compiler-mode and table
interpretation, and `abi-windows-x64` for machine unwind details.

For investigation, keep exception detection, filter search, selected handler,
unwind cleanup, resumption and process termination separate. Swallowing an access
violation does not repair corrupted state, undo earlier writes, validate an input
or authorize an operation. A first-chance debugger event is not automatically
an unhandled crash; preserve handler and debugger decisions as evidence.
[Debugger exception handling](https://learn.microsoft.com/en-us/windows/win32/debug/debugger-exception-handling).

## First chance describes dispatch order, not the first corrupting operation

In ordinary Windows debugger exception dispatch, the debugger has a first chance
before application handlers. If the exception remains unhandled, the debugger
gets another chance. This ordering does not identify the earliest invalid write
or guarantee the first notification is a fatal crash. Fail-fast is a distinct
path; do not invent an earlier application-handler search for it.

WinDbg break status controls when execution stops; handling status controls
whether the exception is treated as handled when execution resumes. These are
separate settings. Treating an exception as handled can bypass application
exception handling and change observed control flow. Preserve both settings and
the actual continuation decision when comparing traces. Merely choosing not to
stop is not the same claim as proving the application recovered safely.
[Debugger event control](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/controlling-exceptions-and-events).

## SEH filter -1 resumes, 0 searches and 1 enters the handler

In MSVC __try/__except, the filter is evaluated for an exception in the guarded
body or a called routine. EXCEPTION_CONTINUE_EXECUTION (-1) resumes at the
exception point; EXCEPTION_CONTINUE_SEARCH (0) searches outward;
EXCEPTION_EXECUTE_HANDLER (1) selects the __except body, after which execution
continues beyond it. Normal execution skips the handler. A filter function call
is part of selection, not evidence that the selected body already ran.
[try-except](https://learn.microsoft.com/en-us/cpp/cpp/try-except-statement?view=msvc-170).

RaiseException can mark an exception noncontinuable; attempting continuation
then raises EXCEPTION_NONCONTINUABLE_EXCEPTION. Even for a continuable exception,
the filter result does not prove resumption is safe. An unchanged faulting
instruction/data condition may fault again. A controlled software exception that
can resume is not proof that arbitrary memory-corruption faults are recoverable.
[RaiseException flags](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-raiseexception).

## Exception information must be captured in its valid context

MSVC GetExceptionInformation is an intrinsic usable in the filter expression.
It supplies EXCEPTION_POINTERS referring to the exception record and machine
CONTEXT. A helper called by the filter cannot independently call the intrinsic;
pass its result as an argument. GetExceptionCode can also be used in the handler.
[GetExceptionInformation](https://learn.microsoft.com/en-us/windows/win32/debug/getexceptioninformation),
[Intrinsic scope](https://learn.microsoft.com/en-us/cpp/cpp/try-except-statement?view=msvc-170).

The C++ syntax documentation warns the information is generally stack-backed
and unavailable after transfer to the handler. Preserve needed data while valid;
copying a pointer variable does not extend the pointee's lifetime. For deferred
logging, identify copied records/context and any nested pointers separately.
Use target-appropriate CONTEXT layout and validity flags instead of treating an
x64 host structure as every target's register snapshot. A saved address without
its lifetime and architecture is incomplete evidence, not a durable crash record.

## Faulting instruction address and inaccessible data address are distinct

For Windows EXCEPTION_RECORD, ExceptionAddress identifies where the exception
occurred; NumberParameters bounds defined ExceptionInformation entries. For an
access violation, information[0] distinguishes read 0, write 1 and DEP execution
violation 8; information[1] identifies the inaccessible address. For an in-page
error, information[2] additionally carries the underlying NTSTATUS. Verify code
and parameter count before using any of these meanings.

Other exception codes do not automatically use those slots the same way.
Software RaiseException arguments can be application-defined. ExceptionRecord
can chain nested records; the native structure contains pointer-width fields,
and explicit 32/64-bit forms exist for cross-architecture debugging.
Investigative implication: classify instruction location, accessed address and
underlying storage failure separately. An in-page failure need not be an
out-of-bounds access; an AV record alone does not identify the corrupting write
or prove exploitability.
[EXCEPTION_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-exception_record).

## __finally runs on scoped exits, not every way a process can stop

MSVC __try/__finally runs its termination block on normal fallthrough and exits
such as return/goto, and during applicable unwinding to an exception handler.
It does not itself catch the exception or stop handler search. An outer filter
can be evaluated before inner unwind cleanup; do not assume resources were
released before a filter inspects them.
[try-finally](https://learn.microsoft.com/en-us/cpp/cpp/try-finally-statement?view=msvc-170).

The guarantee is not process-exit cleanup: termination while inside the guarded
body, including ExitThread/ExitProcess, can bypass it. If no handler is selected,
do not invent a normal cleanup-to-catch path. Separate process termination from
ordinary scope exit in a resource audit. A resource release may be absent from
ordinary disassembly because it is an unwind target, but finding a finally block
does not prove it executes on every fatal path.
[Termination-handling limits](https://learn.microsoft.com/en-us/windows/win32/debug/termination-handling).

## AbnormalTermination true does not prove an exception occurred

Within MSVC __finally, AbnormalTermination is nonzero for exits such as return,
goto, break or continue leaving the guarded body, even though those statements
do not raise an exception. Fallthrough and __leave are normal for this purpose.
__leave transfers to the end of the guarded body and then its finally block;
it does not skip cleanup. Do not label every abnormal branch a hardware-fault
or security-error path.
[AbnormalTermination](https://learn.microsoft.com/en-us/windows/win32/debug/abnormaltermination).

Constructed investigative example: cleanup marks an operation failed whenever
AbnormalTermination is true, but a successful early return also reaches that
branch. Whether this is a logic bug depends on the intended status policy and
actual output effects. Preserve the exit reason separately from the cleanup
branch. Do not assume the source programmer intended abnormal to mean failed.

## VEH registration is not scoped to a stack frame or pinned DLL lifetime

Windows vectored exception handlers are not frame-based. They run after the
debugger's first chance and before stack unwinding; a debugger handling the
exception can change what the application observes.
[Vectored exception handling](https://learn.microsoft.com/en-us/windows/win32/debug/vectored-exception-handling).

AddVectoredExceptionHandler with nonzero First inserts ahead of existing handlers;
a later first insertion can change the order. Registration success returns a
token used to remove the handler. Unloading a DLL containing that handler does
not unregister it. A callback address in an unloaded image is therefore a
lifetime candidate, not proof that a later dispatch actually occurred.
[Registration and unload](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-addvectoredexceptionhandler).

Trace registration, removal, module/context retention and concurrent callbacks.
Do not infer a drain guarantee from a remove API name, or treat VEH as a local
__except attached to the nearest lexical function. Vectored continue-handler
registration is a separate API, not an alias for adding a VEH.

## VEH return values are not low-level EXCEPTION_DISPOSITION enum values

A Windows vectored exception callback returns EXCEPTION_CONTINUE_EXECUTION (-1)
or EXCEPTION_CONTINUE_SEARCH (0). Its documented contract does not include the
SEH filter's EXCEPTION_EXECUTE_HANDLER result. Microsoft advises avoiding
allocation and synchronization-object acquisition in these callbacks.
[VectoredHandler](https://learn.microsoft.com/en-us/windows/win32/api/winnt/nc-winnt-pvectored_exception_handler).

Installed MSVC 14.37.32822 `excpt.h`, inspected 2026-10-02, separately defines
the low-level EXCEPTION_DISPOSITION enum: ExceptionContinueExecution=0,
ExceptionContinueSearch=1, ExceptionNestedException=2, ExceptionCollidedUnwind=3.
Those are not the -1/0/1 filter constants. The same integer 1 means different
things for a language-level filter and a runtime exception routine. Identify
the actual callback signature/caller before decoding a return constant. A
generic decompiler label named handler is insufficient. These header constants
describe distinct return domains, not a complete runtime dispatch algorithm.

## A top-level unhandled filter is not a guaranteed safe reporting thread

SetUnhandledExceptionFilter replaces the process's existing top-level filter
for existing/future threads and returns the previous filter, not a success BOOL.
Its documented application callback runs if an exception reaches that filter
and the process is not being debugged. It executes on the faulting thread, whose
stack/state may already be damaged. A registered filter therefore does not prove
every fatal exception reaches healthy logging or recovery code.

Recover subsequent replacements, debugger state and the actual terminal path.
Do not mistake a NULL previous-filter return for failed installation. An import
or registration call alone does not establish a particular crash report was
written or an external side effect was rolled back.
[SetUnhandledExceptionFilter](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-setunhandledexceptionfilter).

## Fail-fast bypasses ordinary frame and vectored handlers

Windows 7+ RaiseFailFastException bypasses frame-based and vectored handlers,
terminates the application and invokes Windows Error Reporting when enabled.
It raises a second-chance exception and may involve debugging facilities.
Do not draw a normal SEH recovery edge through a surrounding __except or VEH
when this is the actual path.
[RaiseFailFastException](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-raisefailfastexception).

Investigation implication: separate deliberate invariant-failure termination
from an unhandled memory access. Neither automatically establishes attacker
reachability or memory corruption. Identify the check and state that led there;
do not assume normal destructors/finally blocks or application rollback ran.
This rule is for this fail-fast mechanism, not every function named fatal.

## __fastfail reason parameters matter more than a stack-buffer label

With native support on Windows 8+, user-mode __fastfail produces a noncontinuable
second-chance exception with code 0xC0000409. Its first exception parameter carries
the FAST_FAIL reason passed by the caller; ordinary exception handlers are not
invoked. Older systems without native support can report a different failure,
such as an access violation. This is the intrinsic's contract, not a claim that
every RaiseFailFastException call produces the same record.

Investigative consequence: preserve the reason parameter, caller and failed check.
The exception code or a debugger's stack-buffer-overrun label alone does not prove
a stack overwrite. Establish the actual invariant failure and antecedent state.
Do not infer which operation corrupted memory merely from the termination routine.
[MSVC __fastfail](https://learn.microsoft.com/en-us/cpp/intrinsics/fastfail?view=msvc-170).
