---
id: reference-crypto-randomness-state-failure
title: Cryptographic randomness, generator state, initialization and failure
kind: reference
topics: [cryptography, randomness, entropy, seeding, initialization, failure, state-lifetime]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Randomness and generator-state evidence

## Random-looking output does not establish cryptographic unpredictability

A deterministic random bit generator (DRBG) derives initial state from seed
material and evolves that state to produce output. NIST distinguishes entropy
input, initialization, generation, reseeding and state protection. [1]

For investigation, identify the actual generator and the output's role: key,
challenge, salt, nonce, identifier or nonsecurity simulation. A pseudorandom API,
high entropy estimate or varied outputs cannot alone establish adequate seeding
or unpredictability. Conversely, a deterministic construction is not automatically
insecure when its required seed/state properties hold. Bind the generator's
contract and source/state evidence to the operation rather than its function name.

## Initialization and reseeding belong to a particular generator instance

NIST's DRBG model assigns each instantiation its own protected internal state. [1]
For analysis, retain instance identity, initialization outcome, seed provenance,
supported reseeding policy and the actual state consumed by generation.

Initialization of one object cannot prove that another object's outputs have
the same assurance. Restart, fork, snapshot restore or copied application state
can require investigation of repeated state; they do not by themselves prove
repeated cryptographic output. Determine the selected implementation's treatment
and any fresh input. Missing seed history leaves the claim unresolved, rather
than making a time value, process ID or observed byte distribution a sufficient seed.

## A randomness request must supply the extent actually consumed

Linux getrandom returns a byte count on success and -1 on error. Depending on
flags and interruption, its result can be shorter than requested; nonblocking
requests can fail when the required source is not ready. [2]

Investigate flags, actual return, initialized extent and failure path before
joining the buffer to a key or nonce. A call is not proof all requested bytes
were filled. Retain retries, fallbacks and stale buffer contents separately.
This is a named Linux result contract, not a universal convention for other
randomness APIs. A failed source followed by a weaker fallback needs its own
supported consumer/effect evidence before becoming a security finding.

## Randomness requirements depend on the value's security role

For analysis, determine whether the consumer requires unpredictability, uniqueness,
independent state or a combination. A nonce need not always be secret; a secret
key cannot be treated as a public sequence counter. The algorithm/protocol
specification supplies the actual requirement.

Retain lifecycle across devices, workers, resets and key changes. Repeated salt
or identifier values do not automatically prove key recovery or an observed
compromise. A uniqueness rule for one encryption mode cannot establish the needs
of every IV or protocol. Nonce lifecycle is in reference-crypto-nonce-iv-lifecycle;
the distinction here is a role/evidence question, not a generator recommendation.

## Sources and scope

Reviewed 2026-10-08. NIST SP 800-90A revision 1, section 8.3 and the generation
status/working-state descriptions in section 9:
conceptual DRBG lifecycle/state and status. Linux man-pages 6.19 getrandom result
and readiness rules. Publication editions record provenance, not target versions.

1. [NIST DRBG publication](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90Ar1.pdf): seed/state and generation concepts; no algorithm or strength table adopted.
2. [getrandom(2)](https://man7.org/linux/man-pages/man2/getrandom.2.html): extent, failure and flag-specific behavior.

Workflow: playbook-crypto-operation-evidence. No output sample is a statistical
certification, and no target generator execution is claimed.
