---
id: playbook-re-protocol-security-state
title: Recover protocol authentication, negotiation, replay and recovery state
kind: playbook
topics: [reverse-engineering, vulnerability-identification, malware-analysis, protocols, authentication, replay, state-machines]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover protocol security state

## Identify the endpoint role and effective protocol

Record listener/client role, local dispatch, transport, selected version and
extensions, intermediaries and the sensitive operation under investigation.
Treat port numbers, banners, embedded libraries and decompiler names as leads.
Confirm message fields and state transitions against the actual implementation;
a familiar wire prefix does not establish complete standards compliance.

For malware analysis, follow decoded commands/configuration into handlers and
effects. Legitimate TLS, LDAP, SSH or HTTP usage is not itself malicious behavior.
Separate protocol identification, endpoint identity and the purpose inferred from
the payload/operation. Missing decryption or an incomplete exchange leaves a
visibility gap, not a clean verdict or proof that a command executed.

## Recover a state tuple rather than one authenticated flag

For each accepted message, record transport protection, parser mode, attempted
identity, verified identity, effective authorization, logical session generation,
active operation and pending callbacks. These may live in different objects.
Mark the instruction/callback that changes each component and its failure exits.

Reference-parser-protocol-authentication-state supplies concrete LDAP anonymous
bind, SSH partial-success/probe and SASL identity distinctions. A helper returning
success can mean parsing, key acceptance or one factor rather than final login.
Follow the exact condition opening privileged dispatch and any trusted upstream
enforcement before claiming that a local check is missing.

## Trace bytes across negotiation and protection boundaries

Map proposal → chosen mode → policy decision → completion → selected parser.
Retain counted names, buffered suffixes and the exact direction-specific activation
boundary. Distinguish unread network bytes, plaintext already parsed and newly
protected records. A late callback must not relabel earlier input as trusted
merely because the connection has since changed modes.

Use reference-parser-protocol-upgrade-negotiation for SMTP and ALPN examples.
For each fallback, identify trigger, attacker influence, effective policy floor
and actual post-fallback checks. Compare capability caches before/after upgrade.
Compatibility is a defect only when the reached path violates the required policy.

## Recover replay identity and duplicate-effect handling

Separate transport retransmission, early-data replay, application retry and a new
request carrying old content. Find the actual identity used for deduplication:
request ID, principal, operation, payload binding and retained completion record.
Track concurrent attempts, timeout, reconnect, restart and serving-instance scope.

Use reference-parser-protocol-replay-error-scope for 0-RTT, HTTP 425 and HTTP/2
processing claims. A sequence number or ACK is not automatically an application
commit receipt. Build the ordering of identity reservation, external effect,
durable record and acknowledgement from code. Record ambiguous completion without
assuming either rollback or successful execution.

## Follow failure to the next request and each affected state owner

For malformed messages, denied credentials, cancelled authentication, disconnect
and stream reset, trace retained fields, parser cursor, identity, grants and
queued work. Ask whether recovery applies to one message, one stream, the whole
connection or a logical session that intentionally outlives the transport.

Constructed comparison: begin authentication as A, fail a subsequent attempt as B,
then trace a sensitive request. Evidence must show which identity/grant reaches
the effect; the sequence alone is not a finding. For multiplexing, retain shared
compression state separately from per-stream authority. Use
reference-concurrency-cancellation-completion-shutdown for late-completion lifetime.

## Report the violated transition and preserve alternative explanations

Return the applicable contract/policy, feasible input/event sequence, branch and
state-write evidence, selected identity/object, and first forbidden effect.
Distinguish a parser or status-code disagreement from demonstrated authority gain,
duplicate effect, disclosure or availability loss. Include upstream checks,
intentional anonymous access, legitimate delegation and allowed resumption as
possible counterevidence where relevant.

Static evidence can establish transitions without executing a specimen. If runtime
observations are available from an authorized environment, label them separately
and preserve configuration and history. Do not treat an analyst-forced impossible
state as reproduction of a remotely reachable protocol flaw.

## Basis and related workflows

Reviewed 2026-10-02. Analytical workflow based on the three named protocol references
and their primary RFC sources. No target observations or experiments are claimed.
Use playbook-re-incremental-parser-state for fragment/buffer mechanics and
playbook-re-reconstruct-operation-invariants for broader authorization/commit rules.
For sequence-level comparisons, reset domains, dynamic identifiers and delayed
events, use playbook-validation-stateful-sequences.
