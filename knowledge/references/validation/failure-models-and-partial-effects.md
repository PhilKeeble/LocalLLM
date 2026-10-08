---
id: reference-validation-failure-models-partial-effects
title: Failure models, allocation errors, partial I/O, timeout and cleanup evidence
kind: reference
topics: [fault-injection, error-handling, allocation-failure, partial-io, cancellation, timeout, cleanup, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Failure conditions and the state they leave behind

## A failure model specifies more than an error return

For investigation, a failure model describes where work stops, what progress and
effects remain, how failure is reported, and what may happen afterward. Fault
injection deliberately substitutes such a condition at a chosen boundary. The
model can represent an API-permitted outcome or an explicitly stronger corruption
assumption; these support different claims about the original target.

Constructed example: allowing a resource acquisition to succeed, then replacing
its returned handle with a failure sentinel, can orphan an acquired resource.
That observation does not demonstrate a leak on an acquisition failure that
creates no resource. Preserve status, output validity, ownership, partial effects
and pending work together. A branch forced by an inconsistent result is evidence
about that intervention, not automatically a reachable application failure.

## Allocation failure must follow the selected allocator's contract

The standard C++ throwing single-object operator new forms return suitable
non-null storage or throw bad_alloc; the nothrow allocation forms can return null.
[1] A function name resembling new does not identify every custom wrapper's
failure policy. Returning null from the throwing form is not its specified
allocation-failure path.

For GNU libc realloc of a valid block to nonzero size, allocation failure leaves
the old block undisturbed and returns null. Zero-size behavior is a separate case.
[2] Thus a failure model must not also free the old block. Investigative questions
include losing the only pointer, increasing capacity metadata despite failure,
publishing a partially constructed object, and cleaning up resources that were
never acquired. Detailed ownership rules: reference-native-ownership-release-dangling.

## A short transfer is partial progress, not a generic failure

Linux read and write can succeed with fewer bytes than requested. Read's returned
count bounds the new input; write's count describes the transferred prefix. A
subsequent transfer can progress or fail. [3,4] Windows has operation-specific
status/count rules; use reference-windows-overlapped-io-lifetime-cancellation rather
than importing Linux sentinels into Win32 code.

Constructed input case: an eight-byte buffer receives three bytes. Returning
three while filling all eight with fresh data can hide a parser's unsupported
read of the remainder. Returning three after consuming eight source bytes can
also create an artificial stream gap. Track both buffer extent and source progress.
For output, resending an already transferred prefix can duplicate bytes. Whether
that duplicates an application action depends on framing and commit behavior.

## Error reporting can coexist with partial or delayed external effects

Linux write documents that a direct-I/O error need not mean nothing was written;
the affected file range can be inconsistent. A successful write also does not
alone establish durable storage. [4] These are scoped contracts, not permission
to invent partial effects for every failing API.

Investigative consequence: distinguish submission, transfer, publication, durability
and acknowledgement. An error model at one stage does not automatically describe
another. A post-commit lost response can leave the caller uncertain while the
effect already exists; a pre-submission rejection does not. Record the actual
stage before reasoning about retries, rollback or disclosure. Shared error text
does not make these states equivalent.

## Timeout, cancellation request and completion are distinct events

Windows WaitForSingleObject reports WAIT_TIMEOUT when its interval elapses with
the object nonsignaled. [5] That wait result is not a termination or rollback
operation on the work being awaited. CancelIoEx requests cancellation without
waiting for completion; final I/O can complete normally, be canceled or fail
otherwise. Its OVERLAPPED storage must remain valid until completion. [6]

Investigative consequence: a model that deletes pending work when the waiter times
out can hide late-use or duplicate-completion defects. Retain request generation,
buffers, owner and completion delivery separately. Conversely, fabricating a
completion forbidden by the actual API proves only behavior under that stronger
model. Use reference-concurrency-cancellation-completion-shutdown for lifetime
and application-quiescence distinctions.

## Transient, persistent and compound failures exercise different assumptions

SQLite documents one-shot and persistent simulated allocation/I/O failures, and
failures occurring during recovery from a prior crash. [7] These illustrate
different failure models; none establishes that all environmental combinations
have been covered.

Investigative consequence: an error handler may recover from one failed acquisition
but fail when its own allocation, logging, rollback or reconnect also fails. Record
which dependency remains unavailable and which calls are affected. A numbered call
position is meaningful only with the actual call sequence; another thread or an
earlier error can change what the same number selects. Bound retries, retained
resources and progress against the promised policy, not an assumed universal retry
count. Deliberate fail-stop behavior can be a valid contract.

## Cleanup and rollback have separate success and ownership contracts

An error response does not establish that state was rolled back. SQLite documents
COMMIT failures with SQLITE_BUSY that leave the transaction active; some other
errors undo a statement or the whole transaction depending on circumstances. [8]
That database contract does not roll back arbitrary external effects.

Investigative consequence: record acquired resources, transferred ownership,
published state and still-active transactions at each exit. Cleanup can itself
fail, overwrite the original status, release twice or leave state for the next
request. Do not retry every failed release indiscriminately: Linux close can
already have released the descriptor before reporting certain errors, as scoped
in reference-native-resource-lifetimes-results. Recovery after process loss is
also a different path from ordinary error returns.

## Failure-path evidence supports conditional behavior, not invented intent

For vulnerability analysis, connect the modeled failure to the required invariant
and the responsible operation: stale use, disclosure, wrong authority, duplicate
effect or unbounded resource retention. Distinguish a supported error-path defect
from the unresolved question of how an actor could induce its preconditions.

For malware analysis, failure may select a fallback destination, defer activation
or leave persistence work incomplete. Recover the actual branch, arguments and
effect. A branch exposed by forcing an unavailable dependency demonstrates a
conditional capability; it does not establish that the original specimen took
that path. Missing activity under failed prerequisites is not proof of benignness.

## Sources and scope

Reviewed 2026-10-02. Named API contracts retain their platform/runtime scope.
Constructed examples and failure-model consequences are analytical guidance.
Workflow: playbook-validation-error-path-investigation.

1. [C++ single-object allocation forms](https://eel.is/c++draft/new.delete.single): throwing versus nothrow allocation contracts.
2. [GNU libc changing block size](https://sourceware.org/glibc/manual/latest/html_node/Changing-Block-Size.html): nonzero realloc failure preserves the old allocation.
3. [Linux read](https://man7.org/linux/man-pages/man2/read.2.html): returned extent and partial success.
4. [Linux write](https://man7.org/linux/man-pages/man2/write.2.html): partial writes, direct-I/O error effects and durability limits.
5. [Windows WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject): WAIT_TIMEOUT meaning.
6. [Windows CancelIoEx](https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex): no-wait cancellation, eventual statuses and request-storage lifetime.
7. [SQLite anomaly testing](https://www.sqlite.org/testing.html): sections 3.1-3.4, one-shot, persistent, crash and compound failure models.
8. [SQLite transactions](https://www.sqlite.org/lang_transaction.html): sections 2.3 and 3, active transactions and error-dependent rollback.
