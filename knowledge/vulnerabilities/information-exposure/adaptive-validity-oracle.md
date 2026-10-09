---
id: vulnerability-information-adaptive-validity-oracle
title: Adaptive error, timing or validity oracle
kind: vulnerability
topics: [information-disclosure, oracle, timing, cryptography, authentication]
platforms: [cross-platform]
architectures: [any]
---

# Adaptive error, timing or validity oracle

## Definition and violated invariant

An adaptive oracle exists when an unauthorized actor can submit or select inputs and distinguish responses, timing or side effects that reveal a protected predicate, then use prior observations to choose later queries. Examples include account existence, padding validity, signature-format acceptance, authentication state or decryption structure.

Different internal outcomes are not themselves a vulnerability. The violated invariant requires an observable, sufficiently reliable distinction tied to protected state under a feasible attacker query model.

## Conditions that establish the issue

Define the actor, chosen-input capability, protected predicate, observable channel, query rate, noise, state reset and inference algorithm. Demonstrate or analytically support that the observations distinguish predicate classes better than chance at a practical sample count. Bind the signal to the secret-dependent branch or operation and exclude public input length, caching, network route and load as explanations.

For cryptographic claims, recover the exact scheme, encoding, key role, verification order and response behavior. A padding oracle, MAC oracle and signature-format oracle reveal different predicates and support different attacks.

## Evidence that is not sufficient

Distinct log messages hidden from the attacker, two internal status codes mapped to one response, one slow request or a non-constant-time instruction is not sufficient. Constant response text also does not refute an oracle if timing, connection handling, retries or state changes remain distinguishable.

Do not infer plaintext or key recovery solely from a validity bit. Establish that a known adaptive method applies to the exact scheme and that the attacker has the necessary ciphertext, query and success conditions.

## Investigation sequence

Trace each candidate input through parsing, verification and failure handling to every externally observable effect. Locate where protected state first selects control flow, memory access or work. Compare response body, status, length, connection behavior, timing distribution, retry counters and persistent side effects while preserving the actor's actual network and authentication position.

At binary level, a secret-dependent early branch supports a candidate channel but not remote distinguishability. Recover calls, loops and error convergence after that branch. Record measurement uncertainty and distinguish a direct response oracle from a statistical timing oracle.

## Constructed example

A hypothetical RSA decryption endpoint returns `bad padding` for an encoding failure and `bad record` when padding succeeds but record parsing fails. If an unauthenticated caller can submit chosen ciphertexts and distinguish these results, the endpoint exposes an encoded-message validity predicate.

The example does not by itself prove plaintext recovery. The analyst must establish the exact RSA encoding, key use, ciphertext transformations, query availability and applicability of an attack to that oracle.

## Primitive and impact limits

Report the predicate learned per query, reliability, query complexity, rate constraints and state dependence. The primitive may enable enumeration, incremental secret comparison or chosen-ciphertext inference; it may also be too noisy or constrained for a stronger result.

Account access, plaintext recovery, forgery or key recovery requires a scheme-specific chain. Keep the observed oracle separate from the projected consequence.

## Related knowledge and primary sources

Authentication and cryptography profiles provide the consumer-specific state and key contracts. This profile supplies the observer and adaptive-query evidence threshold.

Reviewed 2026-10-09 against [RFC 8017 section 7.2.2](https://www.rfc-editor.org/rfc/rfc8017#section-7.2.2), which warns that PKCS #1 v1.5 decoding errors must not be distinguishable by message or timing, and [MITRE CWE-203](https://cwe.mitre.org/data/definitions/203.html). The original chosen-ciphertext result is Daniel Bleichenbacher's [CRYPTO '98 paper](https://link.springer.com/chapter/10.1007/BFb0055716); applicability depends on the target encoding and oracle.
