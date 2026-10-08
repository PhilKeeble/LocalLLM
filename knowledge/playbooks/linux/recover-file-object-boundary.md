---
id: playbook-linux-file-object-boundary
title: Recover Linux pathname selection, descriptor identity and file authority
kind: playbook
topics: [linux, file-descriptors, paths, object-identity, ownership, authorization, investigation]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover file selection and retained-object authority

## Identify the consumer and its actual path representation

Retain original input, decoded/normalized path, consumer API and actual flags.
Bind root, working directory, directory descriptor and mount namespace to the
same invocation. Determine whether the operation selects a pathname or consumes
an existing descriptor.

Apply reference-linux-path-resolution-identity. A path prefix, basename or
analyst-host resolution cannot certify the target object. A parser's normalized
display also cannot silently replace the bytes the consumer uses. If selection
is unresolved, report the requested object and missing relation rather than a
confirmed file operation.

## Establish enforced resolution constraints and fallback behavior

Recover absolute/relative handling, link and mount policy, feature support,
lookup result and any fallback. Identify how errors change the selected path.

Under the named Linux contracts, openat is a starting-directory mechanism;
ordinary O_NOFOLLOW addresses the final component; supported openat2 flags have
distinct constraints. Their full scope stays in reference-linux-path-resolution-identity.
An apparent containment call followed by unrestricted fallback needs its own
evidence. Do not infer escape or safety merely from API or flag presence.

## Bind each descriptor generation to the underlying object

Trace successful open, duplicate, inheritance or transfer to the descriptor used
by the operation. Retain open mode, object identity, shared offset/status and
descriptor-specific flags. Include close/replacement and reuse.

Use reference-linux-descriptors-open-file-descriptions. One integer across
processes or time is not object identity. A later pathname replacement need not
retarget an already held descriptor; a later descriptor reuse can. Preserve which
relation the evidence actually establishes. Authority for the specific operation
still needs its applicable credential and policy checks.

## Separate creation, checked object and later consumed content

For temporary files or multi-stage operations, identify creation result, retained
reference, name mutation interval, validation extent and actual consumed bytes.
Track whether the checked reference is the reference used later.

Exclusive creation does not authenticate every future reopening. A name check
does not freeze directory entries or content. Conversely, a theoretical mutation
possibility is not an observed effect. Establish the selected object's generation,
available mutability and decisive use; shared invariant guidance remains in
reference-logic-authorization-object-binding.

## Report the scoped selection and operation result

Deliver original/consumed path or reference, context, resolution constraints,
selected object generation, authority and actual effect. Distinguish attempts,
successful open, I/O completion and durable or externally observed state where
those levels matter.

Missing event history, inaccessible proc views or absent bytes limit the conclusion.
They do not establish that a file never existed or was maliciously removed.
Keep each missing relation next to the claim. This workflow can finish with a
conditional capability when available static evidence does not establish use.

## Basis and scope

Reviewed 2026-10-08. Applies the focused Linux path and descriptor references,
with shared parser, authorization and lifetime evidence. No fixed descriptor
numbers, filesystem-specific universal guarantees or runtime test artifacts.
