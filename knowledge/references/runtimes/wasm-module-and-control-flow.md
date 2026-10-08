---
id: reference-wasm-module-control-flow
title: WebAssembly binary sections, indices, structured branches and indirect calls
kind: reference
topics: [webassembly, wasm, binary-format, leb128, control-flow, indirect-calls]
platforms: [windows, linux, macos]
architectures: [wasm32, wasm64]
---
# WebAssembly module and control-flow evidence

## Core Wasm magic and format version do not identify enabled features

A core binary begins with bytes 00 61 73 6d and format-version bytes 01 00 00 00.
The current core specification still uses this format version. [1] Do not infer
the supported instruction set, compiler version or runtime configuration from
that field. Identify required instructions/types and the target engine's enabled
features separately. Distinguish a core module from a component container or
engine-specific compiled artifact before applying a decoder.

## Section lengths and custom sections are parsing evidence, not provenance

Each core section has a one-byte ID and an unsigned-LEB128 byte length for its
contents. Noncustom sections follow the specification's order, not simply
ascending numeric IDs; custom sections may repeat and occur between them.
Custom sections are ignored by core execution semantics. Function type indices
and function bodies occur in separate function and code sections. [1]

Bound each parse to its declared section and body extent. Names, producer strings
and debug metadata are attribution leads, not authenticated compiler identity.
A malformed optional metadata payload need not imply invalid core instructions.

## LEB128 integers permit bounded nonminimal encodings

Wasm integer fields use signed or unsigned LEB128 as specified for that field,
not fixed-width little-endian reads. An N-bit encoding occupies at most
ceil(N/7) bytes; unused upper bits must satisfy the unsigned-zero or signed
extension constraints. Some nonminimal encodings within those limits are valid:
the specification gives unsigned 3 as either 03 or 83 00. [2]

When investigating parser disagreement, distinguish a forbidden overlong value
from a permitted nonminimal representation. Preserve encoded byte extent as
well as decoded value; they answer different offset and canonicalization questions.

## Function indices include imports; local indices begin with parameters

Core function, memory, table and global indices belong to separate zero-based
spaces. Imports precede definitions within each applicable space. Function
parameters occupy the first local indices, followed by declared locals. [3]

A call's function index is therefore not necessarily its ordinal in the code
section. Construct the import-prefix mapping before naming a callee. Keep
function index, type index, table slot, file offset and native JIT address as
different coordinates; confusing them can invent or hide a sensitive call.

## br and br_table target structured labels, not arbitrary byte addresses

Core br/br_if label operands count outward through enclosing control constructs:
zero selects the innermost label. Branching to block/if exits it; branching to
loop returns to its loop target. br_table chooses a listed label or its default. [4]

Recover nesting and operand-stack values before flattening the control-flow
graph. A decompiler's switch or loop syntax is a reconstruction, not the binary
encoding. Check which error or authorization branch actually dominates the use.

## call_indirect type checks do not establish intended callee identity

Core call uses a function index; call_indirect selects through a table and checks
the selected function against the expected type, trapping on mismatch. call_ref
uses a function reference. [4] A table stores typed references, not ordinary
linear-memory code bytes. [3]

For an attacker-influenced dispatch, recover reachable table contents and their
updates. A type-compatible but unintended function can still violate application
policy. Do not equate signature compatibility with authorization, or a guest
table slot with a writable native instruction pointer.

## Active data initialization and a start function precede exported calls

Active data segments initialize their selected memory during instantiation;
passive segments are available for explicit memory.init. A declared core start
function runs automatically after memory/table initialization. [3]

Instantiation is consequently an execution boundary, not a safe metadata-only
inspection step. Trace start-function calls when recovering payload activation.
An exported function named _start is not, solely because of that name, the core
start-section function; establish the host's invocation path separately.

## Primary sources and scope

Reviewed 2026-10-02 against the living WebAssembly 3.0 specification. These are
core-format and semantic rules, not a claim that every engine implements every
feature. Native compiled caches: reference-wasm-runtime-trust-limits.

1. [Core binary modules](https://webassembly.github.io/spec/core/binary/modules.html): header, sections, custom sections, function/code split.
2. [Core binary values](https://webassembly.github.io/spec/core/binary/values.html): signed/unsigned LEB128 and width constraints.
3. [Core module syntax](https://webassembly.github.io/spec/core/syntax/modules.html): index spaces, locals, tables, data and start.
4. [Core instruction syntax](https://webassembly.github.io/spec/core/syntax/instructions.html): control instructions and indirect calls.
