---
id: vulnerability-authentication-update-target-activation-gap
title: Update authentication not bound to component, device, sequence, and activation
kind: vulnerability
topics: [cryptography, updates, manifests, rollback, firmware, activation]
platforms: [cross-platform, firmware]
architectures: [any]
---

# Update authentication not bound to component, device, sequence, and activation

## Definition and violated invariant

An update trust vulnerability occurs when authenticated metadata or content is accepted without preserving its authorization binding to the intended component, product or device, accepted freshness state, exact installed bytes and activated object. Signature validity, rollback policy, safe installation and activation consistency are separate properties; success in one does not establish the others.

An older valid image is not automatically an unauthorized rollback. Recovery or operator policy may permit it. The defect requires acceptance contrary to the target's trusted sequence, version, expiry or recovery contract.

## Conditions that establish the issue

Recover the initial trust state, authorized signer or role, exact signed representation, target and device identifiers, component and destination, payload digest and extent, sequence or freshness rule, trusted time where applicable, retained monotonic state, download and transformation path, stable identity of installed bytes, activation selector, failure/restart transitions and recovery policy. Prove attacker influence breaks one required binding and causes forbidden installation or activation.

For rollback, identify the authenticated comparison field and authority able to reset it. For multi-component updates, trace dependencies and publication boundaries rather than treating archive membership as shared authorization.

## Evidence that is not sufficient

A signature check, old version string, unsigned URL, staged image, writable cache, two file opens, recovery slot, failed update or reboot request is not sufficient. Signed metadata may bind an external payload digest, protected storage may preserve identity, recovery may select an authorized prior image, or activation may independently reverify content.

Transport security authenticates its peer under that transport's policy; it does not by itself authorize the downloaded image, component or device target.

## Investigation sequence

Build an update ledger from trusted root and current state through metadata verification, role authorization, target selection, download, digest/length validation, transformation, staging, installation, persistent state update, activation and recovery. Record the exact object identity and transaction boundary at each step. Explore interruption before and after each persistent write and selector change.

At binary or firmware level, follow verified metadata fields into component selection, flash or filesystem coordinates, version comparisons and boot-slot handoff. Confirm that the verifier and activator refer to the same bytes and policy generation.

## Hypothetical component-binding example

```text
manifest = verify_signed(request.manifest)
image = download(manifest.image_url)
if hash(image) == manifest.image_digest:
    install(component=request.component, bytes=image)
```

The payload bytes are bound to signed metadata, but the shown destination component comes independently from the request. The path is vulnerable only if an attacker can select a component outside the signer's authorized target and no later policy binds that component before installation or activation.

## Primitive and impact limits

The direct primitive is installation or activation of authentic but unauthorized, stale, mismatched or substituted content, or an inconsistent persistent update state. Impact depends on selected component, execution authority, boot policy and recovery. Code execution follows only when the accepted bytes are invoked as code in the claimed context.

## Related knowledge and primary sources

`reference-crypto-update-trust-activation`, `reference-logic-update-verification-installation` and firmware boot references provide role, target, rollback and activation fundamentals. This profile keeps those bindings in the root-cause evidence chain.

Reviewed 2026-10-09 against [RFC 9019](https://www.rfc-editor.org/rfc/rfc9019.html) for firmware-consumer, verifier, invocation and recovery roles, [RFC 9124](https://www.rfc-editor.org/rfc/rfc9124.html) for manifest target and sequence concepts, and the [TUF specification](https://theupdateframework.github.io/specification/latest/) for one role-separated update model. The example is hypothetical; these sources do not prescribe every updater's structure.
