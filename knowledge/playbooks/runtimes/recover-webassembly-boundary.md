---
id: playbook-re-webassembly-boundary
title: Investigate WebAssembly guest bugs, host capabilities and payload behavior
kind: playbook
topics: [reverse-engineering, webassembly, wasm, vulnerability-analysis, malware-analysis, native-bindings]
platforms: [windows, linux, macos]
architectures: [wasm32, wasm64, x64, arm64]
---
# Investigate a WebAssembly boundary

## Identify the artifact and its loader before interpreting its guarantees

Distinguish core module, component, text representation and engine-native compiled
cache. Trace embedded/downloaded bytes through decoding or decompression into
the actual loader. Record engine/configuration evidence without guessing it from
magic bytes or producer names. Instantiation may execute a core start function;
do not instantiate an unknown sample merely to list its contents.

Use reference-wasm-module-control-flow and reference-wasm-runtime-trust-limits.
A failure to decode can reflect an unsupported feature, wrong format or malformed
input; it does not alone identify maliciousness or an engine defect.

## Map entry points, imports and indirect dispatch to actual targets

Reconcile imported-function indices with code-section bodies. Recover start and
host-invoked exports, structured branch targets and relevant indirect table
contents. Follow host linker registrations/import objects to concrete callbacks.
For components, include interface adapters and resource-handle implementations.

Record the trigger, binding, input and downstream operation for each relevant
path. A signature-compatible indirect call or correctly linked import is not
proof of intended authorization. reference-wasm-host-capabilities supplies the
core/WASI/component distinctions.

## Track guest object bounds separately from linear-memory extent

For a suspected buffer bug, record selected memory, offset, access width, object
capacity, arithmetic width and allocation lifetime. Distinguish a prior wrapping
integer calculation from the memory instruction's effective-address calculation.
Follow error and growth-failure results into the eventual use.

Use reference-wasm-linear-memory. Ask whether the violation crosses an object,
allocation, whole memory or host boundary; these are different claims. Recover
what the overwritten/read bytes influence instead of treating every guest
overflow as native control-flow takeover.

## Audit native pointer conversion, re-entry and retained views

Follow pointer/length pairs into the host's range checks and copy/access API.
Keep byte counts distinct from pages or element counts. Identify callbacks,
memory growth, concurrent writers and asynchronous retention between validation
and use. For JavaScript, identify buffer mode rather than assuming detachment.

Establish which bytes were validated and which bytes the sink later consumes.
An in-bounds but changed path/request can cause a logic failure even when a raw
native pointer remains valid. For a lifetime finding, name the invalidation edge
and subsequent use rather than merely noting an unsafe API.

## Compare granted authority and execution limits with the intended policy

Recover actual WASI preopens/permissions and any custom network, file or command
bindings. Identify whether the host acts with its own authority or a narrower
request-specific identity. Inspect fuel/epoch setup and separately account for
host blocking work, allocations and queued callbacks.

Follow trap/error cleanup and any effects already committed. State the missing
invariant: resource authorization, object lifetime, range, integrity or budget.
A powerful intentionally granted capability is not itself a vulnerability.

## Report feasible behavior without conflating capability and observation

For malware analysis, connect payload entry, decoded data, imported effect and
destination; separate runtime/library helpers from sample-specific logic.
Distinguish capability presence, reachable behavior under a stated host, and
observed execution. Missing host bindings or payload stages remain limitations.

For vulnerability analysis, report controlled input, the violated invariant,
feasible path and bounded consequence. Identify whether evidence supports a
guest-only defect, host misuse or engine failure. Use
playbook-re-sensitive-data-flow for cross-boundary value tracking.

## Evidence basis and scope

Reviewed 2026-10-02. This procedure applies the four WebAssembly references named
above and their primary sources. It does not assume a particular browser, WASI
generation, source language or engine-native artifact layout.
