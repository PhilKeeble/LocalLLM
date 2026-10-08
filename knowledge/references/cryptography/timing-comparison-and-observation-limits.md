---
id: reference-crypto-timing-comparison-evidence
title: Secret-dependent comparison, constant-time scope and timing claim limits
kind: reference
topics: [cryptography, timing, comparisons, side-channels, constant-time, observation-limits]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Comparison and timing evidence

## A content-independent comparison has a bounded input/length scope

OpenSSL CRYPTO_memcmp documents comparison time dependent on length but
independent of the compared contents. [1] This is a named equality-comparison
contract, not a whole-program or universal hardware timing guarantee.

For investigation, bind actual call target, compared extents and length selection.
A constant-time helper cannot automatically remove secret-dependent work before
or after the comparison. A wrapper name also does not prove the helper was used.
Keep length and content dependence separate; variable public lengths can be
consistent with the helper's contract without establishing secret disclosure.

## Secret-dependent control flow needs an observable relation to matter

For analysis, identify protected value, selected branch/load/work and what the
relevant observer can actually distinguish. Preserve code/implementation identity,
conditions and the claimed observation boundary.

An early exit or lookup indexed by data is a lead, not proof that an external
observer learned a secret. Conversely, a uniform source expression is not proof
of uniform emitted work. Compilers, libraries and hardware can change execution
behavior; scope any implementation claim to supported evidence. This reference
asks for a justified timing relation, not a procedure to recover secrets.

## Timing observations include scheduling, collection and unrelated work

For investigation, retain timing units, event boundaries, environment, collector
interventions and the evidence joining a difference to the same secret-dependent
operation. Separate the observed timing from the proposed explanation.

A few different durations or a slow request do not establish a timing leak or
its practical consequence. Missing capture can conceal other work; a debugger
or instrumentation can alter timing. A solver/model result describes its premises,
not measured behavior. No sample count, universal threshold or remote exploitability
rule is adopted. Supported static dependence can remain a conditional finding.

## Return semantics and policy still need the actual consumer

For analysis, trace comparison result to the accepted message/credential and
sensitive operation. Content-independent comparison alone does not establish
that the caller compared the full required value or interpreted success correctly.

Truncation, changed representations and skipped/error paths need their own
evidence. Do not assume an equality-only helper supplies lexicographic ordering
or that a variable-time function proves malicious use. Report the exact operation,
coverage and unmet condition rather than labeling the whole program 'constant
time' or 'timing vulnerable' from one import.

## Source and scope

Reviewed 2026-10-08. Rolling OpenSSL CRYPTO_memcmp manual, Description and
comparison scope. Other timing observations are analytical evidence requirements,
not a source-independent certification of implementation or hardware behavior.

1. [CRYPTO_memcmp contract](https://docs.openssl.org/master/man3/CRYPTO_memcmp/): length/content timing distinction.

Workflow: playbook-crypto-operation-evidence. Observation/intervention concepts
remain in the shared validation references.
