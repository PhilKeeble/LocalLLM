---
id: vulnerability-information-secret-in-log-diagnostic-crash-telemetry
title: Secret exposure through logs, diagnostics, crash artifacts or telemetry
kind: vulnerability
topics: [information-disclosure, logging, crash-dump, telemetry, diagnostics]
platforms: [cross-platform]
architectures: [any]
---

# Secret exposure through logs, diagnostics, crash artifacts or telemetry

## Definition and violated invariant

This vulnerability occurs when a log, error, trace, diagnostic bundle, crash artifact or telemetry event records sensitive data and makes it available beyond the data's authorized audience or lifetime. The violated invariant is that operational observability must not create a less-protected copy of a secret or protected record.

The root cause can be direct insertion, overly broad capture, unsafe exception formatting, memory dumping or incorrect access/retention policy. The mere existence of diagnostics is not a vulnerability.

## Conditions that establish the issue

Identify the protected value, the exact field or memory range captured, every transformation or redaction, the artifact destination, readers, transport, retention and deletion behavior. Prove that an actor lacking authority over the source data can obtain the resulting artifact, or that the artifact persists beyond the approved lifecycle.

For crash dumps, distinguish metadata, selected memory and full-address-space capture. For telemetry, include local queues, collectors and downstream exports. A secure initial sink does not settle exposure if replicas, support bundles or alerts widen access.

## Evidence that is not sufficient

A logging call near a password variable, a crash handler, verbose mode, exception text or telemetry library is only a lead. The value may be omitted, irreversibly transformed, redacted before the boundary, protected by equivalent authorization or unavailable in the selected dump class.

Do not call identifiers, hashes or tokens secret without establishing their security role and whether the recorded form remains usable or linkable. Masking only part of a credential can still leak material, but the usable portion and observer must be shown.

## Investigation sequence

Follow sensitive data from acquisition through formatting, serialization, buffering, transport, storage and every reader. Resolve format strings and structured fields at the binary call site; inspect exception and crash paths that bypass normal redaction. Recover configuration that selects verbosity, dump scope and upload destination without assuming a development default applies in production.

Record file, endpoint or collector permissions and the effective identity of each consumer. Compare retention and deletion with the source secret's lifetime. State the exposed representation and whether it supports replay, recovery, correlation or only limited metadata inference.

## Constructed example

This hypothetical authentication path records a bearer credential in an error message:

```c
if (!verify_token(token))
    log_error("authentication failed: token=%s", token);
```

The call establishes insertion only if `token` is a usable secret and reaches the formatter. Disclosure additionally requires an unauthorized reader of the log, export or support bundle. A formatter that replaces the value before storage can refute the shown data path.

## Primitive and impact limits

The direct primitive is unauthorized access to the recorded value or a stable inference derived from it. State whether the artifact contains a complete credential, cryptographic key, personal record, address, request content or narrower metadata and whether it remains valid.

Replay, account takeover, decryption or elevation depends on the secret's role, binding, expiry and the attacker's ability to use it. Log access alone does not establish those outcomes.

## Related knowledge and primary sources

Error handling, dump formats and platform logging contracts determine the bytes captured; authorization profiles determine who may read each artifact. This profile keeps the full source-to-secondary-copy boundary together.

Reviewed 2026-10-09 against [NIST SP 800-53 Revision 5.1 control SI-11](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final), which requires useful errors without exploitable disclosure, [MITRE CWE-532](https://cwe.mitre.org/data/definitions/532.html) for sensitive log insertion and [MITRE CWE-209](https://cwe.mitre.org/data/definitions/209.html) for sensitive error messages. Product-specific dump and telemetry capture still require target documentation or binary evidence.
