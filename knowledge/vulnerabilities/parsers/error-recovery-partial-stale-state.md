---
id: vulnerability-parser-error-recovery-partial-stale-state
title: Parser error recovery with partial, stale, or uninitialized state
kind: vulnerability
topics: [parsers, error-recovery, incremental-parsing, state, initialization, lifecycle]
platforms: [cross-platform]
architectures: [any]
---

# Parser error recovery with partial, stale, or uninitialized state

## Definition and violated invariant

An error-recovery state vulnerability occurs when parsing fails or remains incomplete but the application continues with fields, callbacks, buffered bytes, authority flags, or object state that do not belong to one successfully completed message. State used by a security-relevant consumer must be initialized for the current message, written only from validated input, and committed only after the grammar and integrity conditions required by that consumer are complete.

Recovery is protocol-specific. Some grammars define an unambiguous resynchronization marker; others require closing the transport or discarding the enclosing object. A parser error does not itself roll back callbacks or writes that occurred before the error, and apparent progress does not establish completion.

## Conditions that establish the issue

Recover object allocation and initialization, per-message reset, incremental callbacks, parse return semantics, provisional versus committed fields, error labels, resynchronization, buffer consumption, connection reuse, object pooling, reconnect behavior, late completions, and dispatch. Prove that an error or incomplete result reaches a consumer with attacker-influenced partial data, stale data from another generation, or data read before initialization, and connect that state to a bound, identity, authority decision, pointer, length, or operation.

For stale state, establish the object or field survives across messages, connections, tenants, or privilege contexts. For uninitialized state, distinguish a real read before a dominating write from a decompiler's missing initialization or an unavailable caller contract.

## Evidence that is not sufficient

A parse error, ignored optional field, recovered stream, reused object, partially filled structure, warning log, or branch that continues is not sufficient. The consumer may check a validity bitmap, initialize safe defaults, discard the object, or use only fields known complete.

Successful parsing of a prefix does not prove the enclosing message is complete, while final failure does not prove earlier effects were undone. Establish both the parse contract and the actual use.

## Investigation sequence

Track every field with states such as uninitialized, defaulted, provisional, validated, committed, invalidated, and consumed. Follow return values and error codes to every successor, including logging and cleanup paths that fall through. Compare the bytes consumed with bytes retained for the next parse and identify the grammar rule that permits resynchronization.

Trace lifecycle generation through disconnect, pool return, reconnect, cancellation, retry, and late callback paths. At binary level, locate dominating stores, structure-clearing calls, validity tests, and error branches before interpreting a stack or heap slot as current state.

## Constructed stale-request example

```c
request req = {0};
for (;;) {
    ssize_t n = receive_next(connection, buffer, sizeof buffer);
    if (n <= 0)
        break;
    int status = parse_request(buffer, (size_t)n, &req);
    if (status < 0)
        audit_parse_error(status);
    dispatch(req.operation, req.object_id);
}
```

If `parse_request` writes fields incrementally and an error leaves an earlier iteration's `operation` or `object_id` intact, the fallthrough dispatch can combine messages or repeat a prior operation. The finding requires the actual write/reset behavior and reachable dispatch; reuse of `req` alone is not enough.

## Constructed x86-64 control-flow shape

```asm
; Illustrative System V AMD64 shape. r12 = &req, r13/r14 = input pointer/length.
mov     rdi, r13
mov     rsi, r14
mov     rdx, r12
call    parse_request
test    eax, eax
jns     .dispatch
mov     edi, eax
call    audit_parse_error
.dispatch:                       ; error path rejoins consumer without reset/commit test
mov     rdi, r12
call    dispatch_request
```

This branch shape proves only that both results can reach dispatch. It becomes evidence of stale or partial-state use only after stores inside `parse_request`, prior initialization, and the fields read by `dispatch_request` are recovered. Calling-convention and compiler differences can produce other shapes.

## Primitive and impact limits

The direct primitive is use of state that was not validly committed for the current message or generation. Consequences can include authorization bypass, cross-request data disclosure, wrong-operation dispatch, out-of-bounds access, pointer misuse, replay, or protocol desynchronization. Memory corruption requires a concrete invalid memory operation, not merely stale semantics.

## Related knowledge and primary sources

`reference-parser-stream-recovery-limits`, incremental parser references, and lifecycle references provide reusable protocol and ownership contracts. This profile keeps the per-field commit and generation requirements local.

Reviewed 2026-10-09 against [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html) for HTTP/1.1 message completeness and connection reuse, [RFC 7464](https://www.rfc-editor.org/rfc/rfc7464.html) for an explicit JSON-sequence recovery marker and incomplete elements, and the [C abstract-machine draft N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) for indeterminate object values. The source and assembly are constructed; target behavior requires its own parser, ABI, and data-flow evidence.
