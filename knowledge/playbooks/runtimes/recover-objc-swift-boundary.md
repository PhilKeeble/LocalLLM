---
id: playbook-re-objc-swift-boundary
title: Recover Objective-C and Swift dispatch, ownership and security-relevant effects
kind: playbook
topics: [objective-c, swift, reverse-engineering, vulnerability-analysis, malware-analysis, callbacks]
platforms: [macos, ios, linux, windows]
architectures: [x64, arm64]
---
# Investigate Objective-C and Swift boundaries

## Start with the binary and the actual runtime path

Identify architecture, executable mapping, loaded libraries and relevant runtime
families. Apple Objective-C facts do not automatically apply to another Objective-C
implementation; Swift exists beyond Apple systems. Separate compiler/runtime
helpers from application code without deleting their lifetime or dispatch edges.

For a vulnerability task, select a caller-controlled value and the invariant it
must satisfy. For malware analysis, select a behavior question and trace the
trigger, controlling data and effect. A runtime name or selector is a lead, not
the conclusion. Use `reference-objc-dispatch-type-evidence` and
`reference-swift-metadata-abi` for the applicable facts.

## Resolve the callback or dynamic method before trusting a call graph

For Objective-C, record receiver identity, selector, candidate implementation,
method signature and any registration/replacement/forwarding path. For Swift,
separate value-management witnesses from protocol dispatch, and identify the
concrete type or constrained candidate set. Preserve unresolved alternatives.

For a block or closure, trace creation/captures, registration, invoke and disposal.
A copy/dispose helper is not the behavior-bearing callback. At a Swift/C/Objective-C
adapter, reconstruct both calling conventions rather than forcing one decompiler
prototype across the boundary. Record whether the path is statically possible or
actually observed; neither substitutes for the other.

## Follow input through ownership, conversion and validation

Track the value from file/network/configuration or IPC decoding to its consumer.
Keep object identity, byte extent, element count and caller authority distinct.
Type metadata can explain representation but cannot prove input legitimacy.
Inspect nil/error branches and the exact comparison that permits the effect.

At each retained callback or native pointer export, identify the owning object or
allocation, transfer rule, last valid use and cleanup on failure/cancellation.
Use `reference-objc-ownership-blocks` and
`reference-swift-ownership-native-boundaries`. A closure retained beyond its
creator does not by itself preserve a captured raw buffer.

## Reconstruct re-entry and suspension around security decisions

Treat dynamic resolution, destructor cleanup and callbacks as potential calls
into other code. For actor-based work, compare the state before and after each
possible suspension. Ask whether object ownership, permissions, request identity
or resource reservation can change before the effect.

A useful finding names the violated invariant, controlling input, feasible
ordering and resulting access or state change. Distinguish checked runtime traps,
resource exhaustion, unsafe native memory accesses and logical authorization
failures. Memory-safety checks do not establish correct security policy.

## Attribute behavior to effects, not language artifacts

For a suspicious selector, dynamic method replacement or native callback, recover
what data reaches what operation under which trigger. Separate a capability
present in linked code, a feasible use by the sample and an observed execution.
Framework dispatch, ARC helpers, mangled symbols and closure machinery occur in
ordinary applications as well as malware.

Report remaining uncertainty explicitly: receiver/type ambiguity, unresolved
native target, unknown callback lifetime or missing environment condition. Use
`playbook-re-sensitive-data-flow` for source-to-effect tracing and
`playbook-re-validate-library-attribution` for separating shared-library behavior
from sample-specific behavior. Those distinctions prevent both false positives
and premature declarations that the boundary is safe.

## Evidence basis and limits

Reviewed 2026-10-02. Investigation procedure derived from the primary-backed
runtime references identified in each section. This is a runtime-boundary
workflow, not an Apple signing, entitlement, sandbox or persistence reference.
