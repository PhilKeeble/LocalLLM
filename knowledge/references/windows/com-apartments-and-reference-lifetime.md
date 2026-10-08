---
id: reference-windows-com-apartments-reference-lifetime
title: Windows COM apartments, pointer transfer and reference lifetime
kind: reference
topics: [windows, com, apartments, reentrancy, reference-counting, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows COM apartments, pointer transfer and reference lifetime

## An apartment defines call dispatch and interface-pointer use

In Windows COM, an apartment groups objects under a threading and call-dispatch
model. A single-threaded apartment (STA) dispatches its objects' calls on its one
thread; the multithreaded apartment (MTA) permits concurrent calls by its member
threads. These are not separate processes or memory-protection boundaries.
An interface pointer's valid use depends on its apartment/marshaling or agility
contract, not just whether its address is readable. The specific rules below
distinguish same-apartment sharing, reentry and cross-apartment transfer.
[COM apartments](https://learn.microsoft.com/en-us/windows/win32/com/processes--threads--and-apartments).

## CoInitializeEx succeeds with S_FALSE as well as S_OK

Scope: Windows COM, reviewed 2026-10-02. `CoInitializeEx` initializes the calling
thread and selects its concurrency model; it is not process-wide security
initialization. Repeated compatible initialization returns S_FALSE. Each successful
initialization, including S_FALSE, requires a matching `CoUninitialize`.
`RPC_E_CHANGED_MODE` is failure, not confirmation that the requested mode took
effect; it can involve incompatible prior initialization or an NTA transition.

Inference: a branch comparing only to S_OK can misclassify a successful repeat.
Track each thread and its balanced initialization lifetime, rather than using
one process-global initialized flag. A failure on one thread does not prove
COM is unavailable throughout the process. This section does not prescribe a
universal WinRT initialization sequence.
[CoInitializeEx](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coinitializeex).

## An STA serializes ordinary dispatch but permits reentrancy

Windows COM delivers an STA object's calls on its apartment thread using message
dispatch. The object can be reentered when a method pumps messages or makes an
outgoing cross-thread COM call. One thread therefore does not guarantee that a
method runs uninterrupted to completion. A callback can observe intermediate
state or release references before the outer call resumes.

For an investigation, identify the actual reentry point, nested method and state
invariant. A lock need not exclude a same-thread reentrant call. A blocking wait
is a deadlock candidate only when needed progress depends on dispatch that the
wait prevents; STA membership alone is not proof of a wait cycle. Preserve
message-pump and outgoing-call evidence. Do not infer an STA synchronization
context merely from an async function name or an STA annotation in source.
[Single-threaded apartments](https://learn.microsoft.com/en-us/windows/win32/com/single-threaded-apartments).

## MTA sharing removes a marshaling boundary, not synchronization duties

In Windows COM, free-threaded threads in a process share its MTA. Interface
pointers can be passed directly among those threads; calls on MTA objects can
execute concurrently, including calls to the same method. COM does not serialize
those calls for the application. This same-MTA rule does not permit arbitrary
raw pointer use from another apartment or process.

Investigation implication: record the apartments of both endpoints before calling
a transfer a violation. Then audit shared state and reference acquisition under
actual concurrency. Free-threaded does not mean logically race-free, and an
atomic AddRef does not make compound object state atomic. Callback objects and
contained interfaces can have different apartment requirements from the holder.
[Multithreaded apartments](https://learn.microsoft.com/en-us/windows/win32/com/multithreaded-apartments).

## Cross-apartment marshaling has a separate stream-consumption lifetime

Ordinary apartment-bound COM interface pointers require marshaling across
apartments. An established inter-thread path uses
`CoMarshalInterThreadInterfaceInStream` followed in the destination thread by
`CoGetInterfaceAndReleaseStream`. COM may perform marshaling automatically when
passing interface parameters through a proxy; a manually queued raw pointer
does not itself establish such a path. Check for supported agility before
assuming every cross-thread use needs this particular helper pair.
[STA transfer rules](https://learn.microsoft.com/en-us/windows/win32/com/single-threaded-apartments).

`CoGetInterfaceAndReleaseStream` releases its input stream even if unmarshaling
fails. The failure branch must not blindly retry or release that same consumed
reference again. This does not prove the underlying stream has no other owners;
track each reference separately. The helper also carries the untrusted-data
warning, so it is not a safe specimen-inspection shortcut.
[Stream helper contract](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cogetinterfaceandreleasestream).

## A global interface table cookie is process-local routing, not a raw pointer

Windows COM's Global Interface Table registers an interface and returns a cookie
used to retrieve an appropriate pointer from another apartment in the same
process. It is not a process- or machine-portable object reference. An agile
holder can still contain apartment-bound interfaces; its own agility does not
automatically make its members safe for direct use everywhere.

Inference: recover register/get/revoke paths and the apartment where the resulting
pointer is used. A numeric cookie is not an interface address or an authorization
token for another process. Revocation controls table registration; do not infer
destruction of all existing object references solely from the word revoke.
Use `reference-windows-com-activation-interface-evidence` for object identity
and inspect the actual reference ownership in the target.
[Cross-apartment access](https://learn.microsoft.com/en-us/windows/win32/com/accessing-interfaces-across-apartments),
[GIT revocation](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nf-objidl-iglobalinterfacetable-revokeinterfacefromglobal).

## Reference accounting follows ownership, not every pointer-sized copy

COM's default client rule is AddRef for a new independently retained interface
reference and Release when relinquished. Proven lifetime nesting or ownership
transfer can omit redundant pairs. A borrowed `[in]` pointer used only within
its containing call is different from a pointer retained for later work. Clients
must not assume all interfaces share one physical counter; AddRef/Release return
values are diagnostic, not reliable application ownership decisions.

For a queued callback, establish an acquired reference or other valid lifetime
guarantee before publication. For a synchronous helper, missing AddRef alone is
not proof of a defect if lifetime is contained. An outgoing call can release the
last external reference, so inspect protection of the outer method's continued
use. Smart-pointer copy, attach/detach and move operations require their actual
wrapper contracts; do not infer an extra reference from the type name alone.
[COM reference-count rules](https://learn.microsoft.com/en-us/windows/win32/com/rules-for-managing-reference-counts).
