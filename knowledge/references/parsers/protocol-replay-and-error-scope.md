---
id: reference-parser-protocol-replay-error-scope
title: Early-data replay, HTTP/2 retry signals and stream-error scope
kind: reference
topics: [protocols, replay, retries, tls, early-data, http2, error-recovery, hpack]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Protocol replay and error scope

## TLS early-data acceptance does not establish exactly-once application effects

TLS 1.3 provides no inherent replay protection for 0-RTT data. RFC 8446 separates
direct early-data replay from duplication caused by client retries and describes
why multiple serving instances complicate enforcement. Clients must restrict early
data to what they consider safe to replay. [1]

Investigative inference: trace whether early data is enabled, accepted and released
to application handlers. A resumption path alone does not prove 0-RTT use. Record
the scope of replay records and request identity across workers, failover, restart
and retry; a local ticket check is not evidence of application-wide deduplication.
Use reference-logic-retries-transactions-replay for idempotence and commit-boundary
rules. Do not generalize early-data limitations to all ordinary TLS records.

## HTTP Early-Data preserves replay risk across forwarding hops

RFC 8470 uses Early-Data: 1 to convey early-data history. An intermediary forwarding
before its client handshake completes adds the field and must not remove an
existing one. A later hop's completed handshake does not remove risk from early
data already forwarded on an earlier hop. [2]

Investigative inference: follow the metadata from TLS termination to origin
dispatch. A protected proxy-to-origin channel does not establish that the original
request was never early data. Absence of this header from an original client is
not proof of absence of early data; transport/API state can supply that fact.
Distinguish actual early-data provenance from merely finding the header string
in a binary or request template.

## HTTP 425 requests a retry outside early data, not a replay-proof operation

HTTP 425 Too Early declines processing because of replay risk. For a request
sent in early data, RFC 8470 expects retry after 425, but the retry must not itself
use early data. It also treats multiple or invalid Early-Data fields as the risk
signal value 1, not as permission to ignore the signal. [2]

Investigative inference: follow the response branch to the retry's transport mode,
payload identity and prior side effects. Returning 425 after committing an effect
does not undo it. An application deduplication policy is still distinct from this
transport retry rule. Parsing disagreement over the risk field can matter when
one component forwards while another executes; establish actual branch behavior.

## HTTP/2 REFUSED_STREAM is stronger evidence than an arbitrary reset

HTTP/2 REFUSED_STREAM indicates no application processing occurred and permits
retry, including non-idempotent requests. A server must not use it once stream
frames were passed to the application layer. An arbitrary RST_STREAM does not
provide that guarantee. [3]

Investigative inference: connect emitted error code to dispatch/commit ordering.
A wrapper mapping every internal error to REFUSED_STREAM can falsely invite a
duplicate operation. Conversely, receipt of that code is protocol evidence about
the peer's claim, not independent proof a defective peer obeyed it. Keep request
identity and application deduplication separate from transport stream identity.

## HTTP/2 GOAWAY Last-Stream-ID is a processing boundary, not a commit receipt

GOAWAY's Last-Stream-ID bounds streams on which its sender might have acted or
might still act. Higher-numbered peer-initiated streams can be retried; lower or
equal numbers do not establish committed success or known non-processing. [3]

Constructed investigation: a client retries every unfinished operation after
GOAWAY, including a lower-numbered non-idempotent request already dispatched.
Recover the peer role, numeric stream boundary, response state and retry policy.
Do not confuse the GOAWAY frame's own connection-level stream field with its
payload Last-Stream-ID. A close without adequate processing evidence leaves
completion ambiguous; use the application's idempotence/deduplication contract.

## HTTP/2 stream reset must preserve connection-wide decoding state

HTTP/2 distinguishes stream-local errors from connection errors. After sending
RST_STREAM, an endpoint can receive already-sent frames and must preserve relevant
connection-level compression/flow-control updates. HPACK decoding failure is a
connection error, not merely failure of one request. [3]

Investigative inference: trace the reset path's minimal processing separately from
application delivery. Continuing to update shared decoding state need not mean the
rejected request is still executing. Conversely, blindly skipping every frame
after reset can desynchronize other streams. Confirm stream-object lifetime and
late callbacks without confusing retained connection state with leaked authority.
Do not transfer HTTP/2's recovery contract to HTTP/1.1 or a custom binary protocol.

## Sources and scope

Reviewed 2026-10-02. These are protocol guarantees and obligations, not measured
behavior of a target implementation. Crypto construction, certificate validation
and distributed transaction design are outside this document's scope.

1. [RFC 8446 §8](https://www.rfc-editor.org/rfc/rfc8446.html#section-8): 0-RTT and retry/replay distinctions.
2. [RFC 8470 §§5-6](https://www.rfc-editor.org/rfc/rfc8470.html#section-5): Early-Data, 425 and intermediaries.
3. [RFC 9113](https://www.rfc-editor.org/rfc/rfc9113.html): §§4.3, 5.4, 6.8 and 8.7, shared state, errors and retry evidence.

Workflow: playbook-re-protocol-security-state. For HTTP/1.1 body consumption and
EOF, use reference-parser-stream-recovery-limits.
