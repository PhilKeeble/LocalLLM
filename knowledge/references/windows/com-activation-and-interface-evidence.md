---
id: reference-windows-com-activation-interface-evidence
title: Windows COM activation, interface identity and proxy discovery
kind: reference
topics: [windows, com, activation, interfaces, proxies, marshaling, idispatch]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows COM activation, interface identity and proxy discovery

## Scope and distinct identities

Scope: Windows Component Object Model (COM) contracts, reviewed 2026-10-02 against
the Microsoft sources linked below. Keep class identifier (CLSID), interface
identifier (IID), application AppID, proxy/stub CLSID,
object instance, interface pointer and process identity distinct. Equal class IDs
do not prove one object instance; equal IIDs do not prove one implementing class.
A byte sequence resembling a GUID is a discovery lead, not evidence of a live
registration or a successful activation.

Record activation arguments/results, registration or activation-context evidence,
loaded implementation and proxy modules, architecture, apartment and method.
Use `reference-windows-dll-plugin-resolution-activation` for loader context,
`reference-windows-com-apartments-reference-lifetime` for pointer use and
`reference-windows-com-rpc-authentication-impersonation` for authority.

## CoCreateInstance separates class selection from requested interface

Windows `CoCreateInstance` takes a class CLSID, optional controlling IUnknown for
aggregation, allowed class contexts and requested IID. On success its output is
the requested interface pointer, not necessarily the implementation's allocation
base. It combines class-object acquisition, instance creation and class-object
release. `E_NOINTERFACE` differs from class-registration failure;
`REGDB_E_CLASSNOTREG` can also mean the requested server kind is unavailable.

Inference: reconstruct the CLSID and IID operands separately. Do not rename an
entire implementation from the requested interface alone, or treat every failed
activation as evidence that no registration exists. Inspect the HRESULT before
following the output pointer. Factory-based construction can occur without a
nearby `CoCreateInstance` import.
[CoCreateInstance](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cocreateinstance).

## Local server is a process boundary; a context mask is not the result

In Windows COM, `CLSCTX_INPROC_SERVER` selects a DLL in the caller's process;
`CLSCTX_LOCAL_SERVER` describes a separate process on the same computer;
`CLSCTX_REMOTE_SERVER` describes another computer. Multiple context bits permit
alternatives. The mask alone does not establish which server was selected.
Record the effective activation configuration and observed module/process.

`CLSCTX_ENABLE_CLOAKING` uses a thread impersonation token for the activation
request when present; otherwise the process token is used. The flag is supported
from Windows Vista. This is activation-request identity, not a guarantee about
every later proxy call or the server's launch identity. Those need their own
security/configuration evidence. A same-machine call is not automatically
in-process or unprivileged.
[CLSCTX contracts](https://learn.microsoft.com/en-us/windows/win32/api/wtypesbase/ne-wtypesbase-clsctx).

## EXE class registration and DLL class factories have different entry points

Windows COM EXE servers publish class objects using `CoRegisterClassObject`;
DLL servers instead export `DllGetClassObject`. The registered object is the
class object, not every subsequently created instance. Record the CLSID,
class-object pointer, class-context and REGCLS flags, registration result and
revocation cookie. The same class object can have independent registrations.

`CoRegisterClassObject` takes a reference and `CoRevokeClassObject` releases the
registration's reference. Inference: class registration lifetime and individual
instance lifetime must be traced separately. An exported factory is not proof
it was loaded; an import of the registration API is not proof its call succeeded.
Follow factory dispatch into instance construction before assigning methods to
a particular class implementation.
[CoRegisterClassObject](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-coregisterclassobject).

## A COM vtable belongs to an interface, not a universal C++ object layout

COM interfaces expose method tables; objects can expose several interface
pointers and can be implemented without C++. An IID specifies an immutable
interface contract, not internal fields or a unique implementation class.
[Interface pointers](https://learn.microsoft.com/en-us/windows/win32/com/interface-pointers-and-interfaces).

All COM interfaces inherit IUnknown's three initial methods. Constructed layout
example: for an interface directly deriving from IUnknown, its first added method
is slot 3 (zero-based), at vtable byte offset 12 with four-byte pointers or 24
with eight-byte pointers. This is not an offset within the object's data, an RPC
opnum proof or a rule that every custom method follows only three slots: other
inherited methods count too. Bind IID and declaration order to the target ABI;
follow adjustment thunks and proxy targets rather than assuming the call target
is the ultimate server implementation.
[IUnknown inheritance](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iunknown).

## QueryInterface identity and authorization are different questions

For a COM object, querying its interfaces for IID_IUnknown yields the canonical
IUnknown pointer used for identity comparison. Other interface queries need not
return identical pointer values, even for the same IID. Interpret comparisons
within the relevant local COM context; raw addresses across processes or
apartments do not establish remote object identity. Successful QueryInterface
also adds a reference that the recipient must manage.

The supported interface set must remain static, and QueryInterface is not an
ACL authorization hook. COM can cache interface pointers; the server need not
receive every query. Therefore success does not authorize a later operation,
and an ACL check confined to QueryInterface is not adequate per-method access
control. Keep interface compatibility, object identity and resource policy
as separate observations.
[QueryInterface contract](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-queryinterface%28refiid_void%29).

## A proxy/stub class is not necessarily the application class

COM's default marshaling uses a client proxy and server stub to translate calls
and pass them to the real implementation through RPC. A client-side virtual
call may therefore target marshaling code rather than the business method.
`IMarshal` permits custom marshaling and does not require a custom implementation
to use RPC. Absence of a familiar NDR routine alone does not disprove COM use.
[IMarshal and proxy roles](https://learn.microsoft.com/en-us/windows/win32/api/objidl/nn-objidl-imarshal).

`CoGetPSClsid` retrieves a proxy/stub CLSID for an IID, including mappings supplied
by `CoRegisterPSClsid` in the current process. Do not equate that CLSID with the
activated object's CLSID, or treat a registry export as a complete runtime map.
Correlate IID, selected proxy module, stub and actual implementation. Loader and
activation-context differences remain relevant.
[CoGetPSClsid](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-cogetpsclsid).

## IDispatch member IDs are not vtable offsets

For Windows `IDispatch::Invoke`, the DISPID selects a member; `wFlags` distinguishes
method, property get, property put and reference assignment. Its `riid` must be
IID_NULL, not the object's custom IID. Recover the DISPID through the matching
name/type information or implementation, not as a byte displacement in a vtable.

Positional arguments in `DISPPARAMS.rgvarg` are reversed. Constructed three-argument
call f(a,b,c) with no named arguments stores c,b,a. Named arguments and property
puts also require their DISPID metadata; do not reverse an arbitrary mixed call
without interpreting it. `puArgErr` indexes rgvarg for TYPEMISMATCH/PARAMNOTFOUND,
not the original source-order list. Inspect HRESULT before interpreting it or
EXCEPINFO. Type coercion and locale can affect which values reach the method.
[IDispatch::Invoke](https://learn.microsoft.com/en-us/windows/win32/api/oaidl/nf-oaidl-idispatch-invoke).

## Interface unmarshaling can execute component code

Windows `CoUnmarshalInterface` is not a passive byte-to-structure parser. Its
documented custom-marshaling path reads a class identifier from the stream,
creates the corresponding component and invokes IMarshal unmarshaling. With
IID_NULL the requested interface comes from the stream. Microsoft explicitly
warns against using this API with untrusted data.

Investigation implication: trace stream provenance, selected unmarshaler and
activation policy before treating a serialized interface as ordinary data.
Do not call CoUnmarshalInterface on an unknown specimen merely to inspect it.
Static parsing or a separately authorized isolated environment is required for
that investigation. A bounds-valid stream does not establish trusted component
selection. MIDL user_marshal and COM IMarshal are different mechanisms; route
ordinary NDR parameter contracts to `reference-windows-ndr-marshaling-contracts`.
[CoUnmarshalInterface](https://learn.microsoft.com/en-us/windows/win32/api/combaseapi/nf-combaseapi-counmarshalinterface).
