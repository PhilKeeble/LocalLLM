---
id: playbook-re-object-reconstruction-boundary
title: Recover deserialization type selection, callbacks and object invariants
kind: playbook
topics: [reverse-engineering, deserialization, callbacks, object-graphs, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Investigate object reconstruction from untrusted input

## Distinguish record decoding from object activation

Identify the library, entry point, declared destination type, options and effective
custom registrations. Trace input provenance through transport, storage, decoding
and decompression. Determine whether the operation returns inert records, binds
fields into a fixed type, selects among a closed set, resolves names dynamically
or invokes application-provided factories.

A method named deserialize does not establish which contract applies. Find the
selected implementation, including generated or monomorphized code, wrappers and
nested parsers. Do not activate an unknown graph merely to list its types. Use
bounded structural evidence and preserve unresolved names, buffers and dependencies.

## Put construction, checks and side effects in execution order

Recover type admission, allocation, constructors or constructor bypass, field
writes, setters, conversion functions, callbacks, replacement and final use.
For each intended invariant, identify the branch that enforces it and whether
that branch executes before the relevant effect.

An invariant is a condition the object must satisfy, such as count matching an
allocated extent or a resource belonging to the requesting tenant. A normal
constructor that enforces it may not run during restoration. A check after load
cannot prevent earlier callback effects. A final exception does not establish
rollback; follow handlers, published references and external writes.

## Trace the exact graph and values used after reconstruction

Separate field presence, nullness, numeric/string range, type admission, graph
relationships and operation authorization. Record defaults, aliases, duplicates,
unknown fields, replacement versus population and forwarded extension data.
Preserve original bytes before reserialization erases differences.

Recover shared references, cycles, external object IDs and separately supplied
buffers. Show that the consumer uses the same object/value version that validation
checked. A type allowlist does not establish child ownership, immutable contents
or complete resource bounds. A cycle-safe traversal also needs to account for
the policy context in which a shared object is visited.

## Distinguish a vulnerability from a malware behavior claim

For a vulnerability, connect controlled input to the effective reconstruction
path, surviving checks, violated invariant and security consequence. An installed
library, dangerous API or familiar gadget-class name alone is insufficient.
Identify counterevidence such as rejection before the relevant callback or a
closed mapping whose permitted operations remain correctly constrained.

For malware analysis, follow reconstructed configuration or executable requests
into actual handlers and effects. Separate stored capability, statically reachable
behavior and observed execution. Obfuscated names, custom tags or callbacks can
be legitimate; evaluate what they select and do, under whose authority. Preserve
unresolved imports, unsupported formats and missing external objects as limits.

## Route to the serializer's actual factual contract

- Python pickle/JSON hooks: `reference-parser-python-object-reconstruction`.
- YAML construction and shared aliases: `reference-parser-yaml-tags-construction-aliases`.
- Rust Serde fields and variants: `reference-parser-serde-type-binding-validation`.
- Java construction and filters: `reference-jvm-serialization-construction-and-graphs`, `reference-jvm-serialization-filters`, `playbook-re-jvm-deserialization-boundary`.
- .NET binding and activation: `reference-dotnet-json-contracts`, `reference-dotnet-serializer-type-and-state-boundaries`, `playbook-re-dotnet-deserialization-boundary`.

Reviewed 2026-10-02. The linked references contain primary-source contracts and
their limits. This workflow is not a guarantee that a loader labeled safe,
a valid signature, authenticated transport or a final object cast makes arbitrary
reconstruction safe. Resource budgets must cover bytes, objects, repeated work,
external resolution and callback effects separately.
