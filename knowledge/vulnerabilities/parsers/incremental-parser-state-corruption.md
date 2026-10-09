---
id: vulnerability-parser-incremental-state-corruption
title: Incremental parser state corruption across fragments, retries, or reset
kind: vulnerability
topics: [parsers, incremental-parsing, fragments, retries, reset, buffering]
platforms: [cross-platform]
architectures: [any]
---

# Incremental parser state corruption across fragments, retries, or reset

## Definition and violated invariant

An incremental-parser vulnerability occurs when cursor, partial field, decoder, message identity or authorization state is retained, duplicated or cleared inconsistently across input fragments, partial consumption, retry, pause/resume, error recovery, disconnect or object reuse. Each byte must be consumed under exactly one logical message state, and reset must clear every state that must not cross the selected boundary.

Successful consumption of a fragment is not necessarily message completion. Requested read size is not returned size, and unconsumed suffix bytes can belong to the next message.

## Conditions that establish the issue

Recover input chunks and actual returned counts, buffered prefix and suffix, parser cursor, bytes-consumed result, partial scalar or Unicode state, current message/session identity, completion signal, pause/resume offset, reset semantics and error path. Prove a feasible sequence causes bytes to be skipped, repeated, combined across messages or interpreted under stale privileged state and reaches a security-relevant consumer.

Include connection pooling, reconnect, timeout and late callbacks. A parser object can survive a transport replacement even when the protocol requires a fresh state.

## Evidence that is not sufficient

Short reads, partial parse returns, retained buffers, parser reset, reconnection, or a delimiter split across fragments is not sufficient. Incremental parsing is expected when the state machine carries exactly the required state and commits only on complete messages.

A final parse error does not undo effects already triggered by provisional callbacks; determine when the application commits.

## Investigation sequence

Build a fragment ledger containing input bytes, starting state, consumed count, retained suffix, callbacks, ending state and owner generation for every call. Follow pause, retry and error positions according to the actual API contract rather than resubmitting guessed ranges.

Trace reset and pool-return paths field by field, including application data stored outside the parser. Verify message completion separately from fragment acceptance.

## Constructed resume example

```c
result = parse(parser, buffer, received);
if (result == NEED_MORE)
    parse(parser, buffer, received);   /* resubmits already consumed bytes */
```

If the first call consumed a prefix before returning `NEED_MORE`, the second call can interpret that prefix twice and shift the grammar or duplicate a callback. The finding requires the actual parser contract and consumed offset; an API that guarantees zero consumption on `NEED_MORE` would refute this example.

## Primitive and impact limits

The direct result can be request boundary confusion, stale authentication state, duplicated fields or effects, skipped validation, unbounded buffering, or invalid retained pointers. Impact depends on the protocol action committed under the corrupted state.

## Related knowledge and primary sources

`reference-parser-incremental-input-buffer-state` and `reference-parser-stream-recovery-limits` define partial-input and reset evidence. This profile repeats the fragment ledger and commit boundary locally.

Reviewed 2026-10-09 against llhttp's [incremental parser API](https://llhttp.org/), Boost.Asio [read-until behavior](https://www.boost.org/doc/libs/latest/doc/html/boost_asio/reference/async_read_until.html), and WebSocket [fragmentation rules](https://www.rfc-editor.org/rfc/rfc6455.html). The source is constructed.
