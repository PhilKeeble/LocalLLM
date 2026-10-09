---
id: vulnerability-parser-named-pipe-ipc-message-parsing
title: Named-pipe and IPC message parsing failure
kind: vulnerability
topics: [parsers, ipc, named-pipes, framing, partial-io, deserialization]
platforms: [windows, linux, macos, cross-platform]
architectures: [any]
---

# Named-pipe and IPC message parsing failure

## Definition and violated invariant

An IPC message-parsing vulnerability occurs when a receiver treats transport reads, buffers, connection state, or decoded objects as complete messages without enforcing the actual IPC mechanism's framing and identity contract. Every request must be assembled from exactly its transferred bytes, within one connection or peer generation, then decoded and authorized only after the complete application frame is established.

On Windows named pipes, pipe type, per-handle read mode, and wait mode are distinct. A client handle initially uses byte-read mode even for a message-type pipe. In message-read mode, `ReadFile` can return failure with `ERROR_MORE_DATA` after supplying part of one message; the remainder stays available. Byte-read mode does not preserve message boundaries. These rules do not transfer automatically to Unix-domain sockets, Mach messages, RPC, shared-memory queues, or other IPC mechanisms.

## Conditions that establish the issue

Recover pipe/socket/port type, handle mode, application framing, read and completion APIs, return and error handling, actual byte counts, buffer capacities, fragment accumulation, length arithmetic, connection generation, peer identity binding, decoder/type selection, request state, and dispatch. Prove attacker-influenced bytes are truncated, combined, padded with unwritten data, carried across peers, or deserialized under a broader contract, and connect the resulting object to a security-relevant operation.

Keep transport authorization separate from message parsing. A restrictive ACL does not make malformed messages safe, while parse control alone does not prove an untrusted principal can connect. For a privileged service, establish the actual peer or reachable lower-privilege writer as well as the parsing defect.

## Evidence that is not sufficient

A named pipe, IPC endpoint, short read, `ERROR_MORE_DATA`, fixed buffer, length field, serializer, or privileged server is not sufficient. The receiver may reassemble correctly, use a bounded incremental parser, authenticate each request, or reject incomplete input before effects.

One successful read is not universally one message. Conversely, a partial read is not universally an error: the correct conclusion depends on the transport and mode contract.

## Investigation sequence

Identify endpoint creation, security descriptor or peer credential policy, instance and connection lifecycle, then recover the exact read mode and completion contract. Build a byte ledger containing requested capacity, transferred bytes, accumulated bytes, declared frame size, parser-consumed bytes, remainder, and generation. Follow every error value that can carry valid bytes.

Trace reconnection, pooled state, overlapped or asynchronous completions, cancellation, and late callbacks. At the decoder, recover schema/type selection, nested lengths, callbacks, and whether any action occurs before full-frame validation. Bind authorization to the same peer and request generation that supplied the bytes.

## Constructed Windows named-pipe example

```c
DWORD got = 0;
BOOL complete = ReadFile(pipe, buffer, sizeof buffer, &got, NULL);
if (!complete && GetLastError() == ERROR_MORE_DATA)
    complete = TRUE;             /* wrongly treats a message prefix as complete */
if (complete)
    decode_and_dispatch(buffer, got);
```

In message-read mode, the `ERROR_MORE_DATA` branch can contain valid prefix bytes while the same message still has unread bytes. Dispatching that prefix is unsafe only if the application decoder accepts it and the resulting partial interpretation changes an operation or state; the error itself is not the vulnerability. In byte-read mode, even a successful read would not establish an application message boundary.

## Constructed x86-64 control-flow shape

```asm
; Illustrative shape after ReadFile. eax = BOOL result, [got] = bytes transferred.
test    eax, eax
jnz     .decode
call    GetLastError
cmp     eax, 234                 ; ERROR_MORE_DATA
jne     .fail
.decode:                         ; partial-message error is accepted as completion
mov     edx, dword ptr [got]
lea     rcx, [buffer]
call    decode_and_dispatch
```

This shape shows the partial-message status reaching a decoder; it does not prove exploitability or even that the handle is in message-read mode. Recover creation flags, `SetNamedPipeHandleState`, buffer lifetime, decoder behavior, and peer reachability before making those claims. The register use shown follows the Windows x64 integer-argument convention for this constructed call site.

## Primitive and impact limits

The direct primitive can be message-boundary confusion, partial-object use, cross-request state injection, stale-buffer disclosure, length-driven memory misuse, or attacker-selected deserialization. Privilege escalation requires a lower-authority peer and a privileged operation whose authorization or parameters the defect changes. Remote code execution requires remote reachability plus a concrete execution-capable sink or memory-corruption path.

## Related knowledge and primary sources

`reference-windows-named-pipe-security-identity` and `reference-native-binary-protocol-framing-deserialization` define transport, identity, and framing facts. This profile repeats the Windows partial-message and byte-mode distinctions locally.

Reviewed 2026-10-09 against Microsoft [Named Pipe Type, Read, and Wait Modes](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-type-read-and-wait-modes), [`ReadFile`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile), [Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights), and [`ConnectNamedPipe`](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-connectnamedpipe). The code and assembly are constructed.
