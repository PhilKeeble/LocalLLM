---
id: playbook-re-dotnet-deserialization-boundary
title: Recover a .NET deserialization boundary and its actual validation path
kind: playbook
topics: [reverse-engineering, dotnet, deserialization, type-resolution, validation, logic-bugs]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Recover a .NET deserialization boundary

## Bind bytes to the real entry and implementation

Reviewed 2026-10-02. Preserve input provenance, trust boundary, transport framing,
compression/encoding and original bytes. Resolve the deserializer call using
module/hash, token, overload, declared root type and loaded library identity.
Use playbook-re-dotnet-method-dispatch for managed/native mapping. An imported
type name does not prove the call is reached or the implementation is enabled.

Separate BinaryFormatter/compatibility code, Json.NET, System.Text.Json,
DataContractSerializer, NetDataContractSerializer and custom adapters. Record
settings constructed locally or injected by a framework, type/member attributes,
resolvers, binders and generated contracts. A library's default is only a starting
hypothesis until the call site's effective configuration is established.

## Recover concrete type selection before following object members

Trace discriminators/type metadata to the resolved type and assembly instance.
Include member/item overrides, generic/nested values, converters, known-type
providers, fallback behavior and custom resolvers. Establish whether the input
selects a fixed mapping or can request broader loading; equal printed names
alone do not establish type identity or trusted provenance.

Do not execute unknown payloads or activate unknown types for discovery. For
NRBF inspection distinguish bounded record decoding from object construction.
A binder around BinaryFormatter is not a general safety guarantee; a configured
System.Text.Json discriminator is not automatically arbitrary CLR activation.
Facts: reference-dotnet-serializer-type-and-state-boundaries and
reference-dotnet-json-contracts.

## Reconstruct construction, mutation and rejection order

List selected constructors/factories, initializers, direct field writes, setters,
converters, callbacks and graph fixups. Follow actual call/assignment order and
which validation branches execute. Determine replacement versus population,
retained defaults, shared references/cycles and extension data forwarded later.

Trace exceptions through catches and serializer error handlers. Determine whether
partial values or external side effects survive rejection, whether a callback
runs, and whether the caller uses the result after a handled error. A validation
method on the type is not evidence of protection if the serializer bypasses it.
Do not assume a failed Deserialize call rolls back setters or static mutations.

## Separate presence, value, shape and operation rules

For each security-relevant field distinguish absent, explicit null, empty,
zero/default, duplicate and unknown input. Recover case matching, wire aliases,
numeric coercion and range checks. Check root values and collection elements,
not just top-level member attributes. Record whether a newer opt-in API exists
in the deployed library and is enabled at this entry.

Follow graph-wide invariants through the final consumer: owner/tenant binding,
legal state transitions, allowed paths/operations, count relationships and
authority. Type acceptance, syntax validity and non-nullness do not prove these
invariants. Use playbook-re-reconstruct-operation-invariants for the application
logic boundary after decoding.

## Compare validator and consumer on the same preserved input

Compare the validator's and consumer's effective code paths for omission/null,
duplicate order, case variants, quoted versus numeric values, unknown fields and
repeated references. Recover the selected values, not just nominal success/failure.
Use instruction/IL and contract evidence first; runtime observations, if separately
authorized, need an isolated environment matching the target's relevant settings.

Match runtime/library/options to the target; label deliberately different
configurations as constructed differentials, not target findings. Preserve raw
bytes before any parse-and-reserialize step can discard duplicate/order evidence.
Cap input sizes, callback effects and execution time; do not test allocation
exhaustion or execute unknown gadget payloads merely to inspect a document.

For malware analysis, follow restored configuration and callback parameters into
their handlers: a deserialized path, URL or type name is not itself evidence that
the corresponding file, network or loading operation occurred. Keep stored values,
reachable behavior and observed effects separate.

## Decide whether the evidence supports a finding

Require controlled input, reachable effective contract, exact check/use mismatch
or unsafe activation, feasible affected state and a security consequence.
Counterevidence includes a throwing disabled implementation, rejected unmapped
type, an effective required/null check, validation before side effects, or a
consumer using the same validated immutable representation.

Report unresolved transitions explicitly. A dangerous API is a high-priority
review surface, not proof of a particular exploit; a successful small test is
not proof of complete parser safety. Resource review must separately cover bytes,
nesting, collection width, decompression and custom-converter work.

## Sources and factual homes

- [BinaryFormatter security](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide): unsafe activation/binder limits.
- [System.Text.Json contracts](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/required-properties): presence versus effective contract.
- [Json.NET settings](https://www.newtonsoft.com/json/help/html/SerializationSettings.htm): actual serializer configuration.

reference-dotnet-json-contracts and
reference-dotnet-serializer-type-and-state-boundaries hold scoped API facts,
source sections and version caveats. This playbook supplies the investigation
sequence, not an observed defect in a target binary.
