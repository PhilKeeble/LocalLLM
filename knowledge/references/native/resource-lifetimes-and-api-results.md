---
id: reference-native-resource-lifetimes-results
title: Handle and descriptor ownership, mapping lifetime, partial I/O and stale errors
kind: reference
topics: [resource-lifetime, handles, descriptors, mappings, locks, partial-io, errors]
platforms: [windows, linux]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Resource lifetimes and API results

## Resource identity and release contracts

Maintain an acquisition ledger: API, success sentinel, resource type, owning
scope, borrowed aliases, duplication/transfer, release function and pending
operations. Raw numeric equality does not establish identity after reuse.
Do not apply a memory allocator's lifetime rule to an OS handle, mapping or lock.
An error path must release only resources actually acquired, exactly as their
contracts require; absence of a release in one function is not a leak if ownership
was transferred to another evidenced owner.

For a candidate leak, count outstanding resources across repeated operations
and all cleanup paths. Link exhaustion to an actual limit and reachable workload;
one intentionally cached descriptor does not establish unbounded exhaustion.

## Linux dup shares the open file description, not descriptor flags

Linux dup creates a distinct descriptor referring to the same open file
description, sharing offset and file status flags. Descriptor flags such as
FD_CLOEXEC are separate. [1] Closing one descriptor is not the same as destroying
every reference to that underlying description.

## Linux close errors and reused descriptor numbers

Linux releases a descriptor early during close, including before some errors
are reported. Blindly retrying close after failure can close a reused descriptor
belonging to another operation. Do not export this Linux rule to every OS's
interrupted-close contract. [2]

Constructed investigation: a queued task retains integer fd=7, another path
closes it, and a later open reuses 7. The task may now act on the wrong object
without an invalid-descriptor error. Trace acquisition generation and ownership,
not just whether fd=7 is currently open.

## Windows handles have resource-specific release functions

CloseHandle applies to documented kernel handle types, not every Windows
resource. Search handles from FindFirstFile require FindClose, for example. [3]
DuplicateHandle creates another handle to the same object, not an independent
copy of its state. [4] Track which process owns each handle and who closes it.

## Windows mutex ownership belongs to a thread, not just a handle

A Windows mutex's ownership is associated with a thread. ReleaseMutex fails
when the caller does not own it, and recursive acquisitions require matching
releases. Closing a handle and releasing ownership are distinct operations. [5]
Investigate failed waits, early returns and exceptions before counting releases.
Do not infer lock protection merely from an imported wait/release function.

## Mapping lifetime is separate from a backing descriptor

On Linux, closing the descriptor used for a successful mmap does not invalidate
the mapping. munmap removes the mapping; accesses and aliases to that range need
separate lifetime tracking. [6] Closing a file is therefore not sufficient
evidence that a mapped pointer became stale, nor is a still-open file evidence
that an unmapped pointer remains valid.

Constructed investigation: a cache returns a borrowed pointer into a mapping,
then eviction unmaps it while a consumer remains active. Identify mapped range,
borrower lifetime and eviction synchronization. Track partial unmapping and
remapping of the same address separately. Apply platform-specific view/section
contracts when analyzing Windows rather than assuming mmap semantics.

## Linux short read initializes only the returned byte range

On Linux, successful read can transfer fewer bytes than requested. read
returns the bytes obtained, and -1 with errno on error; a positive short result
does not initialize the rest of the requested buffer. For a nonblocking socket,
would-block is reported with EAGAIN or EWOULDBLOCK, not as successful end-of-file.
A zero-count read can return zero without establishing end-of-file. [7]

Constructed scenario: a parser requests a 16-byte header, receives 5, then parses
all 16. Trace prior buffer contents and subsequent fields; distinguish stale
data consumption from a correctly buffered incremental parse. Preserve the signed
result until success is established before converting it to a buffer size.
Use reference-parser-incremental-input-buffer-state for incremental API contracts.

## Linux short write requires accounting for the transferred prefix

On Linux, a successful write can transfer fewer bytes than requested. Its positive
result is the transferred byte count, not proof that the whole request was written;
another write can transfer the remainder or fail. [8]

An error also does not universally mean zero progress: Linux direct-I/O writes
can leave partial data and an inconsistent affected range on failure. [8] Preserve
the I/O mode and exact result contract rather than assuming that retrying the
original request is equivalent to a first attempt.

Investigative inference: trace the remaining offset/count and preserved error
state. Resubmitting the original buffer can duplicate its already transferred
prefix. Whether this duplicates a logical operation depends on downstream framing
and commit behavior. A transport retry and an application-operation retry are
different; use reference-logic-retries-transactions-replay for the latter.

## errno must be interpreted through the API result contract

errno is meaningful according to the called API's result contract; a successful
call can change it. Some APIs use an ambiguous sentinel and require clearing
errno before the call. Do not treat any nonzero errno as proof that the last
operation failed. [9]

## GetLastError is meaningful only where the Windows API specifies it

Windows GetLastError must be read when the particular API documents it as
meaningful, immediately before another call can overwrite the thread's value. [10]
The mere presence of a nonzero thread error is not a substitute for interpreting
the operation's primary return value.

## Failure status and partial effects need separate evidence

Investigation: record primary return, output parameters, error code, partial
effects and cleanup return separately. Logging or cleanup can overwrite the
original error; a later successful cleanup must not turn a failed operation into
reported success. Conversely, failure status is not proof that no side effects
occurred. Confirm which outputs remain valid on every error path.

For conditional failure models and partial-state investigation, use
reference-validation-failure-models-partial-effects and
playbook-validation-error-path-investigation. A substituted error must be interpreted
with the ownership and effects that actually accompany it.

## Resource lifetime connects authority to observed malware behavior

For malware analysis, a resource-lifetime trace also connects authority to effects:
which object was actually opened, which operation used it and what completed.
Closing one descriptor/handle does not establish that every duplicate or mapped
view was destroyed. A stale numeric value may act on a replacement resource, not
necessarily fail. Use playbook-validation-allocation-lifetime-trace to separate
acquisition generation, retained references and observed use. A successful open
or a powerful imported API alone does not prove the subsequent behavior occurred.

## Sources: ownership and mappings

Reviewed 2026-10-02; Linux man-pages 6.19 and Microsoft API contracts. Examples
are constructed. Cross-platform concepts do not imply identical OS semantics.

1. [Linux dup](https://man7.org/linux/man-pages/man2/dup.2.html).
2. [Linux close](https://man7.org/linux/man-pages/man2/close.2.html).
3. [CloseHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-closehandle).
4. [DuplicateHandle](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle).
5. [ReleaseMutex](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-releasemutex).
6. [Linux mmap/munmap](https://man7.org/linux/man-pages/man2/munmap.2.html).

## Sources: results and errors

7. [Linux read](https://man7.org/linux/man-pages/man2/read.2.html).
8. [Linux write](https://man7.org/linux/man-pages/man2/write.2.html).
9. [errno](https://man7.org/linux/man-pages/man3/errno.3.html).
10. [GetLastError](https://learn.microsoft.com/en-us/windows/win32/api/errhandlingapi/nf-errhandlingapi-getlasterror).
