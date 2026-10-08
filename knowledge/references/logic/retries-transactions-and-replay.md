---
id: reference-logic-retries-transactions-replay
title: Retry ambiguity, idempotence, replay and transaction boundaries
kind: reference
topics: [logic-bugs, retries, idempotence, replay, transactions, recovery]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Retry ambiguity, idempotence, replay and transaction boundaries

## Scope and ambiguous completion
Reviewed 2026-10-02. General examples are constructed; HTTP, TLS and SQLite facts
are separately scoped below. A lost response does not determine whether the
server applied the request. Constructed sequence: server commits a charge,
connection closes before acknowledgement, client retries and server charges
again. Reliable transport within one connection does not deduplicate application
requests across retries or reconnects. A timeout is an observation by the waiter,
not proof of rollback or cancellation at the executor.

Repeated operations are distinct from duplicate fields inside one encoded message.
For the latter's replacement/merge rules, use
reference-parser-duplicate-fields-decoded-values.

## Idempotence is about the intended effect
RFC 9110 §9.2.2 defines HTTP idempotence in terms of repeated identical requests
having the same intended server effect as one request. It does not require
identical responses or prohibit per-request logging. PUT and DELETE have
idempotent method semantics; automatic retries of non-idempotent requests need
knowledge that the operation is safe to repeat or was not applied. [1]

Binary-investigation inference: a method label, retry flag or function name is
not proof the implementation satisfies that contract. Replacing state with a
specified value differs from incrementing it. A repeatable operation can still
be unauthorized, and an idempotent write can overwrite a newer intervening
version unless the protocol requires and enforces an appropriate precondition.

## Deduplication keys and exactly-once claims
Constructed deduplication invariant: one logical request identity causes at most
one committed sensitive effect, with defined handling of retries. A request ID
alone does not establish it. The lookup, reservation of that ID, effect and
durable result must satisfy the promised failure/concurrency semantics.

Check key scope (principal, tenant, operation), binding to request content,
in-progress behavior, expiration, restart recovery and concurrent duplicates.
Reusing a key with different payload must not silently authorize an unrelated
effect. Recording done before effect can lose work; recording done after effect
without atomic coordination can repeat work after a crash. Exactly-once effects
need a stated failure model and coordination boundary, not merely an ACK or UUID.

## Replay versus legitimate retry
A replay reuses previously accepted message material; a retry repeats a logical
operation because its result is unknown. Either can duplicate effects. A valid
MAC/signature proves neither freshness nor uniqueness by itself. Application
anti-replay state needs scope, lifetime and reset behavior appropriate to the
operation; timestamp acceptance windows permit multiple arrivals within a window
unless another mechanism excludes them.

TLS 1.3 0-RTT specifically lacks inherent replay protection; RFC 8446 §8 also
separates early-data replay from application duplication induced by client retries.
[2] Do not generalize that limitation to every TLS record or assume ordinary
TLS provides application-level exactly-once execution. Recover the actual early
data setting and application retry/deduplication behavior before making a claim.
Concrete early-data forwarding, HTTP 425 and HTTP/2 processing-boundary signals
are in reference-parser-protocol-replay-error-scope. Those scoped protocol signals
must not be inferred from arbitrary timeouts or reset errors.

## Atomic commit has a defined boundary
SQLite's atomic-commit explanation describes all-or-none database changes within
a transaction, with separate mechanisms for rollback-journal and WAL modes and
explicit storage assumptions. [3] It is not a guarantee that arbitrary external
effects are rolled back with SQL.

Constructed example: handler sends a device command, then its database transaction
rolls back. The physical command is not undone merely because the database is
consistent. Conversely a database commit followed by failed notification can
leave committed state with an unaware client. Record which participants and
effects belong to the transaction, what is visible before commit, and which
compensation actions can themselves fail or be repeated.

## Errors do not imply one universal rollback outcome
SQLite COMMIT returning SQLITE_BUSY can leave the transaction active for later
retry. Certain other errors can roll back a statement or a transaction depending
on circumstances; the connection's transaction state must be determined. [4]
Do not treat all non-success database results as committed or all as rolled back.

For a binary using a transaction library, recover exact API/result semantics,
connection identity, transaction lifetime and error handling. Constructed bug:
caller returns a pooled connection after failed commit while its transaction
remains active; a subsequent client inherits state. This requires evidence of
the actual failure and pool reset behavior, not merely a COMMIT import.

## Recovery and compensation invariants
Constructed multi-step install: reserve space, write staged object, publish it,
record completion, release reservation. For failure between each pair, distinguish
recoverable private state from published partial state. A compensation operation
can restore accounting without undoing disclosure, execution or an external
notification. Crash recovery may replay work that ordinary error cleanup would
skip; both paths belong to the operation's semantics.

Evidence should identify persistent markers, ordering/durability assumptions,
recovery parser, duplicate handling and the source of truth after disagreement.
A durable journal entry is not proof the referenced payload was durably written.
Do not infer power-failure guarantees from successful normal process-exit tests.

## Primary sources
Reviewed 2026-10-02. HTTP RFC 9110 (2022), TLS RFC 8446 (2018), SQLite current
documentation; match deployed SQLite version, journal mode and VFS separately.

1. [RFC 9110 §9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2).
2. [RFC 8446 §8](https://www.rfc-editor.org/rfc/rfc8446.html#section-8).
3. [SQLite atomic commit](https://sqlite.org/atomiccommit.html).
4. [SQLite transactions and errors](https://www.sqlite.org/lang_transaction.html).
