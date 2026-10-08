---
id: playbook-re-jvm-deserialization-boundary
title: Investigate Java deserialization from input bytes through filters, callbacks and use
kind: playbook
topics: [reverse-engineering, jvm, deserialization, serialization-filters, callbacks, validation]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Investigate a Java deserialization boundary

## Preserve the actual parser and trust boundary

Reviewed 2026-10-02. Identify the library/API and version, stream subclass,
runtime build, dependency/class hashes, defining loaders and effective
configuration. Separate Java Object Serialization from JSON/XML binding,
Kryo, Android parceling and custom binary readers. A method named readObject
does not by itself establish ObjectInputStream semantics.

Trace controlled bytes through framing, decoding, decompression, authentication
and storage to the exact parser. State the input trust and intended invariant.
Treat encrypted transport and authenticated sender identity separately from
permission to select types, values or operations. Preserve data without invoking
unknown constructors, loaders, hooks or object methods just to inspect it.

## Recover descriptors, field mappings and live classes

For standard object streams, decode bounded headers, descriptors, field types,
handle references and reset epochs. Preserve byte offsets and declared versus
available extents. Use structural inspection rather than deserializing an
unknown graph on the analyst's machine. A class name or valid stream header is
not a finding or an authenticity check.

Follow actual resolveClass/resolveProxyClass implementations and loader results.
Map descriptors to the installed class definitions, including hooks and custom
field mappings. Keep serialVersionUID compatibility separate from identity,
integrity and application policy. Use playbook-re-jvm-method-and-dispatch for
the actual bytecode and callback body rather than trusting source-like output.

## Recover the effective Java serialization filter, not just its setting

Record JVM-wide configuration, factory selection, stream construction and any
setObjectInputFilter call with outcomes and ordering. Reconstruct current,
requested and returned filters. With a custom factory, preserve the actual
thread/caller context used to choose policy; do not infer automatic intersection.

Evaluate exact patterns, first-match order, whitespace, module/package/array
semantics, limits and all three statuses. Check null-class callbacks and wrapper
exceptions. Distinguish a missing filter, UNDECIDED and a null returned status.
Trace each nested stream separately. Facts: reference-jvm-serialization-filters.

## Trace construction, callbacks and partial state before rejection

Classify ordinary Serializable, Externalizable, record, enum, array and proxy
paths before assigning constructor rules. Recover superclass restoration,
readObject/readObjectNoData/readExternal, canonical constructors, replacement
hooks and registered validation. Inspect exact signatures, not only names.

Place value checks and side effects on a timeline. A validating constructor may
be bypassed; a constructor that does run may be followed by unchecked overwrites.
A post-read cast, filter rejection of a replacement or graph validation can be
later than an important callback. Track exception handlers and escaped state;
do not assume a failed readObject rolls back work already performed.

## Validate the graph actually used and independent resource bounds

Track object identities, aliases, cycles, replacements and mutable children.
Show that the later consumer sees the same value/object version that was checked.
readUnshared does not establish recursive independent ownership. Ordinary-object
and record-cycle behavior differ. Facts:
reference-jvm-serialization-construction-and-graphs.

Separate class admission from field invariants and operation authorization.
Check byte/time/allocation limits before and during reconstruction, including
primitive/string reads and callback work not fully represented by filter metrics.
Do not call toString, hashCode or other unknown object methods for convenience
while inspecting a graph; those are additional executions to justify and trace.

## Compare restoration paths and record missing evidence

Compare the effective code paths for valid versus invalid constructor input,
absent versus explicit-default fields, aliased versus independent children,
array counts around a limit and opposite class-pattern orders. Use bytecode,
configuration and graph evidence to establish the distinction before considering
separately authorized isolated execution. Do not change the target's process-wide
filter factory merely to inspect a policy hypothesis.

Record runtime and class identity, exact input/coordinates, effective filter,
callback path and rejection stage. Do not replay an untrusted gadget graph,
disable safeguards or exhaust resources merely to inventory content. A modeled
filter decision is not proof the real parser reaches the corresponding callback.

For malware analysis, trace restored configuration and handler state into actual
operations. A stream descriptor naming a powerful class is a lead, not proof of
malicious use. Preserve missing classes, unresolved loaders and unexamined nested
streams instead of treating failed reconstruction as a benign verdict.

## Sufficiency and counterevidence

A supported finding links controlled input to the actual parser and live types,
effective filter decisions, feasible callback/graph path, violated invariant and
observable consequence. Dependency presence or a famous class name is not enough.
Counterevidence includes rejection before the relevant callback, an unreachable
type under the effective policy, a correctly enforced value/identity invariant,
or a different serializer with independently verified contracts.

Report unresolved edges explicitly, including loader identity, nested parser,
factory context and partial effects. Rejection and successful parsing both need
stage-specific interpretation. Keep isolated test observations distinct from target
evidence and avoid claiming universal safety from a bounded regression suite.

## Sources and factual homes

- [Java Object Serialization specification, JDK 25](https://docs.oracle.com/en/java/javase/25/docs/specs/serialization/index.html): versioned input, graph and stream contracts.
- reference-jvm-serialization-construction-and-graphs: construction, hooks, identity and failure.
- reference-jvm-serialization-filters: installation, composition, callback coverage and limits.
- reference-jvm-loading-and-reflection: defining-loader identity and execution before intended target entry.
