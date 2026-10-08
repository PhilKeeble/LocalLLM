---
id: reference-parser-offset-based-serialization
title: Offset-based serialization, FlatBuffers tables and verification boundaries
kind: reference
topics: [parsers, serialization, flatbuffers, offsets, zero-copy, schema, verification]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Offset-based serialization evidence

## FlatBuffers encoded layout is not the host compiler's struct layout

In the ordinary 32-bit-offset FlatBuffers layout, scalars are little-endian,
structs are inline with format-defined alignment, and tables are reached by
offsets. Table fields have no fixed physical order. [1]

Investigative inference: do not apply a recovered native sizeof/offsetof model
directly to serialized bytes. Identify the actual offset-width variant and outer
framing before interpreting its root. A familiar layout is a hypothesis until
generated accessors or the consuming code corroborate it.

## FlatBuffers pointer-field offsets use the offset field's own address

In the inspected C++ Table::GetPointer implementation, a present pointer field
at address P resolves to P plus the unsigned offset read at P. The vtable first
locates P within the table; these are two different offset calculations. The
implementation provides both ordinary and 64-bit offset accessors. [3]

Investigative inference: record which base each addition uses. An offset valid
relative to the buffer start may be wrong relative to its own field. Recover
width and checked target extent before following it; a decoded address alone is
not evidence that its target is a complete valid object.

## FlatBuffers vtable is field metadata, not C++ virtual dispatch

A FlatBuffers table begins with a signed offset subtracted from the table start
to locate its vtable. Vtable entries describe field locations; a missing entry
or zero field offset yields the accessor's default. The vtable can be on either
side of the table. [1]

Investigative inference: a subtraction before field access is not automatically
a negative-length bug. Recover base, sign and field extent. Conversely, an in-range
metadata pointer alone does not establish that the selected field lies in bounds.
Do not label these field-offset tables as executable C++ function-pointer tables.

## FlatBuffers vectors and unions need schema-aware interpretation

In the ordinary FlatBuffers layout, vectors carry a 32-bit element count. Strings
are byte vectors with a trailing NUL excluded from their count. A union uses a
selection enum plus an offset to its value; NONE denotes an unset union. [1]

Investigative inference: distinguish element count from byte span and selection
tag from payload validity. Recover the element type and matching union arm before
following offsets or multiplying sizes. A NUL terminator does not establish that
every consumer uses the full counted string.

## FlatBuffers C++ accessors do not substitute for buffer verification

The FlatBuffers C++ guide distinguishes fast generated accessors from the optional
verifier. The verifier checks structural offsets, field sizes and string termination;
it also supports depth/table-count limits. [2]

Investigative inference: locate the actual verification call, checked result,
root schema and buffer/length passed to it. Importing a verifier is not evidence
that it dominates all accesses. Structural verification does not prove application
authorization, cross-field policy or harmless content.

## Verification of one byte snapshot does not protect later mutation

Analytical boundary: a successful structural check applies to the representation
checked. Constructed case: a shared serialized buffer passes verification, then
another writer changes an offset before an unchecked accessor uses it. The earlier
result does not establish the new offset's validity.

Recover immutable storage, ownership, synchronization or copying that binds use
to checked bytes. Zero-copy means using the serialized storage directly; it is not
a lifetime or concurrency guarantee. Use
reference-concurrency-mutable-validation-double-fetch for mutable validation.

## Primary sources and scope

Reviewed 2026-10-02. Living FlatBuffers internals and C++ documentation; the layout
sections describe the ordinary 32-bit-offset form, not every extension or binding.
Custom offset formats require their own bases and schema evidence.
Workflow: playbook-re-serialization-schema-boundary.

1. [FlatBuffers internals: structs, tables, unions and vectors](https://flatbuffers.dev/internals/).
2. [FlatBuffers C++: access of untrusted buffers](https://flatbuffers.dev/languages/cpp/#access-of-untrusted-buffers).
3. [FlatBuffers C++ table.h, Table::GetPointer/GetPointer64](https://github.com/google/flatbuffers/blob/master/include/flatbuffers/table.h), master source inspected 2026-10-02; implementation evidence, not a claim that every binding uses identical code.
