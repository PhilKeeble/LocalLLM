---
id: reference-windows-rpc-dispatch-ndr-metadata
title: Windows RPC dispatch tables and DCE NDR versus NDR64 interpreter metadata
kind: reference
topics: [windows, rpc, midl, ndr, ndr64, stubs, dispatch, binary-layout]
platforms: [windows]
architectures: [x86, x64]
---

# Windows RPC dispatch tables and interpreter metadata

## Scope and evidence

Reviewed 2026-10-02 against Microsoft's NDR format documentation and Windows SDK
10.0.22621.0 declarations in rpcdcep.h, rpcndr.h and ndr64types.h. The field
descriptions below summarize those headers; they are not universal binary offsets.
Private interpreter structures require matching the target architecture, packing
and metadata family. Public RPC contracts and actual registration take precedence
over an inferred structure match.

Use reference-windows-rpc-interface-stub-evidence to establish registration,
effective manager selection and selected transfer syntax. This reference supplies
decoding distinctions, not a complete NDR implementation.

## RPC dispatch functions and manager entry points are different tables

The reviewed SDK's RPC_SERVER_INTERFACE contains interface/transfer-syntax
identifiers, an RPC dispatch-table pointer and InterpreterInfo. MIDL_SERVER_INFO
instead contains a SERVER_ROUTINE dispatch vector, stub descriptor, procedure
format data, format-offset table, thunk table and transfer-syntax information.

Investigative consequence: similarly named DispatchTable fields are not
interchangeable. Repeated interpreter entry addresses do not establish identical
application methods. Follow the applicable metadata and actual registration to
the effective manager, rather than assigning the interpreter's behavior to every
method. Do not assume every server uses interpreted rather than inline stubs.
These are native structures; recover target pointer widths before following them.

## DCE NDR procedure headers have variable forms

Microsoft's documented DCE procedure-header family includes handle type, flags,
optional RPC flags, procedure number and argument-stack size. Explicit binding
descriptions and later extensions add fields. Compiler mode affects the form;
there is no universal fixed header length or method stride. [1]

Recover the applicable procedure-format base and offset table before decoding.
A format offset is a metadata coordinate, not an RVA, manager address or packet
offset. Bound each read and decode optional fields before advancing to the next
record. Successful decoding of one description does not validate the remainder.

## Oif parameter records separate attributes, stack coordinates and type data

A documented DCE Oif parameter descriptor occupies six bytes: two-byte
attributes, two-byte virtual stack offset, then a base-type code plus padding
or a two-byte type-format offset. Older Oi records use different forms. IsIn,
IsOut and IsReturn describe direction/result; IsBasetype selects the last field's
interpretation. IsSimpleRef can select the referent description directly rather
than an additional pointer descriptor. [2]

MustSize and MustFree concern NDR sizing/freeing, not permission for the manager
to free any pointer. StackOffset is a virtual argument coordinate, not a packet
offset or automatically a hardware stack load. Recover source-level signedness
from the combined descriptor, correlation and native-use evidence, not a guessed
source declaration. Do not apply DCE descriptor strides to NDR64 fragments.

## NDR64 fragment structures are interpreter data, not wire structs

The reviewed SDK declares NDR64_PROC_FORMAT with 32-bit Flags, StackSize and
constant client/server buffer sizes, followed by 16-bit RpcFlags, FloatDoubleMask,
NumberOfParams and ExtensionSize. NDR64_PARAM_FORMAT contains a native
type-description pointer, attributes/reserved fields and a 32-bit StackOffset.

These structures do not describe a network PDU to copy into native memory.
Native metadata pointers are not serialized client addresses. Determine the
selected transfer syntax and actual table representation before interpreting
offsets or pointers; a field name alone is insufficient. Follow explicit type
and expression relationships rather than assuming adjacent fragment order
establishes parameter order or count correlation.

## A recovered descriptor is not proof of a reachable bug

Keep three separate maps: method to effective manager, parameter to native
argument/type description, and parameter to wire contract for the selected
syntax. Bounds-check metadata against its containing image/mapping and compare
accepted values with manager allocation, copies and cleanup. Unknown format
codes must remain unresolved rather than silently becoming plain pointers.

A descriptor does not establish authentication, resource authorization, current
manager selection or runtime acceptance. A candidate needs an independently
supported input path and violated application invariant; the stub may reject it
before dispatch. Use reference-windows-ndr-marshaling-contracts for wire/count
rules and playbook-re-rpc-wire-to-manager for investigation order.

## Primary sources

- [1] [Microsoft procedure-header descriptors](https://learn.microsoft.com/en-us/windows/win32/rpc/procedure-header-descriptor): optional fields, procedure numbers and stack size.
- [2] [Microsoft parameter descriptors](https://learn.microsoft.com/en-us/windows/win32/rpc/parameter-descriptors): Oi/Oif forms, virtual offsets and attribute interpretation.
- Windows SDK 10.0.22621.0: rpcdcep.h, RPC_SERVER_INTERFACE; rpcndr.h, MIDL_SERVER_INFO and MIDL_SYNTAX_INFO; ndr64types.h, NDR64_PROC_FORMAT and NDR64_PARAM_FORMAT. Relevant declarations are summarized above so interpretation does not depend on local SDK access.
