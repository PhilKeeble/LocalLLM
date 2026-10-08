---
id: playbook-re-com-activation-authority
title: Recover COM activation, interface dispatch and effective caller authority
kind: playbook
topics: [reverse-engineering, windows, com, activation, authorization, lifetime]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Recover COM activation, interface dispatch and effective caller authority

## Build a class-interface-implementation map without activating the specimen

Scope: authorized Windows COM reverse engineering; reviewed 2026-10-02. Begin
with static call sites, GUID cross-references, factory exports/registrations,
matching IDL/type information and known module mappings. Separate CLSID, IID,
AppID and proxy/stub CLSID. Record class-context flags, aggregation input,
HRESULT path, returned interface and subsequent calls. Follow factories and
QueryInterface instead of searching only for CoCreateInstance.

Do not register DLLs, start a class server or unmarshal unknown interface streams
merely to enumerate metadata. These operations can execute component code.
Use existing authorized traces or separately approved isolated execution when
execution is necessary. Reference `reference-windows-com-activation-interface-evidence`;
[CoUnmarshalInterface trust requirement](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-counmarshalinterface).

## Resolve the call at the correct interface and apartment

For a COM virtual call, bind the pointer's interface contract to its vtable slot
and ABI; identify inherited methods, adjustment thunks and proxy/stub boundaries.
Do not treat a proxy routine as the final application method. For IDispatch,
recover DISPID, flags, VARIANT types, named/positional arguments and result/error
handling separately. Preserve uncertain type information as hypotheses.

Record caller and object apartments. Locate marshaling, GIT or agility evidence
for transfers; same-process is not the same as same-apartment. Identify STA
reentry and MTA concurrent access before reasoning about state isolation. A
reference-counted pointer proves neither thread safety nor method authorization.
Use `reference-windows-com-apartments-reference-lifetime` and
`reference-windows-com-activation-interface-evidence`.

## Recover effective security as a timeline rather than one configuration value

For COM/DCOM, record explicit or implicit process-security initialization and
its result; decode pSecDesc using capability flags. Then separate launch/access
policy, machine restrictions, activation authentication, exact proxy blanket,
caller impersonation and resource checks. Include client/server updates where
DCOM activation hardening is relevant. A registry value or low constant alone
does not prove effective policy.

Track shared proxy aliases, private copies, subsequent QueryInterface and static
or dynamic cloaking. At each downstream call, identify the projected identity
and compare it with the identity checked for the requested resource. Do not
assume a broker's thread token automatically becomes its outgoing proxy identity.
Use `reference-windows-com-rpc-authentication-impersonation`;
[COM cloaking](https://learn.microsoft.com/en-us/windows/win32/com/cloaking).

## Prove an ownership or authority mismatch across the actual path

For COM lifetime review, classify borrowed, independently retained and transferred
references. Account for successful QueryInterface, stream consumption on failure,
queued work, callbacks and final Release. Inspect wrapper operations rather than
counting raw pointer assignments. For a reentrancy candidate, identify what the
nested call changes before the outer call resumes.

For authorization review, retain the principal, permitted operation, actual
resource and sink context. Distinguish new impersonation failure from automatic
call-end restoration and asynchronous completion signaling. Candidate defects
need a feasible mismatch and consequence; a missing familiar API name, separate
interface pointer or repeated AddRef is not sufficient. Generic resource and
concurrency evidence remains in the existing native/concurrency references.

## Distinguish activation, marshaling and application outcomes

Locate success or failure at activation, interface acquisition, marshaling, proxy
admission, method dispatch or application validation. Preserve architecture,
registration, apartment, updates and caller policy with the evidence. An observed
call under an administrator's token does not establish access by a less-privileged
caller. A statically supported path is not an observed execution; neither requires
inventing a successful activation when the effective configuration is unknown.

For malware analysis, follow the selected component and method's actual arguments,
objects, results and downstream effects. A familiar CLSID or legitimate component
does not establish benign use, and COM activation alone does not establish malicious
intent. Successful interface acquisition is not proof a later operation executed.

Retain exact call operands/results, implementation mapping, ownership transitions,
policy evidence and a competing explanation. Arithmetic models of vtable offsets
or argument reversal do not execute COM, prove wire acceptance or validate
security policy. If only static evidence exists, state the unresolved runtime
conditions. Route NDR details to `playbook-re-rpc-wire-to-manager`; this workflow
is an investigative synthesis, not an observed target vulnerability.
