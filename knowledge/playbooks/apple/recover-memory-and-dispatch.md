---
id: playbook-apple-memory-dispatch
title: Recover Apple runtime dispatch, driver arguments and asynchronous lifetime
kind: playbook
topics: [apple, dispatch, ownership, iokit, callbacks, pointer-authentication]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# Apple dispatch and lifetime investigation

## Recover the executed target and its actual calling convention

For Objective-C, bind selector, possible receiver class, category/forwarding and
resolved implementation. For Swift, distinguish value witnesses, protocol
witnesses, native calls, interoperability thunks and async resumes. A symbol or
selector string alone does not prove behavior. Use reference-objc-dispatch-type-evidence
and reference-swift-metadata-abi; the shared workflow is
playbook-re-objc-swift-boundary.

## Reconstruct ownership independently from representation

Track strong owners, borrowed/weak references, autorelease boundaries, block
captures and raw pointees. Recover both callback-context and underlying-buffer
lifetime through registration, failure, cancellation and final completion.
Retaining a closure does not deep-copy a captured C buffer.

Use reference-objc-ownership-blocks and reference-swift-ownership-native-boundaries.
Ownership protects lifetime, not mutable-state consistency or authority. Await
can permit logical state changes even when individual accesses are isolated.

## Bind driver dispatch to validated extents and outstanding work

Identify actual IOKit or DriverKit user client, selector contract, scalar counts,
structure sizes and output capacity. Follow mapping/backing identity, mutable
aliases, object references and outstanding I/O through close and completion.
Submission success cannot certify completion or immutable input.

Use reference-apple-iokit-user-client-memory. Preserve platform/API distinctions;
no universal selector numbering, argument layout or driver dispatch table is assumed.

## Interpret authenticated pointers and crashes within their target scope

Determine architecture, ABI, pointer role and supported decoding. Distinguish
pointer stripping from authentication and a lifetime/bounds defect from a
mitigation-related failure. A decoded address or crash alone does not establish
controllable execution. Use reference-apple-arm64e-pointer-auth-evidence.

## Basis and finding limits

Reviewed 2026-10-08 against the linked reference contracts. A supported finding
requires input/path, required invariant and effect; unresolved ownership or dispatch
is reported as missing evidence. Runtime helpers and driver APIs also occur in
ordinary software. No target execution, exploit procedure or fixed private offsets.
