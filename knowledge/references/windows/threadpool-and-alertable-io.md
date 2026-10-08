---
id: reference-windows-threadpool-alertable-io
title: Windows thread-pool I/O accounting, callback drains and alertable completion routines
kind: reference
topics: [windows, overlapped-io, thread-pool, callbacks, cancellation, alertable-waits, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows thread-pool I/O accounting, callback drains and alertable completion routines

## Scope: distinguish three completion dispatch mechanisms

Reviewed 2026-10-02. These Microsoft contracts distinguish raw IOCP dequeue,
Windows Vista+ thread-pool I/O objects and ReadFileEx/WriteFileEx completion
routines on alertable threads. An imported callback address or OVERLAPPED pointer
does not select between them. Recover the registration, issue API, notification
configuration and thread/wait context.

Investigative inference: count separately accepted I/O, expected notifications,
queued/running callbacks and application references. Canceling one category may
leave others live. `reference-windows-iocp-packets-notification` covers raw
packets; `reference-windows-overlapped-io-lifetime-cancellation` covers underlying
request and buffer requirements. No thread-pool object name itself proves a
particular owner's lifetime is extended through callback return.

## StartThreadpoolIo arms notification accounting before each operation

For Windows thread-pool I/O, call StartThreadpoolIo before each asynchronous
operation on the bound handle. It announces expected I/O to the pool; it does
not itself issue the read/write. The callback can run after completion on a
worker, so a start placed after submission is not a safe ordering substitute.
The API documents ignored completions and memory corruption when the required
start notification is omitted.
[StartThreadpoolIo](https://learn.microsoft.com/en-us/windows/win32/api/threadpoolapiset/nf-threadpoolapiset-startthreadpoolio).

Investigation implication: follow wrappers and retry paths to match every start
with the corresponding issue attempt and eventual notification disposition.
Initialize application context before exposing the operation to completion;
establish reference retention for both the issuer and callback if they can
overlap. This is a proof obligation, not a claim that a particular target's
callback actually ran before its submission wrapper returned.

## CancelThreadpoolIo cancels a start notification, not underlying I/O

Windows CancelThreadpoolIo balances notification from StartThreadpoolIo. The
documented cases requiring it are an overlapped issue failure other than
ERROR_IO_PENDING, or immediate success with FILE_SKIP_COMPLETION_PORT_ON_SUCCESS
enabled, where the callback will not arrive. Pending submission is not the
first failure case; ordinary immediate success without that suppression is not
the second case.
[CancelThreadpoolIo](https://learn.microsoft.com/en-us/windows/win32/api/threadpoolapiset/nf-threadpoolapiset-cancelthreadpoolio).

Do not substitute this function for CancelIoEx when an actual pending request
must be canceled. Constructed bookkeeping model, not an API counter layout:
one start creates one expected-notification obligation; either a callback path
consumes it or an appropriate no-notification path cancels it. Canceling twice,
canceling after a callback has consumed it, or expecting a suppressed callback
requires investigation of the real ordering. Memory retained for the underlying
I/O is a separate obligation from this accounting.

## Canceling queued callbacks does not cancel pending kernel I/O

WaitForThreadpoolIoCallbacks waits for outstanding callbacks and can cancel
queued callbacks not yet begun. With fCancelPendingCallbacks=TRUE, pending I/O
requests themselves are not canceled. Before freeing OVERLAPPED, independently
establish I/O completion; CancelIoEx can request cancellation but is not that
completion proof. If callbacks normally release storage, suppressing them needs
an alternate proven cleanup path.
[WaitForThreadpoolIoCallbacks](https://learn.microsoft.com/en-us/windows/win32/api/threadpoolapiset/nf-threadpoolapiset-waitforthreadpooliocallbacks).

Investigation implication: do not infer request quiescence from the word Wait
or from TRUE in a callback-cancellation argument. Prevent new submissions and
identify the final owner of buffers, request records and application context.
Also inspect callback disassociation: the waiting API's accounting completion
can precede actual callback return, as described in the next section. Never
wait while holding a lock the outstanding callback needs without proving the
dependency can resolve.

## Disassociation can release a callback waiter before the callback returns

Windows DisassociateCurrentThreadFromCallback removes the executing callback
from the initiating object's active-callback accounting. If it was the last,
waiters for that object's callbacks may proceed while the callback continues.
The thread remains associated with the cleanup group until return to the pool;
cleanup-group synchronization is a different boundary.
[DisassociateCurrentThreadFromCallback](https://learn.microsoft.com/en-us/windows/win32/api/threadpoolapiset/nf-threadpoolapiset-disassociatecurrentthreadfromcallback).

Investigation implication: a returned WaitForThreadpoolIoCallbacks is not
unconditional proof that every callback instruction finished. After explicit
disassociation, track independently retained application state and any later
access to the original context, event, lock or DLL code. Releasing a waiter can
avoid a dependency cycle, but it does not create a reference to user data.
A safe callback may copy/retain what it needs before disassociating; establish
that evidence before reporting an early-free defect.

## CloseThreadpoolIo releases the completion object, not all application owners

Microsoft's CloseThreadpoolIo documentation advises closing the associated file
handle and waiting for outstanding overlapped operations before closing the
I/O object; no more overlapped operations may be started afterward. The object
is freed immediately without outstanding callbacks, or asynchronously after
they complete. Outstanding start-notification accounting may need cancellation
on the applicable no-notification paths.
[CloseThreadpoolIo](https://learn.microsoft.com/en-us/windows/win32/api/threadpoolapiset/nf-threadpoolapiset-closethreadpoolio).

Investigation implication: distinguish file handle, TP_IO object and user-owned
context. A close call is not a general-purpose callback join or proof that
externally queued work has released its references. Recover the actual shutdown
sequence, callback disassociation and failure cleanup. Arrange result observation
while required handles/state remain usable; this paragraph is not a recipe to
call GetOverlappedResult on an already closed file handle.

## ReadFileEx completion requires an alertable wait on the issuing thread

ReadFileEx queues/calls its completion routine when I/O finishes and the issuing
thread is in an alertable wait. Success from submission does not mean the routine
has run. A nonalertable wait does not deliver this callback merely because another
thread is alertable. hEvent is ignored by ReadFileEx and may be used by the
application; do not import ordinary ReadFile event-signaling assumptions.
[ReadFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfileex).

A decompiled wait loop must preserve the alertable flag and calling thread.
WAIT_IO_COMPLETION indicates completion-routine/APC delivery, not necessarily
completion of the specific request the caller wanted. Identify its request state
and loop condition. Distinguish this mechanism from a thread-pool I/O callback
running on a pool worker or a packet consumed through GetQueuedCompletionStatus.
The request and all callback-used context need an evidenced lifetime through
their respective last uses, not only until the data transfer ends.

## Completion routines can nest through alertable waits and have their own result

For ReadFileEx/WriteFileEx, FileIOCompletionRoutine receives error, byte count
and the original OVERLAPPED pointer. The system no longer uses that structure
after calling the routine, allowing the routine to release it if application
owners permit. Waiting routines need not be called in I/O completion order;
issuing more asynchronous I/O and entering alertable waits inside one callback
can nest calls and grow the stack.
[Completion-routine contract](https://learn.microsoft.com/en-us/windows/win32/api/minwinbase/nc-minwinbase-lpoverlapped_completion_routine).

Do not infer non-reentrancy from same-thread dispatch or release an enclosing
object while nested/user code still needs it. This API family documents a warning
case where callback dwErrorCode is zero but GetOverlappedResult fails with
ERROR_MORE_DATA: callback zero alone is not proof of a complete message.
Preserve operation type, status, returned length and framing. This is not a
universal error/byte-count rule for Winsock callbacks, IOCP or every device API.
