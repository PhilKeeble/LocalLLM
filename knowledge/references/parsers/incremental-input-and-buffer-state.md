---
id: reference-parser-incremental-input-buffer-state
title: Incremental parser input, buffered remainders and message completion
kind: reference
topics: [parsers, incremental-parsing, buffering, short-reads, llhttp, asio, websocket]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Incremental input and buffer state

## Winsock recv: no data, orderly end and connection reset differ

On a nonblocking Winsock socket, unavailable data produces SOCKET_ERROR with
WSAEWOULDBLOCK. On a connection-oriented socket, orderly peer shutdown followed
by exhaustion of received data produces zero bytes; connection reset produces
WSAECONNRESET. MSG_WAITALL can finish because of closure, cancellation or error,
not only a full buffer. It is not supported for nonblocking or message-oriented
sockets. [1]

Investigative inference: a parser must not turn would-block into end-of-message
or treat a requested receive size as the returned size. This is a Windows contract,
not a universal meaning of every zero result. For Linux read/write, use
reference-native-resource-lifetimes-results; for datagram truncation, use
reference-native-binary-protocol-framing-deserialization.

## llhttp execute success does not by itself mean message completion

llhttp_execute accepts partial or full HTTP input. HPE_OK means the supplied
input was consumed and parsed; message completion has a separate
on_message_complete callback. llhttp_finish reports end-of-input to the parser
and either completes a safely terminated message or reports an error. [2]

Investigative inference: distinguish successful progress from permission to use
a complete request. A header/body callback can precede later parse failure.
Recover when a sensitive operation commits and which completion condition gates
it. EOF semantics still depend on HTTP framing; do not infer that requests lacking
Content-Length are close-delimited. See reference-parser-stream-recovery-limits.

## llhttp pause, resume and reset are different state transitions

llhttp distinguishes HPE_PAUSED from HPE_PAUSED_UPGRADE and provides separate
resume functions. The caller must account for consumed input when resuming;
llhttp_get_error_pos identifies a position relative to the submitted buffer.
llhttp_reset preserves parser type, callbacks, user data and leniency settings. [2]

Investigative inference: resubmitting the whole buffer after partial consumption
can reinterpret bytes; clearing only parser state need not clear application
identity or accumulated fields. Recover the exact resume offset and retained
objects from the target API/build rather than guessing an off-by-one correction.
Parser reset is not proof of session reset or authorization revocation.

## Asio read-until may retain bytes after the matched delimiter

For Boost.Asio async_read_until with DynamicBuffer_v1 and a character delimiter,
successful completion reports the byte count through that delimiter. The dynamic
buffer can also contain later bytes. The operation can complete from data already
buffered without another underlying read. [3]

Investigative inference: using the whole buffer as one record can consume part of
the next record; clearing the whole buffer can lose it. Trace both the consumed
prefix and the retained suffix. A delimiter may also straddle receive calls in
a custom parser; a search only in the newest input does not establish a complete
search of the buffered stream.

## Asio asynchronous read ownership lasts through completion

The documented DynamicBuffer_v1 async_read_until overload leaves ownership of
underlying memory with the caller, which must keep it valid through the completion
handler. Other reads on that stream must not overlap this composed read operation.
A composed operation performs zero or more lower-level reads. [3]

Investigative inference: function return is not a buffer-release boundary.
Track buffer growth, compaction, retained field pointers and callback lifetime
separately. A live outer request object does not by itself establish that its
borrowed byte storage remains at the same address or retains the same contents.

## WebSocket frames are not always complete application messages

In RFC 6455 fragmentation, the initial data frame identifies text/binary type;
continuation frames use opcode zero, and FIN marks the final fragment. Control
frames can occur during a fragmented message but cannot themselves be fragmented.
Interleaving fragments of different messages requires a negotiated extension
that supports it. [4]

Investigative inference: retain message state across control frames without
appending their payloads as application-message data. Frame-length checks do not
alone bound accumulated message size. Recover negotiated extensions before
assuming the base framing rules describe the entire decoding pipeline.

## WebSocket UTF-8 validation has message scope

A WebSocket text frame can contain only part of a UTF-8 sequence; the complete
text message must be valid UTF-8. [4] This differs from formats requiring every
text chunk to be independently valid, such as CBOR indefinite-length text strings.
See reference-parser-container-boundaries-integrity for that separate contract.

Investigative inference: carry decoder state across the relevant fragment boundary
and distinguish incomplete sequence from invalid sequence. Do not label a capture
fragment malformed merely because it is not a whole decoded message. Conversely,
validity of a prefix does not establish validity of the final message.

## Primary sources and scope

Reviewed 2026-10-02: Microsoft Winsock recv, living llhttp documentation,
Boost.Asio latest reference (DynamicBuffer_v1 character-delimiter overload), and
RFC 6455 (2011) §§5.4-5.6. API examples illustrate contracts, not universal layouts.
Workflow: playbook-re-incremental-parser-state.

1. [Winsock recv return values and flags](https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-recv).
2. [llhttp API: execute, finish, pause/resume, reset and callbacks](https://llhttp.org/).
3. [Boost.Asio async_read_until, overload 1](https://www.boost.org/doc/libs/latest/doc/html/boost_asio/reference/async_read_until/overload1.html).
4. [RFC 6455: WebSocket fragmentation and data frames](https://www.rfc-editor.org/rfc/rfc6455.html).
