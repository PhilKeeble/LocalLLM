---
id: reference-windows-iocp-packets-notification
title: Windows IOCP packet identity, result decoding and notification suppression
kind: reference
topics: [windows, iocp, overlapped-io, completion, dispatch, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows IOCP packet identity, result decoding and notification suppression

## Scope: completion ports carry packets, not only successful file transfers

Reviewed 2026-10-02 against the linked Microsoft Win32 API contracts. An input/output
completion port (IOCP) consumer can receive real I/O results and application-posted
control/work packets. Recover packet producers before treating every key/pointer
pair as a file request. Posted-packet behavior does not establish the result of
actual device I/O. Examples are constructed, not observations of a vulnerable target.

Use `reference-windows-overlapped-io-lifetime-cancellation` for request/buffer
contracts and `reference-windows-threadpool-alertable-io` for APIs that manage
notification differently. A completion-port import alone is not proof that the
particular operation is associated with it or that notifications are enabled.

## Completion keys identify handle association, not a unique operation

CreateIoCompletionPort associates an overlapped-capable handle with one port;
the association lasts until that handle is closed. Many handles can share a
port. CompletionKey is an application-defined ULONG_PTR attached at association,
whereas the operation's OVERLAPPED pointer distinguishes individual requests.
A key is not inherently an owning reference or a security identity.

When associating with an existing port, NumberOfConcurrentThreads is ignored;
it is a creation setting. Zero at creation selects processor-count concurrency.
The ordinary API port is process-associated, not a cross-process endpoint to
identify solely by a numeric handle. ReadFileEx/WriteFileEx use another completion
mechanism and cannot use a handle after it is associated with an IOCP.
[CreateIoCompletionPort](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-createiocompletionport).

Inference: casting a 64-bit ULONG_PTR key through DWORD can truncate a stored
pointer/token. Prove the target width and actual key use before diagnosing it;
an intentionally small integer key is not a pointer-truncation defect.

## GetQueuedCompletionStatus FALSE can still dequeue a failed request

For Win32 GetQueuedCompletionStatus, decode BOOL together with returned
*lpOverlapped, then the relevant error:

- FALSE and NULL: no packet dequeued; byte count and completion key are
  indeterminate. A timeout is not a completed failed request.
- FALSE and non-NULL: a failed I/O packet was dequeued; GetLastError supplies
  that operation's error. Its request still needs the appropriate completion path.
- TRUE: a packet was dequeued; classify its producer before treating its fields
  as a successful device transfer. Application-posted packets can have NULL.

Do not skip cleanup of failed I/O merely because BOOL is false, or dereference
an old request variable after a no-packet return. Port closure while waiting
returns ERROR_ABANDONED_WAIT_0/NULL under the documented modern behavior;
XP/Server 2003 instead continue waiting until a packet or specified timeout.
[GetQueuedCompletionStatus](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getqueuedcompletionstatus),
[Posted packets](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-postqueuedcompletionstatus).

## Immediate success can notify unless skip-on-success is actually enabled

SetFileCompletionNotificationModes with FILE_SKIP_COMPLETION_PORT_ON_SUCCESS
suppresses the otherwise-generated packet only when the handle is associated
with a port, opened asynchronously, and the request succeeds immediately. It
does not suppress an operation that first returns pending and later succeeds.
Confirm the configuration call succeeded; configured modes cannot be removed
from that handle. Socket compatibility has additional IFS-provider restrictions.

FILE_SKIP_SET_EVENT_ON_HANDLE is different: it suppresses file-object event
signaling for immediate success or a nonsynchronous function returning pending;
an explicit request event is still signaled. Do not infer IOCP packet suppression
from this second flag.
[Notification modes](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setfilecompletionnotificationmodes).

Separately, a valid OVERLAPPED hEvent with its low bit set prevents that request
from enqueueing an IOCP packet. This is per-request suppression, not a second
name for skip-on-immediate-success. Recover both mechanisms before predicting
which branch owns terminal processing.
[hEvent low-bit rule](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getqueuedcompletionstatus).

## PostQueuedCompletionStatus does not validate an OVERLAPPED-shaped payload

Windows PostQueuedCompletionStatus posts the supplied byte-count, completion-key
and pointer values for a consumer. The system does not validate their meaning;
the pointer need not address an OVERLAPPED structure. NULL or a sentinel can be
an intentional application protocol. The apparent byte count need not measure
any actual transfer. A successful dequeue is therefore not provenance proof.
[PostQueuedCompletionStatus](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-postqueuedcompletionstatus).

Investigation implication: enumerate internal posts, shutdown markers and real
I/O producers; recover discrimination before a containing-record conversion or
free. A collision is a candidate only if both packet classes reach the same
unsafe interpretation. Also identify who can access/post to this port; the
ability to call an API somewhere in the program is not proof of attacker control
or a cross-process injection path.

## GetQueuedCompletionStatusEx success is batch retrieval, not all-I/O success

Windows Vista+ GetQueuedCompletionStatusEx returns an array and the number of
entries actually removed. A TRUE result can include failed I/O operations;
inspect each real operation's status rather than applying one GetLastError to
the batch. Iterate the returned count, not the allocated array capacity. FALSE
means no operation was dequeued, not that every outstanding request failed.

With fAlertable=TRUE an otherwise waiting thread can execute a queued I/O
completion routine or APC. Do not treat every wake/return as an entry-bearing
batch; check the result/count contract. Posted control packets still need their
own classification before following lpOverlapped. A bulk dequeue does not join
other workers or make all associated request storage reclaimable.
[GetQueuedCompletionStatusEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-getqueuedcompletionstatusex).

## FIFO enqueueing and a concurrency limit do not serialize application effects

Windows IOCP queues packets FIFO and releases waiting workers in LIFO order;
the documentation warns packets may be dequeued in a different order. Running
workers and their application effects must not be inferred to follow submission
order. The concurrency value regulates runnable associated workers, not an
application-wide critical section or a per-connection ordering protocol.
[IOCP scheduling model](https://learn.microsoft.com/en-us/windows/win32/fileio/i-o-completion-ports).

Investigative inference: even a nominal single-worker design needs examination
of waits, other threads, timers, nested callbacks and new submissions. A worker
can delegate work or retain an object beyond dequeue. A shutdown sentinel or
empty queue does not prove all I/O, workers or delegated consumers have drained.
Prove the target's ordering and retention mechanism for each shared resource,
rather than using the port's queue terminology as a lock proof.
