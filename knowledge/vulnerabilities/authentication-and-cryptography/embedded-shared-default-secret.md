---
id: vulnerability-authentication-embedded-shared-default-secret
title: Hard-coded, shared, unchanged default, or embedded secret credential or key
kind: vulnerability
topics: [authentication, credentials, hard-coded-secrets, default-passwords, private-keys, key-lifecycle]
platforms: [cross-platform, firmware]
architectures: [any]
---

# Hard-coded, shared, unchanged default, or embedded secret credential or key

## Definition and violated invariant

An embedded or shared-secret vulnerability occurs when recoverable credential or key material grants security authority beyond every actor or device expected to possess it, or remains accepted in a default or stale state contrary to the system's uniqueness, enrollment, rotation or revocation contract. The decisive property is unauthorized reusable authority, not the presence of a secret-looking constant.

Passwords, API tokens, symmetric keys and private keys have different consumers and revocation models. A public key, certificate, identifier, test vector, encrypted key blob or derivation label is not secret merely because it resembles key material.

## Conditions that establish the issue

Recover the exact bytes or derivation, credential type and role, build or provisioning scope, per-device or per-tenant uniqueness requirement, storage and extraction path, accepted entry points, default-to-enrolled transition, rotation and revocation behavior, attacker access, and successful privileged consumer. Prove the recovered value remains valid or can derive a valid value for another actor, device, environment or protected operation.

For a shared fleet credential, establish material equality or equivalent authority rather than matching labels. For an embedded private or symmetric key, separate raw disclosure from authorized operation through an opaque provider.

## Evidence that is not sufficient

A password string, high-entropy constant, certificate, key file, factory account, default username, common hash, firmware blob or secret-scanner match is not sufficient. It may be public, inert, encrypted under inaccessible material, unique after provisioning, accepted only during a constrained enrollment state or removed from production builds.

A default credential becomes security-relevant only with a reachable accepting service and unmet change, uniqueness or authorization condition.

## Investigation sequence

Trace candidate material from storage or derivation into comparison, key import, signing, decryption or authentication. Record build configuration, provisioning state, device/tenant identity, accepted interfaces, credential generation and policy transitions. Compare multiple artifacts by actual material or demonstrated use, and follow rotation and revocation into caches and offline components.

At binary level, distinguish literal bytes from encoded or wrapped data, and follow references into the cryptographic or authentication consumer. A data cross-reference alone does not establish that a candidate is active.

## Hypothetical shared-device example

```text
static DEVICE_ADMIN_PASSWORD = "factory-service-password"
if request.password == DEVICE_ADMIN_PASSWORD:
    session.role = DEVICE_ADMIN
```

If the same recoverable value ships across devices and a remote or local actor outside the intended authority can reach this accepting path after deployment, extraction from one image can grant administration elsewhere. A forced per-device enrollment that disables this value before exposure would change the conclusion.

## Primitive and impact limits

The direct primitive is authentication or cryptographic authority obtained from recoverable, shared, default or stale secret material. Impact is limited by reachable services, credential role, device or tenant scope, additional factors and revocation. Raw key bytes may enable offline use; a default username without a valid secret grants no authority by itself.

## Related knowledge and primary sources

Key lifecycle, credential comparison, session and configuration-state references provide deeper contracts. This profile keeps material provenance, accepting consumer and authority scope together.

Reviewed 2026-10-09 against ETSI [EN 303 645](https://www.etsi.org/deliver/etsi_en/303600_303699/303645/02.01.01_60/en_303645v020101p.pdf) provision 5.1 for consumer-IoT default password uniqueness and NIST [SP 800-57 Part 1 Rev. 5](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final) for key protection and lifecycle concepts. The example is hypothetical; neither source makes every embedded constant a vulnerability.
