---
id: reference-windows-rpc-interface-stub-evidence
title: Windows RPC interface discovery and generated-stub evidence
kind: reference
topics: [windows, rpc, midl, interface-discovery, ndr, stubs]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows RPC interface discovery and generated-stub evidence

## Scope: registration, dispatch and wire evidence are distinct

Scope: Microsoft Remote Procedure Call (RPC) and its Interface Definition Language
compiler (MIDL), not a universal RPC implementation or a COM activation map.
Reviewed 2026-10-02 against the Microsoft contracts linked below. Separate
interface registration, endpoint discovery, selected implementation, wire
description, caller admission and method authorization. A discovered UUID is
not proof that the examined process serves it, that a particular client can
reach it, or that a sensitive operation is allowed.

Investigation evidence should bind the interface/version and procedure to an
actual registration path and manager implementation. Preserve build, image
mapping, transport/binding, process and observation time. Cross-link
`reference-windows-com-rpc-authentication-impersonation` for security layers and
`playbook-re-rpc-wire-to-manager` for the recovery sequence.

## Endpoint-map records are discovery records, not permissions

Windows `RpcEpRegisterW` adds endpoint-map entries using the interface UUID and
version, server bindings and optional object UUIDs. Its annotation is informational
and does not participate in server selection. A friendly annotation is not a
server identity or authorization decision. Dynamic endpoints can be collected
with `RpcServerInqBindings` and then registered.

Inference: endpoint-map data is a lead for correlating interface and transport,
not proof of a successful call from the tested principal. Conversely, failure to
find an entry is not a complete inventory of all target call paths; inspect the
binary's binding and registration paths as well. Do not confuse an object UUID
with an interface UUID or use an annotation match as an implementation match.
[RpcEpRegisterW](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcepregisterw).

## Registration can select a manager other than an assumed default

For Windows `RpcServerRegisterIfEx`, `IfSpec` is MIDL-generated interface data.
`MgrEpv` supplies the manager entry-point vector; NULL selects the generated
default. Manager type UUID and EPV determine the implementation; non-nil manager
types also require object/type registration through `RpcObjectSetType`.

Investigation implication: a plausible generated table is not sufficient if a
registration overrides its manager. Follow the effective arguments and their
success path. Keep the interface/procedure association separate from the
implementation address. No fixed table offset or universal decompiler structure
layout is asserted here.
[RpcServerRegisterIfEx](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcserverregisterifex).

## Authentication registration is not a mandatory-authentication policy

Windows `RpcServerRegisterAuthInfo` alone does not require authenticated calls.
For `RpcServerRegisterIfEx`, a registered security callback normally causes
automatic rejection of unauthenticated callers; `RPC_IF_ALLOW_CALLBACKS_WITH_NO_AUTH`
removes that automatic rejection. `RPC_IF_ALLOW_SECURE_ONLY` is another admission
control. Inspect the actual flags and callback, not just imported API names.

The security callback is not guaranteed to execute for every method call:
runtime admission is tracked by client/interface during a communication session,
and callbacks can also occur more than once. A callback accepting a client does
not establish current authorization for each resource or operation. Do not put
per-call state-transition assumptions on an admission callback without evidence.
[RpcServerRegisterIfEx security remarks](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcserverregisterifex).

## Security callback frequency and authenticated admission are separate controls

Windows RPC_IF_SEC_NO_CACHE disables interface-security-callback caching and
forces a callback for each call on that interface. It is available from Windows
XP SP2 / Server 2003 SP1. Recover the actual registration flags before applying
the default caching model. RPC_IF_ALLOW_CALLBACKS_WITH_NO_AUTH controls whether
unauthenticated calls can reach that callback; it does not mean the callback
accepts them. A security callback is not a MIDL static client callback.

RPC_IF_ALLOW_SECURE_ONLY does not imply a privileged caller or method/resource
authorization. It requires an authentication level above NONE under the
documented rules; it is not a requirement for packet confidentiality. Preserve
runtime/version qualifications, authentication settings and application checks
separately. Removing callback caching does not automatically make its policy
correct for mutable resource state.
[Interface registration flags](https://learn.microsoft.com/en-us/windows/win32/rpc/interface-registration-flags).

## MIDL_STUB_DESC distinguishes type data, helpers and versions

In Windows MIDL-generated stubs, `pFormatTypes` identifies type descriptions;
`apfnExprEval` supplies complex correlation-expression helpers;
`aUserMarshalQuadruple` identifies user/wire marshaling routines;
`apfnNdrRundownRoutines` identifies context cleanup. `Version` is the required
NDR version, whereas `MIDLVersion` identifies the generating compiler version.
Neither field is the target OS build. `fCheckBounds` describes the MIDL `/error`
option; it is not proof that every application bounds check exists.

`RpcInterfaceInformation` points to server/client interface data for nonobject
RPC but is NULL for an object interface. NULL therefore does not by itself prove
an invalid stub descriptor. Allocator/free fields identify stub memory management;
do not substitute an assumed application allocator. Recover target-width layout
from the matching SDK/generated artifacts before following binary offsets.
[MIDL_STUB_DESC member contracts](https://learn.microsoft.com/en-us/windows/win32/api/rpcndr/ns-rpcndr-midl_stub_desc).

## Format descriptors are not payload bytes or manager function bodies

Microsoft NDR type format strings describe types, alignment, pointers and
compound layouts. In the documented FC naming scheme, C denotes conformance,
V variance and P embedded pointers; `FC_PP` starts a pointer-description section.
These are decoder clues, not proof that an arbitrary matching byte is metadata.
[Type format strings](https://learn.microsoft.com/en-us/windows/win32/rpc/type-format-strings).

Procedure descriptors have header and parameter descriptions, with different
Oi/Oif/extended forms. Do not apply one fixed header length to every stub, or
treat a native stack offset as a wire offset. This source does not supply an
NDR64 decoder. Correlate referenced descriptors, calling convention and the
manager call; a format-string pointer alone does not identify the application
sink. Private runtime/stub structures require version-qualified interpretation.
For interpreter metadata distinctions and syntax-specific lookup, use
`reference-windows-rpc-dispatch-ndr-metadata`.
[Procedure formats](https://learn.microsoft.com/en-us/windows/win32/rpc/procedure-format-strings),
[private dispatch table](https://learn.microsoft.com/en-us/windows/win32/api/rpcdcep/ns-rpcdcep-rpc_dispatch_table).

## A 64-bit executable does not prove that a call used NDR64

Microsoft MIDL `/protocol dce`, `ndr64` and `all` select supported transfer
syntaxes. NDR64 is not backward-compatible with DCE NDR. An NDR64-only endpoint
and a DCE-only peer cannot communicate through that combination; the documented
failure is `RPC_S_UNSUPPORTED_TRANS_SYN`. A 64-bit `/protocol all` build can
support both, whereas 32-bit builds support DCE NDR.

Thus binary bitness or the presence of NDR64 metadata does not prove the selected
syntax for a particular call. Record offered and selected syntax separately;
decode with the appropriate rules. Native pointer width, native structure layout
and wire member layout are different coordinates. Do not copy a native struct
over captured wire bytes and call the result an established parse.
[MIDL protocol selection](https://learn.microsoft.com/en-us/windows/win32/midl/-protocol),
[transfer syntax](https://learn.microsoft.com/en-us/windows/win32/rpc/transfer-syntax-and-ndr64).
