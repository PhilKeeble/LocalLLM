---
id: reference-windows-overlapped-io-lifetime-cancellation
title: Windows overlapped I/O results, request storage and cancellation scope
kind: reference
topics: [windows, overlapped-io, completion, cancellation, buffers, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows overlapped I/O results, request storage and cancellation scope

## Scope: submission, I/O completion and application quiescence differ

Reviewed 2026-10-02 against Microsoft Win32 contracts linked below. These facts
concern user-mode overlapped file/device APIs, not a universal contract for
Winsock, kernel IRPs, Windows Runtime tasks or every asynchronous wrapper.
Record exact API, handle type/open flags, notification mode and OS build.

For investigation, distinguish submission return, terminal I/O result, event or
packet delivery, callback execution and last application use. A completed I/O
can leave a queued callback or worker still referring to its enclosing object.
The associated buffer, OVERLAPPED, callback context and owning connection can
have different lifetimes. `reference-windows-iocp-packets-notification` covers
raw completion ports; `reference-windows-threadpool-alertable-io` covers thread
pool and completion-routine mechanisms. Generic race proof obligations remain
in `reference-concurrency-cancellation-completion-shutdown`.

## An OVERLAPPED is per-request state, not a reusable scratch argument

For Win32 OVERLAPPED, initialize unused fields to zero and provide a distinct
structure for each outstanding operation. Do not reuse it before that operation
completes. Internal and InternalHigh are system-managed status/count fields;
the union's Pointer is reserved, not a general application context slot.
Recover field widths/layout from the target ABI rather than using host offsets.

Offset and OffsetHigh form a 64-bit byte position on offset-capable handles;
overlapped I/O does not automatically advance those fields. Nonseeking operations
do not acquire file-offset semantics because the structure contains those names.
hEvent is separate from the data buffer and owning object. A wrapper can embed
OVERLAPPED inside a larger request; a recovered pointer then need not be the
allocation base. Prove the containing-object adjustment before assigning cleanup.
[OVERLAPPED contract](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped).

## ReadFile FALSE with ERROR_IO_PENDING is not an ordinary failed read

For ReadFile on a FILE_FLAG_OVERLAPPED handle, a valid unique OVERLAPPED is
required. FALSE plus ERROR_IO_PENDING means asynchronous completion is pending;
TRUE means success, not a guarantee that no completion notification will follow.
Other results need the API's error/partial-transfer rules. A non-NULL OVERLAPPED
alone does not prove the handle was opened asynchronously, and an overlapped
handle does not guarantee the issuing call never blocks.

Retrieve GetLastError in the relevant return branch before unrelated calls can
overwrite it. ReadFile's immediate byte-count output is not the general async
completion count; recover the eventual result through the selected completion
mechanism. The documented Windows 7 restriction on a NULL byte-count parameter
is version-specific, not a current universal non-NULL rule. Follow handle creation
and wrapper logic rather than labeling every FALSE branch a rejected request.
[ReadFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile).

## Buffer lifetime is independent of the lifetime of a pointer variable

Win32 ReadFile requires its receive buffer to remain valid and unused by the
application until the read completes. WriteFile's source buffer must remain
valid; do not modify, reallocate or free it while the write uses it. An issuing
function returning after pending submission does not end those obligations.
[Read buffer](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile),
[Write buffer](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile).

Investigative inference: a live heap request does not retain a stack buffer or a
resizable container's previous allocation unless its ownership actually does so.
Trace the buffer allocation and all aliases separately from OVERLAPPED. A stack
request is not inherently wrong if its scope demonstrably extends through all
required uses; a heap request is not inherently safe if a timeout frees it early.
After I/O completes, later parsing/sending callbacks may impose longer application
retention. Establish the last consumer instead of freeing from an API name alone.

## GetOverlappedResult polling reports ERROR_IO_INCOMPLETE, not IO_PENDING

For GetOverlappedResult, FALSE with ERROR_IO_INCOMPLETE and bWait=FALSE means
the specified operation is still pending. With bWait=TRUE it waits if pending.
Use the same handle and OVERLAPPED supplied at initiation. A failed query/result
must be interpreted before using its output count as received data.

Its transferred-byte result has operation-specific meaning: bytes read/written
for transfers; output bytes for DeviceIoControl; bytes read for TransactNamedPipe.
For ConnectNamedPipe and WaitCommEvent that count is undefined. A successful
connection completion therefore does not establish an initialized message length.
Keep operation kind in a generic request dispatcher, not only a void pointer
and a count. A nonblocking check returning incomplete is not a timeout policy,
terminal error or authorization to reclaim pending storage.
[GetOverlappedResult](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult).

## Event signaling must be tied to the particular operation

For event-based Win32 overlapped I/O, a dedicated manual-reset event avoids the
documented auto-reset pitfall where one wait consumes the signal and a later
blocking GetOverlappedResult can stall. With NULL hEvent the file handle can be
used for signaling, but concurrent operations on that handle make it ambiguous
which request caused the signal. Do not infer every request on the handle is done.
[Event selection](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/ns-minwinbase-overlapped),
[Shared-handle ambiguity](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getoverlappedresult).

An event wakeup and successful transfer are different questions: retrieve the
specific result and apply the correct byte-count contract. Notification modes
and ReadFileEx have different event rules; the mere presence of hEvent in a
decompiled structure does not prove which mechanism consumes it. References:
`reference-windows-iocp-packets-notification` and
`reference-windows-threadpool-alertable-io`.

## CancelIo and CancelIoEx select different sets of outstanding operations

Win32 CancelIo targets overlapped operations issued by the calling thread for
the specified handle, not operations issued by other threads. On a handle not
opened with FILE_FLAG_OVERLAPPED it does nothing. Its success reports a requested
cancellation, not a completed drain; normal completion notifications still occur.
[CancelIo](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelio).

CancelIoEx can target operations issued by other threads in the current process.
NULL lpOverlapped selects outstanding operations for the handle; a non-NULL
value narrows selection to that request identity. Neither form is a future
submission barrier. The existing `reference-concurrency-cancellation-completion-shutdown`
contains the no-wait, ERROR_NOT_FOUND and final-result distinctions. Keep those
rules when reviewing a cross-thread timeout or shutdown path; replacing CancelIo
with CancelIoEx does not itself prove safe reclamation.
[CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex).

## CancelSynchronousIo names a thread, not a file or a logical request token

Windows Vista+ CancelSynchronousIo targets pending synchronous I/O from the
specified thread; the thread handle requires THREAD_TERMINATE access. It does
not terminate that thread and does not wait for canceled operations to finish.
The eventual operation can succeed, abort with ERROR_OPERATION_ABORTED or fail
another way. The access-right name is not the action performed.
[CancelSynchronousIo](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelsynchronousio).

Microsoft warns that cancellation can race with a thread advancing to another
operation, especially a reused worker. For CancelIoEx(NULL), concurrent new
submissions can escape a cancellation sweep. Not every driver/operation supports
cancellation. Investigation implication: identify admission control, request
generation and the actual issue/cancel schedule. An expired timer associated
with old work is not sufficient identity for whatever the thread is doing now.
[Cancellation considerations](https://learn.microsoft.com/en-us/windows/win32/fileio/canceling-pending-i-o-operations).

## Partial transfer evidence is not the requested buffer capacity

Win32 completion byte counts need the specific operation's result semantics.
For example, ReadFileEx starting before EOF can succeed with fewer bytes than
requested; starting at/beyond EOF has its own error result. A successful
WriteFile on a nonblocking byte-mode pipe can likewise write fewer bytes than
requested. These are scoped examples, not a claim that all handle types share
EOF, message-boundary or short-write behavior.
[ReadFileEx file bounds](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfileex),
[WriteFile pipe counts](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-writefile).

Constructed investigation: a 4096-byte receive allocation with a valid 24-byte
result does not make the remaining 4072 bytes initialized input. Recover how
status, transferred length, framing and subsequent retry/parse logic interact.
Zero bytes is not a universal disconnect indicator across all devices. A short
result alone is not a vulnerability; a later unsupported read, disclosure or
state transition needs its own feasible path.
