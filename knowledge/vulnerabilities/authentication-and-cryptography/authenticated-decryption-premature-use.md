---
id: vulnerability-authentication-authenticated-decryption-premature-use
title: Plaintext or parsing effects released before the required authenticity decision
kind: vulnerability
topics: [cryptography, aead, decryption, authentication-tag, parsing, oracle]
platforms: [cross-platform]
architectures: [any]
---

# Plaintext or parsing effects released before the required authenticity decision

## Definition and violated invariant

An authenticated-decryption sequencing vulnerability occurs when candidate plaintext or effects derived from it cross a trust boundary before the protocol's complete authenticity decision succeeds, or when failure classes expose a distinguishable validity signal that the threat model requires to remain hidden. Under the RFC 5116 AEAD interface, decryption returns plaintext or `FAIL`; bytes produced by an internal or incremental transform are not authenticated plaintext until the selected interface's verification boundary succeeds.

This profile covers trust sequencing. A parser memory-safety defect triggered before verification remains its own root cause, and a timing or error oracle requires a supported observer and query model rather than merely different internal error causes.

## Conditions that establish the issue

Recover the exact ciphertext, nonce, associated data, key and tag supplied; library operation and result contract; incremental output; final verification result; every pre-verification consumer; externally visible errors, timing or side effects; and rollback behavior. Prove attacker-influenced unauthenticated bytes reach a security-relevant parser, state mutation, response or oracle before failed verification suppresses or reverses the effect.

For signed or padded formats, identify the protocol's required ordering and which checks form the complete acceptance decision. Do not impose AEAD semantics on an unrelated construction.

## Evidence that is not sufficient

A decrypt call before a tag check, plaintext buffer, distinct internal status, padding check, parser call or streaming API is not sufficient. The library may withhold output, the parser may be side-effect-free and memory-safe, failure may discard all state, or the difference may be unobservable to the stated attacker.

A final verification call does not retroactively authorize an earlier external effect. Conversely, parsing candidate bytes into isolated temporary state is not automatically a vulnerability when no protected decision, unsafe parser effect or observable validity signal occurs before acceptance.

## Investigation sequence

Build a timeline from input acquisition through transform output, parsing, validation, state changes, response construction, final authenticity result and commit or rollback. Mark the first operation that assumes authenticity and compare it with the actual verification boundary. Trace exceptional, truncated and cancellation paths as well as ordinary failure.

At binary level, follow the decrypt-update destination to its consumers and the final-result branch to all commits. Preserve the named library's return convention; identical-looking calls can expose different output guarantees across interfaces and modes.

## Hypothetical incremental-use example

```text
candidate = decrypt_update(ciphertext)
parse_and_apply_commands(candidate)
if not decrypt_final_and_verify(tag):
    return AUTHENTICATION_FAILED
```

If `decrypt_update` exposes attacker-influenced candidate bytes and `parse_and_apply_commands` produces effects before final tag verification, failed authentication arrives too late to protect those effects. If parsing is isolated and its state is committed only after successful verification, the same call order may not violate the consuming operation's trust boundary.

## Hypothetical control-flow evidence

```text
decrypt_update -> candidate buffer -> parse -> privileged effect
                                      |
                                      +-> decrypt_final/tag result occurs later
```

The diagram establishes the question to prove, not the library behavior. Recover whether output exists before finalization, which bytes are valid on failure and whether the effect is externally durable or observable.

## Primitive and impact limits

The direct primitive is use of unauthenticated candidate data, an irreversible pre-verification effect, or an observable validity distinction. Impact may be unauthorized state change, chosen-input parser exposure, information leakage or a cryptographic oracle. Code execution still requires a separate reachable execution or memory-corruption primitive and its environmental prerequisites.

## Related knowledge and primary sources

`reference-crypto-aead-verification-boundary` provides AEAD input and output contracts; parser, transaction and oracle references cover the downstream effect. This profile keeps verification result, first trusted use and observable failure in one evidence chain.

Reviewed 2026-10-09 against [RFC 5116 sections 2.2-2.3](https://www.rfc-editor.org/rfc/rfc5116.html) for authenticated decryption returning plaintext or `FAIL`, and the OpenSSL [EVP cipher documentation](https://docs.openssl.org/master/man3/EVP_EncryptInit/) for the named incremental AEAD example's decisive final status and invalid output on authentication failure. The example is hypothetical and does not assign OpenSSL sequencing to other libraries.
