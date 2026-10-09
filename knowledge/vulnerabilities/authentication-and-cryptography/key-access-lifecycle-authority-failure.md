---
id: vulnerability-authentication-key-access-lifecycle-authority-failure
title: Key exposure, overbroad key invocation, stale key use, or incomplete destruction
kind: vulnerability
topics: [cryptography, keys, key-storage, authorization, lifecycle, destruction]
platforms: [cross-platform]
architectures: [any]
---

# Key exposure, overbroad key invocation, stale key use, or incomplete destruction

## Definition and violated invariant

A key access or lifecycle vulnerability occurs when an actor can read key material or invoke a protected key operation outside the key's owner, purpose, algorithm, object, lifecycle or policy scope, or when stale material remains usable after the contract requires retirement, revocation or destruction. Export of raw bytes and use through an opaque key handle are distinct authority primitives.

Key identity includes material or a supported handle relation, owner, generation, purpose and lifecycle state. A key identifier, certificate, filename or provider label does not prove which key was used or what protection it received.

## Conditions that establish the issue

Recover key creation or import, material and alias copies, owner and tenant, storage protection, handle provenance, caller identity, permitted operation and object, provider or broker checks, active/retired/revoked state, caches and replicas, rotation propagation, destruction extent and result, and final cryptographic consumer. Prove unauthorized read or use, or successful use after the governing state forbids it.

For incomplete destruction, establish a surviving accessible representation and the actor or path able to use it. A theoretical copy without accessibility or validity does not establish compromise.

## Evidence that is not sufficient

A key-like string, private-key file, exportable flag, open handle, cleanup call, missing zeroization, old key ID, encrypted blob or successful signature is not sufficient. Material may be public, inaccessible, inactive or a test value; an opaque handle may permit only authorized operations; another copy may be independently protected; and a valid output does not identify the caller or policy.

Nonexportable does not imply non-invokable, while handle release does not prove every material copy was erased. Keep disclosure, invocation and lifecycle claims separate.

## Investigation sequence

Create a key ledger containing generation, material or opaque identity, owner/tenant, purpose, allowed algorithms and operations, storage and wrapping, handles and aliases, active policy, use events, rotation/revocation and destruction. Trace the effective caller and selected object through every broker or provider boundary. Compare policy at use time with cached sessions and replicas rather than relying on current configuration alone.

At binary or managed-code level, follow key bytes and handles through copy, import, provider dispatch, serialization, logging, crash paths and cleanup. Confirm buffer extents and API results before claiming erasure or residual access.

## Hypothetical overbroad broker example

```text
request = { key_id, operation, message }
if caller.is_authenticated:
    return key_store[key_id].perform(operation, message)
```

Authentication alone does not bind the caller to the selected key, operation or message purpose. The example is vulnerable only if an unentitled caller can select a protected key or forbidden operation and receive a usable result; a separate broker policy may supply the omitted authorization.

## Primitive and impact limits

The direct primitive is raw key disclosure, unauthorized cryptographic invocation or use of material outside its permitted lifecycle. Consequences depend on key role, operation scope, message control, revocation and relying-party policy. A signing oracle may enable authenticated outputs without revealing the private key; historical decryption requires the relevant ciphertexts and key validity.

## Related knowledge and primary sources

`reference-crypto-key-access-lifecycle` provides key identity, invocation, compromise and destruction distinctions. Authorization, storage and protocol references govern the caller and consumer around a particular key service.

Reviewed 2026-10-09 against NIST [SP 800-57 Part 1 Rev. 5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), particularly its key protection, compromise and lifecycle concepts. The example is hypothetical and makes no storage-product or complete-erasure guarantee.
