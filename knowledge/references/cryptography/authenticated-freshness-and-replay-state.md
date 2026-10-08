---
id: reference-crypto-freshness-replay-state
title: Authenticated messages, freshness fields and anti-replay state
kind: reference
topics: [cryptography, replay, freshness, counters, timestamps, sessions, state]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Freshness and authenticated-message acceptance

## Authentication does not by itself establish a message is new

For analysis, a verified message can be authentic while repeating previously
accepted material. Freshness requires a separate relation to the receiver's
accepted context and state. The shared retry/replay model is in
reference-logic-retries-transactions-replay.

Bind authenticated bytes, key/principal/session, message identity and accepting
operation. A MAC/signature result or secure transport cannot alone prove at-most-
once application effects. Conversely, two messages or connections do not prove
duplicate effects. Preserve the actual retry/deduplication and commit behavior;
an acknowledgment needs its own semantic relation to the requested operation.

## Counters and timestamps require authenticated scope and trusted state

For investigation, determine which identity, operation and key generation a
freshness field belongs to, whether the field is authenticated and how the receiver
compares it with accepted state. Preserve width, units, reset, persistence and
concurrent acceptance conditions.

A monotonic-looking field is not a replay barrier if the consumer does not enforce
its meaning. A timestamp acceptance window also does not inherently exclude
multiple arrivals within that window. These are evidence questions, not a
universal counter algorithm. Missing state or clock provenance leaves freshness
unresolved; it does not supply proof of successful replay or a required timeout.

## TLS 1.3 early data has a specifically scoped replay limit

RFC 8446 states that TLS 1.3 0-RTT early data lacks inherent replay protection
and requires application-aware handling of replay/duplication. [1]

For investigation, establish that early data is enabled and that the relevant
application operation is accepted through it. Do not apply this limit to every
TLS record or infer that ordinary TLS guarantees application exactly-once effects.
Preserve server/cluster state, accepted message and actual effect. A protocol's
defined anti-replay mechanism does not prove a deployed implementation enforced
it, and a rejected early-data attempt does not establish a later retry's outcome.

## Rekey, reconnect and recovery can change freshness scope

For analysis, trace the key/session generation and retained anti-replay state
across reconnect, reset, failover and recovery. Identify which authenticated
context selects the receiver's accepted history.

A new connection is not automatically a new logical operation, and a new key ID
is not proof of distinct material or reset policy. State publication and the
sensitive effect need the promised consistency boundary; logging a request ID
does not alone establish it. Report accepted-state and effect evidence separately,
using the shared transaction/retry reference rather than inventing a universal
nonce-to-replay relationship.

## Source and scope

Reviewed 2026-10-08. RFC 8446 section 8 and appendix E.5 for early-data scope;
the generic freshness/state relations apply the existing logic reference.
No replay construction, live protocol interaction or timing-window recipe.

1. [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html): TLS 1.3 0-RTT versus application replay/duplication.

Workflow: playbook-crypto-operation-evidence. Nonce uniqueness for encryption is
a separate property in reference-crypto-nonce-iv-lifecycle.
