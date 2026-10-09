---
id: vulnerability-authentication-credential-comparison-prefix-error-acceptance
title: Incorrect credential comparison, partial match, or error-path acceptance
kind: vulnerability
topics: [authentication, credentials, comparison, partial-match, errors, lengths]
platforms: [cross-platform]
architectures: [any]
---

# Incorrect credential comparison, partial match, or error-path acceptance

## Definition and violated invariant

A credential-comparison vulnerability occurs when equality is decided over the wrong length, representation, field set or return convention, or when decoding, lookup, verification or comparison failure is treated as success. Authentication must require one complete candidate credential to satisfy the selected verifier contract, with exact type/identity binding and fail-closed handling for every non-success result.

Byte comparison, text comparison, password hashing, signature verification and platform status APIs have different return semantics. Constant-time comparison addresses an observer side channel; it does not repair a missing length check, truncated decode, prefix comparison, wrong credential record or inverted return test.

## Conditions that establish the issue

Recover credential input and decoding, explicit and implicit lengths, embedded terminators, normalization, selected account/verifier record, comparison or verification API and full return domain, error mapping, retry/fallback paths, state update and authenticated-session creation. Prove an incomplete, unequal, malformed, failed or wrong-account credential reaches the success path.

For prefix matches, establish both buffers are readable for the compared count and show the accepted attacker length is shorter than the required credential. For error acceptance, identify the exact error/status value and branch.

## Evidence that is not sufficient

A `memcmp`, string comparison, early exit, short credential, nonzero return, exception handler, timing difference or successful login is not sufficient. The caller may separately require equal lengths, compare a fixed-size digest, map return values correctly or reject before session creation.

An ordinary data-dependent comparison is not automatically exploitable through timing; that separate claim requires the observer model described by the timing profile.

## Investigation sequence

Track raw credential, decoded bytes, candidate length, stored/verifier length, selected identity and every comparison result. Reconstruct the success predicate and all error joins. Follow success into issuance of a token/session or access to the protected operation, and distinguish logging/UI success from effective authentication state.

At binary level, recover calling convention, argument order and length source, then inspect the comparison result branch and dominating length equality checks. Decompiler names such as `bool verify` cannot replace the real return contract.

## Constructed prefix-comparison example

```c
bool credential_matches(const unsigned char *stored, size_t stored_length, const unsigned char *supplied, size_t supplied_length) {
    return memcmp(stored, supplied, supplied_length) == 0;
}
```

If `supplied_length` is smaller than `stored_length`, this accepts any supplied byte sequence equal to the stored prefix; a zero count also compares no bytes. The finding requires a reachable shorter input, readable ranges and no separate exact-length requirement. A supplied length larger than available storage is a separate memory-safety issue.

## Constructed System V AMD64 shape

```asm
; r12/r13 = stored/supplied pointers, r14 = attacker-influenced supplied length.
mov     rdi, r12
mov     rsi, r13
mov     rdx, r14
call    memcmp
test    eax, eax
je      .authenticated          ; no shown comparison with required stored length
```

This shape proves a prefix-risk candidate only after confirming no dominating length equality check and that `.authenticated` creates effective authenticated state. It does not prove the input can be empty or short, or that the compared objects are credentials.

## Primitive and impact limits

The direct primitive is acceptance of a credential that does not satisfy the complete verifier contract. Consequences include impersonation and the session or operations available to the selected account. Account privileges, later authorization, rate limits and reachable credential records bound impact.

## Related knowledge and primary sources

String representation, password verifier, signature validation and timing references provide underlying API contracts. This profile repeats exact-length, full-return-domain and effective-session requirements locally.

Reviewed 2026-10-09 against POSIX [`memcmp`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/memcmp.html), ISO C draft [N1570 section 7.24.4.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and NIST [SP 800-63B](https://pages.nist.gov/800-63-4/sp800-63b.html) for authentication/verifier scope. The source and assembly are constructed.
