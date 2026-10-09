---
id: vulnerability-authorization-boot-firmware-update-authority-gap
title: Boot, firmware, recovery, or variable update accepted under the wrong authority
kind: vulnerability
topics: [authorization, firmware, boot, recovery, variables, updates]
platforms: [firmware, uefi, embedded]
architectures: [any]
---

# Boot, firmware, recovery, or variable update accepted under the wrong authority

## Definition and violated invariant

A firmware update-authority vulnerability occurs when boot code, firmware, recovery logic or a persistent variable accepts a change from an actor, signer, role or physical/logical interface not authorized for the selected component and action. Cryptographic authenticity identifies a key relation; it does not by itself establish that the signer may update every component, change boot policy or invoke recovery.

This differs from payload-integrity or rollback defects. The defining mismatch is between authenticated or physical actor and permitted operation/object, although one update path can contain several failures.

## Conditions that establish the issue

Recover the initiating actor and interface, lifecycle or physical-presence state, trust anchor and signer role, exact authenticated representation, component/device identifiers, requested operation and destination, variable attributes and namespace, ordinary versus recovery policy, retained sequence state, installation and activation context, and resulting authority. Prove the accepted actor is not authorized for that operation on that component.

Include manufacturing, service and recovery modes and the transition that enters them. A physically reachable interface is not automatically authorized for persistent boot changes.

## Evidence that is not sufficient

A signed image, update key, recovery path, USB/serial interface, firmware variable, physical button, alternate slot or successful flash write is not sufficient. The signer or physical flow may be intentionally authorized, policy may restrict the selected component, or activation may independently reject the result.

An old valid image concerns freshness or rollback policy; a wrong-role signature concerns update authority. Keep them separate even when both apply.

## Investigation sequence

Build an authority matrix for ordinary update, boot-time verification, recovery, manufacturing and variable mutation. Trace authenticated identity or physical-presence proof into the exact component/action decision, then follow bytes and policy state through installation and activation. Record which privilege level and processor or firmware domain performs each transition.

At binary or firmware level, follow key/role selection, component IDs, variable GUID/name and attributes, mode flags and control transfer. A verification success branch must be joined to signer-role and target checks.

## Hypothetical role-confusion example

```text
if verify_signature(any_trusted_key, update_manifest):
    write_component(update_manifest.target, update_manifest.payload)
```

The path is vulnerable only if trusted keys have distinct authorized roles or target scopes, a lower-authority signer can select a higher-trust component, and no later stage rejects or reauthorizes it. A trust store intentionally granting every key the same update role changes the policy conclusion.

## Primitive and impact limits

The direct primitive is unauthorized persistent firmware, boot-policy, recovery or variable modification. Impact depends on activated component and privilege domain and can cross from OS to boot firmware or secure world. Persistent code execution requires successful activation and control transfer to attacker-controlled code.

## Related knowledge and primary sources

Firmware boot-chain, update binding, UEFI and secure-world references provide component and activation contracts. This profile keeps actor role and protected firmware object explicit.

Reviewed 2026-10-09 against [RFC 9019](https://www.rfc-editor.org/rfc/rfc9019.html) for the separation between image author authentication, authorization policy, firmware consumer and verifier roles. The example is hypothetical and does not impose that architecture on every firmware platform.
