---
id: reference-crypto-aead-verification-boundary
title: Authenticated encryption, associated data and plaintext release after verification
kind: reference
topics: [cryptography, aead, authentication, associated-data, plaintext, verification, failure]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Authenticated-decryption evidence

## AEAD authenticates its selected inputs, not every surrounding field

Authenticated encryption with associated data (AEAD) protects encrypted content
and authenticates supplied associated data, which is not encrypted. RFC 5116
defines the interface's key, nonce, plaintext/ciphertext and associated-data roles.
[1]

For investigation, bind exact input extents and key identity to the verification
operation. A tag does not automatically authenticate a header omitted from those
inputs or the caller's intended interpretation. Preserve format, lengths and
context encoding before assigning authenticated meaning. Encryption alone does
not provide this interface's authenticity property; the selected construction
and successful verification must support the claim.

## Authentication failure cannot supply trusted plaintext

RFC 5116 defines authenticated decryption as returning plaintext or FAIL for
inauthentic inputs. [1] That interface contract is different from merely producing
bytes through a decryption transform.

Investigate actual verification result and all consumers of candidate output.
Failed authentication must not be treated as success because a buffer looks
plausible or a parser accepts it. Keep decoding/parsing before trust separate
from actions that require authenticated content. The presence of an AEAD call
cannot establish that the caller checked its result or withheld sensitive effects.
No return-code convention is assumed for an unidentified library.

## Incremental output needs the library's actual authentication boundary

OpenSSL's documented EVP AEAD interface makes final decryption status decisive;
output must not be used when authentication fails. [2] Earlier output availability
does not independently prove successful authentication.

For investigation, follow supplied tag/associated data, complete input, final
status and the first consumer requiring trust. A checked final result after an
earlier privileged effect does not retroactively authenticate that effect. Different
modes/interfaces can place verification elsewhere; do not impose one EVP call
sequence on every implementation. Missing finalization evidence leaves output's
authenticity unresolved rather than proving a successful authenticated decrypt.

## Associated-data formatting must preserve the consumer's field boundaries

RFC 5116 requires associated data to be unambiguously parseable into its intended
elements when applications use such a composition. [1]

For investigation, preserve actual serialized bytes, field boundaries, widths
and the consumer's interpretation. Different tuples that select one byte string
do not become distinct authenticated contexts merely because their labels differ.
Likewise, an authenticated field does not authorize the selected application
object without a separate policy check. Shared parsing/normalization contracts
remain in reference-parser-duplicate-fields-decoded-values and related references.

## Sources and scope

Reviewed 2026-10-08. RFC 5116 sections 2.1-2.3 and 3.3; rolling OpenSSL EVP
manual, AEAD Interface. The named API illustrates verification/output scope,
not a required tool or universal function sequence.

1. [RFC 5116](https://www.rfc-editor.org/rfc/rfc5116.html): selected inputs, FAIL and associated-data formatting.
2. [OpenSSL EVP cipher contract](https://docs.openssl.org/master/man3/EVP_EncryptInit/): AEAD final status and rejected output.

Workflow: playbook-crypto-operation-evidence. Successful authentication alone
does not establish freshness, caller authorization or malicious/benign intent.
