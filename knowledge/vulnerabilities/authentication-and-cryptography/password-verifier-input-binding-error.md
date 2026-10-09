---
id: vulnerability-authentication-password-verifier-input-binding-error
title: Password verifier, KDF, salt, cost, or accepted-input binding error
kind: vulnerability
topics: [cryptography, passwords, password-hashing, kdf, salts, input-binding]
platforms: [cross-platform]
architectures: [any]
---

# Password verifier, KDF, salt, cost, or accepted-input binding error

## Definition and violated invariant

A password-verifier vulnerability occurs when enrollment and verification do not bind the intended password bytes, account, salt, construction and cost parameters to one coherent acceptance record, or when the selected construction does not provide the required offline-guessing resistance. Password hashing is distinct from a fast unkeyed content digest; a salt separates verifier instances but is not a secret key.

Text encoding, normalization, length units, embedded NUL handling and truncation are part of the accepted-input contract. Deliberate normalization can be valid when enrollment, authentication and user-facing policy agree.

## Conditions that establish the issue

Recover password acquisition and length, encoding and normalization, truncation or terminator behavior, account and stored-record selection, algorithm identifier, salt provenance and uniqueness scope, cost and memory parameters, output extent, parser bounds, migration path, comparison result and final authentication state. Prove unintended input equivalence, mismatched record use, deficient offline cost under applicable policy, or attacker-controlled parameters reaching a security-relevant path.

For offline risk, establish verifier disclosure and distinguish feasible guessing from an observed password recovery. For online acceptance, include rate limits, factors and session transition separately.

## Evidence that is not sufficient

A field named `hash`, repeated salt, low parameter number, fast-digest import, legacy record, embedded NUL, expensive verification or database exposure is not sufficient. The code may be unrelated, a pepper or external service may participate, parameters may be interpreted differently, the input channel may exclude the disputed representation, or migration may occur before acceptance.

A strong verifier cannot correct wrong account selection, prefix comparison or inconsistent input transformation.

## Investigation sequence

Trace exact password bytes from input through every transformation into enrollment and verification, then compare those paths. Decode stored verifier records and follow algorithm, salt and cost selection into the actual primitive and comparison. Preserve account identity, failure behavior, migration and session creation. Record attacker control of record fields and resource limits without assuming malformed parameters are accepted.

At binary level, follow length-producing calls, terminator scans, conversions and argument widths into the verifier. Compare the accepted byte extent with the protocol or runtime string extent.

## Hypothetical embedded-NUL example

```c
size_t accepted_length = strlen(request.password);
return verify_password_bytes((unsigned char *)request.password, accepted_length, stored_record);
```

If `request.password` originates from a reachable length-delimited field that permits embedded NUL bytes, the verifier ignores every byte after the first NUL. This establishes unintended equivalence only when upstream policy or another consumer treats the full field as distinct and an accepted prefix reaches authentication. A native NUL-terminated input contract may make the same code consistent.

## Hypothetical x86-64 System V evidence

```asm
mov  %rdi, %rbx              ; preserve password pointer
call strlen@PLT              ; RAX is extent before first NUL
mov  %rax, %rsi              ; verifier length
mov  %rbx, %rdi              ; password bytes
mov  %r12, %rdx              ; stored verifier record
call verify_password_bytes
```

This hypothetical non-inlined sequence supports a NUL-derived extent under the stated ABI. It does not establish that the input can contain embedded NUL, that the record is correct or that verification succeeds; register allocation is compiler-dependent.

## Primitive and impact limits

The direct effect is unintended credential equivalence, acceptance against the wrong verifier inputs, or reduced resistance after verifier disclosure. Account takeover requires an accepted alternate input or recovered credential plus any other required factors. Resource exhaustion from attacker-selected cost is a separate direct effect and should be scoped to reachable parameter control.

## Related knowledge and primary sources

`reference-crypto-password-verifier-binding` provides verifier inputs, record parsing and offline/online distinctions. Text, credential-comparison and authentication-state profiles cover neighboring root causes.

Reviewed 2026-10-09 against NIST [SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) for salted, costed password verifier and authentication concepts, and [RFC 9106](https://www.rfc-editor.org/rfc/rfc9106.html) for one memory-hard function's explicit password, salt and cost inputs. The examples are hypothetical and do not prescribe a current algorithm or numeric tuning value.
