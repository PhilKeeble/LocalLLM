---
id: reference-wasm-host-capabilities
title: WebAssembly imports, WASI authority, component interfaces and native boundary validation
kind: reference
topics: [webassembly, wasm, wasi, component-model, host-capabilities, authorization, native-bindings]
platforms: [windows, linux, macos]
architectures: [wasm32, wasm64]
---
# WebAssembly host authority and interface evidence

## Core imports describe a link contract, not trusted implementation identity

A core import names a module/item pair and an external type; the embedder supplies
a matching definition. [1] Wasmtime's security model routes external interaction
through imports and exports rather than direct guest system calls. [2]

Recover the actual linker registration or JavaScript import object. A familiar
module/function name does not prove that the supplied implementation is standard,
benign or restricted. Trace any memory/table/global supplied by the host as well
as functions; shared state can carry input and authority without another call.

## A valid pointer-length pair is not authorization for the requested operation

For a host binding, separately establish memory identity, nonwrapping byte range,
encoding, lifetime and the policy for the requested resource. These are
investigation obligations, not additional guarantees conferred by core validation.

A range check can establish readable guest bytes while those bytes name an
unauthorized file, command or account. Conversely, a permitted resource name
does not make an unchecked native copy safe. Follow conversion into the exact
host API and identify the authority it uses. reference-wasm-linear-memory covers
growth/re-entry invalidation between the check and native use.

## WASI preopened directories grant specific host filesystem authority

In the reviewed Wasmtime WasiCtxBuilder, no preopened directories are supplied by
default. A preopen grants a host directory under a guest-visible name, with
enforced filesystem permissions. The guest name need not equal the host path;
the implementation prevents '..' traversal outside the granted directory. [3]

Recover configured preopens and permissions, not just path strings inside Wasm.
This contract is specific to that WASI implementation/configuration: custom
file-opening imports are not automatically confined by its preopens. A broad
grant may be intentional; a vulnerability claim needs the intended narrower
policy and a reachable operation that violates it.

## WIT describes component contracts, not application behavior

WIT defines interfaces and worlds for the Component Model; it is not executable
implementation code. Resource values distinguish owned handles from borrowed
handles. A borrow lends access for the call without transferring ownership;
dropping an owned resource releases that resource. [4]

Recover the concrete resource table and implementation behind a handle. Do not
treat a small integer handle as a native address or as proof of permission to
use another principal's resource. Type/ownership contracts and application-level
authorization remain separate questions.

## Canonical ABI adapters can explain extra copies and hidden pointers

The Component Model's Canonical ABI defines boundary representations across
source languages. In synchronous lowering, WIT parameters/results become flat
core values where permitted, otherwise linear-memory parameter/result storage
is used. [5] Lowering means mapping a higher-level interface to its core ABI.

Identify the component/interface and adapter before assigning a source-language
prototype to the core function. An internal C or Rust representation need not
match the boundary representation. Track which memory contains each transferred
value and who owns it; extra copies alone are neither obfuscation nor a bug.
Async interfaces have additional rules and must not be decoded as this synchronous
contract merely because some parameters resemble pointers.

## Malware capability requires a reachable host effect

For behavior recovery, map guest entry or start function to import, host wrapper,
resource/data source and external effect. Record unresolved bindings explicitly.
An encrypted data segment, large compute loop or file-related import is a lead,
not proof of exfiltration, mining or persistence.

Separate three conclusions: the package contains a capability; a feasible path
invokes it under stated host configuration; execution was actually observed.
Wasm confinement does not make intentionally granted host actions harmless, and
an engine dependency does not identify the payload's intent.

## Primary sources and scope

Reviewed 2026-10-02. Core rules and Component Model contracts are distinct;
WASI and embedding APIs must match the target rather than an assumed universal
host. Bytecode/native-cache trust: reference-wasm-runtime-trust-limits.

1. [Core imports](https://webassembly.github.io/spec/core/syntax/modules.html#imports): names and external types.
2. [Wasmtime security model](https://docs.wasmtime.dev/security.html): host interaction boundary.
3. [Wasmtime WasiCtxBuilder](https://docs.wasmtime.dev/api/wasmtime_wasi/struct.WasiCtxBuilder.html): preopened_dir and permission scope.
4. [Component Model WIT reference](https://component-model.bytecodealliance.org/design/wit.html): interfaces/worlds and resource ownership.
5. [Component Model Canonical ABI](https://component-model.bytecodealliance.org/advanced/canonical-abi.html): representation and synchronous lowering.
