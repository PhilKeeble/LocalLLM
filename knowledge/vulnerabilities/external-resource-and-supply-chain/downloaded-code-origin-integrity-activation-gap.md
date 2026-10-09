---
id: vulnerability-external-downloaded-code-origin-integrity-activation-gap
title: Downloaded code or update activated without complete trust binding
kind: vulnerability
topics: [supply-chain, update, plugin, package, origin, integrity, activation]
platforms: [cross-platform]
architectures: [any]
---

# Downloaded code or update activated without complete trust binding

## Definition and violated invariant

This vulnerability occurs when a component downloads and activates code, a plugin, package, native cache, firmware, script, model extension, or update without binding trusted origin and integrity to the exact selected bytes, component identity, version/rollback policy, platform, and final consumer. The invariant is end-to-end authorization of one immutable artifact from metadata decision through activation.

Transport encryption, a digest, a signature, or a trusted repository is one control, not the complete binding. State which threat each control covers and what it authenticates.

## Conditions that establish the issue

Trace repository or update metadata, component name/namespace, delegated role, version and rollback state, target path, length/hash/signature scope, redirects and mirrors, cache key, temporary file, replacement authority, verification order, and loader/installer selection. Prove an attacker can substitute or select unauthorized bytes that the final consumer executes or installs.

Check time-of-check/time-of-use and multi-component mix-and-match: individually signed files can still be incompatible or unauthorized as one release if metadata does not bind their intended set and consumer.

## Evidence that is not sufficient

HTTP download, unsigned-looking data, a checksum, updater strings, writable cache, valid signature, or older version is not sufficient. The transport may be authenticated, content-addressed storage may bind bytes, the cache may be reverified, an older version may remain authorized, or activation may never occur.

A signature validates only the signed bytes and key policy. It does not inherently prove freshness, component name, deployment environment, authorization by the current trust root, or absence of rollback.

## Investigation sequence

Start at the update/package decision and preserve metadata and bytes as separate objects. Follow every transformation and copy to the final opened file or memory image, then establish the loader or installer and authority. Verify which fields are signed, threshold/delegation rules, expiration/rollback counters, root rotation, and failure fallback.

At binary level, distinguish hash computation from comparison and a successful verification branch from later selection. A trusted hash of one temporary followed by loading another path does not close the chain.

## Constructed flow

```text
manifest selects plugin A -> downloader verifies SHA-256 of temp file -> filename from response chooses cache destination -> loader opens cache/A by name
```

The digest check does not protect activation if an attacker can replace `cache/A` after verification or make the loader select a different object. Conversely, atomic content-addressed storage plus verification at the final open can defeat that substitution even if temporary names are writable.

## Primary sources and scope

Reviewed 2026-10-09 against [The Update Framework specification](https://theupdateframework.github.io/specification/latest/), IETF [RFC 9111 HTTP caching](https://www.rfc-editor.org/rfc/rfc9111), NIST [SP 800-218 Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final), and Uptane [deployment standard](https://uptane.org/docs/standard/uptane-standard). These frameworks supply distinct threat models; do not claim a target implements one without evidence.
