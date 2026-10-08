---
id: playbook-re-rpc-wire-to-manager
title: Recover a Windows RPC call from registration through marshaling to manager use
kind: playbook
topics: [reverse-engineering, windows, rpc, midl, ndr, validation]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Recover a Windows RPC call from registration through marshaling to manager use

## Establish the interface and actual implementation

Scope: authorized analysis of Microsoft RPC binaries; reviewed 2026-10-02.
Record binary identity, architecture, OS/runtime and whether evidence is static
or observed. Follow registration calls to interface data, effective manager EPV,
flags and success paths. Correlate endpoint/binding, interface UUID/version and
procedure with the implementation. Endpoint annotations are leads, not identity.
Do not infer reachability from an import, UUID byte match or decompiler label.

Keep unknown manager selection explicit. Find other registrations or object/type
associations before concluding the generated default is used. Preserve original
addresses and evidence for renamed functions. Reference:
`reference-windows-rpc-interface-stub-evidence`;
[Microsoft registration contract](https://learn.microsoft.com/en-us/windows/win32/api/rpcdce/nf-rpcdce-rpcserverregisterifex).

## Recover a parameter contract, not just a C prototype

For the selected Windows RPC method, identify the supported and selected transfer
syntax. Match descriptor style and native ABI; do not decode NDR64 as ordinary
FC metadata merely because both are called NDR. Record each parameter's direction,
scalar width/signedness, pointer class, referent identity, array element type,
allocation count, transmitted count/offset, union discriminator and custom
marshaling. Distinguish wire coordinates from native stack/structure coordinates.

Trace correlation expression helpers and user marshal/unmarshal/free routines.
If IDL is reconstructed, label inferred attributes and unresolved fields instead
of presenting the output as original source. Minimum deliverable: a parameter
map with the evidence supporting each relationship, not only a generated header.
Use `reference-windows-ndr-marshaling-contracts`;
[MIDL stub descriptors](https://learn.microsoft.com/en-us/windows/win32/api/rpcndr/ns-rpcndr-midl_stub_desc).

## Resolve interpreter dispatch before renaming application methods

For Windows MIDL stubs, separate RPC_DISPATCH_TABLE's interpreter entries from
MIDL_SERVER_INFO's manager routine vector. Recover effective registration EPV,
method index and syntax-specific metadata. Repeated NdrServerCall2 addresses do
not collapse all methods into one. In a dual-syntax build, inspect the relevant
MIDL_SYNTAX_INFO entry rather than assuming a single descriptor representation.

Use target-width structures and mapped-address checks. Determine whether a table
entry is a byte offset or a native fragment pointer from the selected syntax and
matching interpreter/generated metadata, not a cast or guessed decompiler type.
Bound reads and classify unknown metadata explicitly. Keep native argument coordinates,
wire offsets and code addresses separate. Compare recovered correlation types
with native use before assigning signedness from an FC name alone. Deliver a
method/parameter map with supporting offsets and unresolved fields, not guessed
original IDL. Reference: `reference-windows-rpc-dispatch-ndr-metadata`.

## Follow accepted values past the unmarshaling boundary

For a suspected Windows RPC parser defect, locate the last stub check and first
manager use. Record whether the relevant check executes in the actual build.
Trace accepted counts through narrowing, multiplication, allocation, indexing,
copying and output-length production. Track valid data extent separately from
allocated capacity. For strings, determine counted versus terminated use; for
unions, compare selected arm with reads and cleanup.

A finding needs an accepted or otherwise reachable input, a violated operation
bound/invariant, and the resulting effect. Include the alternative that the stub
rejects the input or the manager checks a tighter limit. A range annotation alone
is neither proof of enforcement nor proof that application bounds are satisfied.
Retain instructions, values and rejection/acceptance evidence. See
`reference-windows-ndr-marshaling-contracts` and
[range prerequisites](https://learn.microsoft.com/en-us/windows/win32/midl/range).

## Separate client admission from operation authority

For Windows RPC authorization review, bind endpoint access, authentication,
interface security callback, effective caller identity and method/resource policy
to the same call path. Determine whether an admission decision is reused rather
than executed for every method. Follow checked return values of identity and
authorization operations; preserve the identity used at the privileged sink.
An admitted authenticated caller is not automatically allowed to operate on every
object named in an argument or context.

Do not test a privileged live endpoint by changing its security settings. Begin
with static evidence and existing authorized traces. Candidate confirmation needs
the actual caller's authority, reachable method and violated policy, not just the
absence of a familiar API name. Route identity facts to
`reference-windows-com-rpc-authentication-impersonation` and
`reference-windows-tokens-sids-groups-impersonation`.

## Enumerate close, rundown, callback and queued-work paths

For each Windows RPC context/resource, build a small ownership record: creator,
application references, explicit close, rundown and final release. Identify the
actual serialization mode and other contexts or workers sharing the state.
Classify callbacks as interface security callbacks, MIDL static callbacks, COM
objects or separate application calls before applying lifetime or reentry rules.

Distinguish strict interface association from type-strict context checking and
resource authorization. For mixed shared/exclusive contexts, prove the claimed
overlap. Record cancellation request, call completion and application cleanup
separately; a successful cancel request does not prove server rollback.

Check partial initialization, nested calls, delayed work and reconnect generation.
For a stale-pointer claim, retain allocation, release and later-use evidence for
the same object; for deadlock, retain a feasible wait cycle. Do not invent an
immediate rundown deadline or assume one context's serialization locks all state.
Use `reference-windows-rpc-context-callback-lifetime` and
`reference-concurrency-locks-waits-reentrancy`.

## Identify the boundary that accepted or rejected the request

Distinguish client-stub failure, transport/bind failure, server-stub rejection,
manager exception and application error result. Recover the relevant input,
branch and status at each boundary rather than collapsing all errors into a
failed RPC call. A constructed arithmetic model does not establish wire acceptance,
authentication or marshaling behavior in the target.

Static metadata/instruction evidence and existing traces can support different
parts of the argument. Separately authorized runtime observations need the actual
stub, syntax, caller policy and isolated conditions recorded; they are not a
prerequisite for reading this workflow or permission to alter a working service.

Retain build, method, syntax, caller, relevant values, exact failure boundary,
minimal input/trace and competing explanation. If no execution is available,
report static proof and unresolved reachability separately. This workflow is
based on the linked Microsoft contracts plus explicit investigative reasoning;
it is not an observed vulnerability case or an exhaustive RPC protocol decoder.
