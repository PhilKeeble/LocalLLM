---
id: playbook-crypto-update-evidence
title: Recover update authority, verified objects and activation state
kind: playbook
topics: [updates, cryptography, signatures, rollback, trust, activation]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Update trust and activation investigation

## Recover the trust root and authority for the selected update

Identify installed trusted keys/roles, permitted targets, delegation, signature
threshold and the selected product/component. Recover how trust changes are
authorized. A valid signature under a supplied key does not prove that key may
authorize this update.

Use reference-crypto-update-trust-activation and
reference-crypto-signed-object-consumer-binding. Keep a framework-specific role
model scoped to that framework; do not assume every updater implements it.

## Trace verified metadata to the exact payload consumed

Follow the accepted target name, length, digest and signed metadata through
download, staging, unpacking and selection. Retain the relationship between
checked bytes and bytes actually installed, including mutable paths and handles.
A checked archive does not alone establish that a later-selected file is its
authorized content.

Use reference-logic-update-verification-installation for the shared updater
boundary. Report the first missing object binding instead of assuming replacement
or malicious modification happened.

## Recover freshness and rollback policy across recovery

Identify trusted retained version state, time source, expiry checks, rollback
comparison and the scope of each counter. Include reset, offline operation and
recovery paths when evidence exists. A larger untrusted version field or valid
old signature does not prove an acceptable current update.

Separate metadata freshness from firmware/application security-version policy.
Different components can have different rollback domains. Unknown retained state
prevents a global claim that downgrade is either possible or prevented.

## Follow installation through activation and failure

Map staging, installation, active-slot selection, commit and fallback, with
authorization and integrity preserved at each transition. Determine which
component will execute after reboot and which old state may be restored.
Cryptographic success does not certify crash consistency or successful activation.

Record whether a reported error leaves a partial effect. Distinguish an authorized
recovery route from unverified fallback. This is static evidence review; no update,
reboot or target modification is implied.

## Report the complete supported update chain

Write the chain as trusted authority → selected metadata → verified payload →
installed object → active component, with retained freshness state alongside it.
Mark unknown links explicitly. A tampered download rejected before installation
does not establish unauthorized execution.

Reviewed 2026-10-08 against reference-crypto-update-trust-activation and
reference-logic-update-verification-installation. Their source scopes govern
the facts; this workflow introduces no universal updater implementation or
specific release requirement.
