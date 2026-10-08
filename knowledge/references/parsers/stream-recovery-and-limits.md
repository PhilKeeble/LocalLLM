---
id: reference-parser-stream-recovery-limits
title: Stream parser EOF, resynchronization, timeouts and buffering limits
kind: reference
topics: [parsers, incremental-parsing, resynchronization, timeouts, backpressure, http, json-sequences, libevent]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Stream recovery and limits

## HTTP/1.1 EOF does not delimit request bodies

RFC 9112 does not use connection closure to delimit request bodies. A request
with neither applicable transfer coding nor Content-Length has no body.
Some responses use closure for delimitation, but closure cannot distinguish a
successfully finished close-delimited response from interruption. [1]

Investigative inference: record request/response role and framing branch before
interpreting EOF as success. Calling a parser's finish function is not evidence
that the application received the intended content. See
reference-parser-framing-normalization-differences for length-delimited cases.

## HTTP/1.1 connection reuse requires consuming the current body

A server must read the complete request body or close the connection after
responding; otherwise remaining bytes can be mistaken for the next request.
A client intending to reuse a connection must consume the complete response
body. [1]

Investigative inference: an early rejection of a request is not automatically a
safe reset to request-line parsing. Follow remaining body bytes and the actual
connection close/reuse path. Distinguish a protocol-supported recovery from a
heuristic scan for something that looks like the next message.

## JSON text sequences have an explicit resynchronization marker

RFC 7464 encodes UTF-8 JSON texts with RS (0x1E) before each text and LF after it.
Raw RS cannot appear inside conforming JSON text; a string can represent it only
through escaping. Sequence parsers should recover from malformed elements by
skipping to the next RS. [2]

This recovery contract is not general permission to scan arbitrary binary payloads
for a magic byte. Investigative inference: establish that the proposed marker is
unambiguous in the current grammar and encoding. Resynchronization discards data;
it does not prove the skipped operation was harmless or never partially executed.

## JSON sequence scalar termination detects possible truncation

RFC 7464 requires trailing JSON whitespace for non-self-delimited top-level
numbers and true/false/null candidates, dropping elements that might have been
truncated without it. An incremental parser can also emit partial results before
later reporting malformed input. [2]

Investigative inference: a decoded numeric prefix is not necessarily the complete
intended number. Track which callbacks have produced data versus which boundary
confirms the whole element. If an application acts on provisional fields, recover
its validation/commit contract; final parse failure does not reverse prior effects.

## Libevent read timeout is not a total-message deadline

Libevent bufferevent read/write timeouts concern periods without successful I/O
while that direction is trying to operate. Read timeout is inactive when reading
is disabled or the input buffer reaches its high-water mark; write timeout is
inactive when writing is disabled or there is no output to send. [3]

Investigative inference: a configured I/O timeout does not prove bounded total
time for a peer to finish a message. Identify timer start, reset, pause and expiry
conditions. Distinguish an idle timeout from an absolute deadline and from limits
on bytes or work; progress under one criterion need not satisfy the others.

## Libevent input watermarks control reading, not every resource

A bufferevent read high-water mark suspends reading until enough buffered input
is drained; a zero high-water mark means unlimited. On I/O timeout, the relevant
read/write direction is disabled and the event callback receives timeout plus
direction flags. [3]

Constructed integration risk: an application waits for a whole record larger than
its read high-water mark without consuming input or rejecting that size. Reading
can stall before the record is complete. Check actual configuration and drain/error
paths; a watermark alone is not a whole-message limit, global quota or proof that
timeout cleanup releases connection state.

## Reconnect does not automatically reset application parser state

Analytical lifecycle distinction: replacing a transport handle and replacing the
object that owns parser buffers are different operations. Constructed example:
a pooled connection object retains a partial length prefix, buffered body bytes
or an authenticated flag when assigned to a new connection.

Trace initialization, disconnect cleanup, pool return and late callbacks using
the same object generation. Some protocols intentionally resume logical sessions;
prove the promised identity/resumption rules before calling retained state a bug.
Use reference-concurrency-cancellation-completion-shutdown for late completions
and reference-logic-retries-transactions-replay for repeated-operation effects.

## Primary sources and limits

Reviewed 2026-10-02: HTTP RFC 9112 (2022), JSON text sequences RFC 7464 (2015),
and the Libevent book's bufferevent documentation. Libevent backend/version
details still require target evidence; these rules do not specify every event
library. Workflow: playbook-re-incremental-parser-state.

1. [RFC 9112 §§6.3 and 9.3: framing and connection persistence](https://www.rfc-editor.org/rfc/rfc9112.html).
2. [RFC 7464 §§2-3: sequence syntax, recovery and truncation](https://www.rfc-editor.org/rfc/rfc7464.html).
3. [Libevent bufferevents: watermarks and read/write timeouts](https://libevent.org/libevent-book/Ref6_bufferevent.html).
