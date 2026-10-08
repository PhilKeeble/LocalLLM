---
id: reference-dotnet-interop-representations
title: .NET PInvoke marshalling, layout, strings and native identity
kind: reference
topics: [dotnet, pinvoke, marshalling, layout, encoding, native-loading]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET interop representations

P/Invoke (platform invoke) is a managed-to-native call boundary. Marshalling
adapts values between the managed and native representations; identical-looking
type names do not establish identical bytes, parameter passing or ownership.
The adapter may be runtime-provided, generated or custom code, as scoped below.

## Scope and evidence coordinates

Reviewed 2026-10-02. Distinguish runtime-marshalled DllImport, source-generated
LibraryImport and explicitly disabled runtime marshalling. The managed signature
alone is not the native ABI. Record runtime/SDK version, architecture, declaring
assembly, attributes, generated/custom conversion code and actual native export.
These are .NET contracts, not general rules for every FFI implementation.
Workflow: playbook-re-dotnet-native-boundaries. Memory/handle lifetime facts:
reference-dotnet-unsafe-memory-lifetimes. Managed/native code identity:
reference-dotnet-loading-code-identity. FFI means foreign function interface;
the native ABI (application binary interface) includes calling and layout rules.

## LibraryImport is generated conversion code, not a DllImport synonym

The .NET 7 SDK introduced P/Invoke generation for static partial methods marked
LibraryImport. Conversion code can be examined as generated source/compiled IL.
LibraryImport uses StringMarshalling instead of DllImport.CharSet and
UnmanagedCallConv for convention selection; it has no ExactSpelling setting.
Its method/EntryPoint name must specify the intended export. Not every
MarshalAs setting supported by runtime interop is supported by the generator. [1]

Inference: inspect the emitted transition and cleanup, including custom
marshallers, rather than applying DllImport defaults to the declaration.
Finding a generated wrapper does not prove every conversion is bounds checked
or that the selected native export implements the assumed contract. Likewise,
do not infer that Native AOT categorically forbids every DllImport declaration;
its interop documentation explicitly covers P/Invoke bindings. [12] Establish
the actual build's supported interop path.

## Disabled runtime marshalling is assembly-scoped

DisableRuntimeMarshallingAttribute affects P/Invokes, delegate types and unmanaged
function-pointer calls in the attributed assembly. It does not change declarations
in other assemblies or disable built-in COM interop. For its raw runtime
transition, char is 16-bit regardless of CharSet; unmanaged value types without
Auto-layout fields use their direct layout, and customized field marshalling is
ignored. Other managed types are unsupported. SetLastError=true and ref/in/out
parameters are among features disabled on that raw path. [2]
Here bool is one byte, without runtime normalization. [3]

Inference: inspect generated/manual adapters separately: they can convert
managed arguments before reaching a raw transition. An assembly-level attribute
does not mean a LibraryImport wrapper cannot marshal a string or preserve an
error through its own code. A declaration in a different assembly must be
evaluated under that assembly's rules.

## Runtime-marshalled Boolean fields have explicit native representations

With runtime marshalling enabled, a bool field defaults to a four-byte Win32
BOOL representation. MarshalAs(U1) or I1 requests a one-byte Boolean field;
VariantBool requests the two-byte Windows VARIANT_BOOL representation, whose
true value is -1. These are field-marshalling contracts, not a universal C/C++
bool size or a statement about managed sizeof(bool). [4]

Inference: recover both native width and true/false convention. A struct that
looks right with small values can still have wrong following-field offsets.
The disabled-runtime-marshalling path has different rules; a field annotation
alone is not evidence that a generated/custom converter honors it.

## Marshal.SizeOf measures a representation, not all object storage

Marshal.SizeOf<T>() reports the unmanaged representation's size for supported
sequential/explicit layouts. Managed and unmanaged sizes can differ, including
character representation differences. [5] It does not report a managed object's
full allocation including object headers or prove that pinning yields those
marshalled bytes.

Inference: distinguish managed sizeof/Unsafe.SizeOf, Marshal.SizeOf/OffsetOf,
generated native surrogate layout and native compiler sizeof/offsetof. Compare
the representation actually passed. A C# unmanaged constraint does not by
itself establish identical runtime-marshalled layout: Boolean conversion is a
counterexample. A correct total size also does not prove correct field offsets.

## Pack controls alignment, not pointer width or byte order

For sequential layout, StructLayout.Pack limits alignment and can change padding;
zero selects the platform default, not one-byte packing. For primitive fields,
alignment is limited by field size and effective type packing. [6]
Constructed example: byte a, byte b, int c has offsets 0,1,4 and size 8 with
four-byte packing; with Pack=2 it has offsets 0,1,2 and size 6.

Inference: compare each offset and nested layout against the exact native build.
Pack does not turn an IntPtr into a fixed-width wire field or perform endian
conversion. Explicit union offsets and platform ABI aggregate passing must be
checked separately; neither follows from the presence of Sequential alone.

## Inline array fields and pointers are different layouts

For runtime field marshalling, ByValArray with SizeConst describes an inline
array of that many elements. An ordinary marshalled array field instead uses a
pointer representation; SAFEARRAY is another distinct contract. A managed array
reference with ByValArray does not itself become inline managed storage.
Built-in structure marshalling does not supply a C99 flexible-array-member
layout for a variable-length array field. [4]

Inference: recover whether the native callee expects a pointer, fixed inline
extent or a separately calculated trailing allocation. Count additional payload
bytes independently of the fixed header. Do not pin a nonblittable managed
structure and treat the resulting address as its converted native counterpart.

## SizeParamIndex describes a count source, not native memory protection

MarshalAs.SizeParamIndex identifies a zero-based parameter containing an array
element count for C-style array marshalling. Where LPArray uses both it and
SizeConst, the indicated count and constant contribute to the total. This
attribute does not affect managed calls to COM objects. [7]

Inference: a count annotation is not proof that the native callee cannot exceed
the supplied allocation. Recover the marshalling direction and actual stub,
then compare managed extent, converted native capacity and callee accesses.
Separate element counts from bytes and check multiplication/narrowing before
copy-back as well as before the call. Whether a particular stub rejects a bad
input count must be established, not inferred from the attribute name.

## DllImport CharSet depends on platform and runtime generation

With applicable runtime marshalling, DllImport CharSet.Ansi uses the Windows
system ANSI code page on Windows but UTF-8 on Unix. Unicode uses UTF-16 on both,
not the host C wchar_t representation everywhere. Auto uses UTF-16 on Windows;
on Unix .NET Core 2.2 and earlier uses UTF-16, while .NET Core 3.0+ uses UTF-8.
The documentation also specifies UTF-8 for Mono on Unix. [8]

Inference: the same managed declaration can produce different native bytes.
Record explicit MarshalAs overrides, module defaults and converter behavior.
Do not apply this DllImport table to LibraryImport.StringMarshalling or to
disabled runtime marshalling. A native char pointer alone specifies neither
encoding nor terminator policy.

## String.Length is not a native byte count or termination contract

String.Length counts Char units, not Unicode scalar values or encoded bytes;
embedded NUL characters are included in that length. [9]
Constructed example: A followed by U+1F600 has three UTF-16 code units but five
UTF-8 bytes, before any terminator. A managed string containing A, NUL, B has
Length 3, even if a native NUL-terminated consumer sees only A.

Inference: trace encoded size, terminator capacity and explicit native count
independently. A managed full-string authorization check and native prefix use
can disagree; that is a hypothesis requiring the actual consumer contract.
Use reference-native-text-encoding-size-units for shared size-unit rules.

## SetLastError captures an error channel, not a success predicate

With runtime-marshalled DllImport and SetLastError=true, the runtime caches the
native error. On .NET 6+ GetLastPInvokeError reads that cached channel;
GetLastWin32Error is available for older .NET/Framework. Modern .NET clears the
native error before the configured call; .NET Framework does not, so older
error state can persist. [10]

Inference: first apply the native API's return-value rule and conditions for a
meaningful error. A zero cached error does not independently prove success.
Capture it before another error-capturing transition; keep HRESULT, native
return value, errno/Win32 error and managed exception separate. Disabled runtime
marshalling or generated/custom wrappers require examining their own error code.

## An import name does not identify the loaded native artifact

Modern .NET native loading can try platform-specific library name variants;
absolute paths do not receive those variants. NativeLibrary.SetDllImportResolver
can provide an assembly's custom mapping and return a different library handle;
returning zero delegates to default resolution. [11]

Inference: a DllImport string or source-level method name is only a resolution
input. Preserve the actual loaded module path/hash, export address and
assembly-specific resolver, then join native coordinates to the managed call.
This mechanism is not proof of attacker-controlled loading: establish who can
influence the resolver/search location and whether that candidate was selected.

## Native AOT direct imports use a different resolution path

Native AOT normally binds P/Invokes lazily at runtime. DirectPInvoke build items
can select direct imports; for dynamically linked direct calls, the OS loader
resolves required libraries/entry points at startup. Missing dependencies can
prevent process startup. These direct imports do not honor
DefaultDllImportSearchPathsAttribute; OS loader rules apply. Native AOT also
supports static native linking through its build configuration. [12]

Inference: distinguish runtime resolution, loader-bound imports and statically
linked code. A managed resolver/search attribute cannot be assumed to control
an OS-resolved direct import, and an absent dynamic dependency may instead be
linked into the image. Record publish settings and native import evidence;
do not transplant JIT deployment's loading trace onto an AOT artifact.


## Sources: interop mode and representation

1. [P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation): generation and differences from DllImport.
2. [Disabled runtime marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/disabled-marshalling): assembly scope, raw signatures and unsupported features.
3. [Native interop best practices](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices): disabled-marshalling bool width and normalization.
4. [Customizing structure marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/customize-struct-marshalling): Boolean fields, inline arrays and flexible-array limit; not source-generated field conversion.

## Sources: sizes, strings and resolution

5. [Marshal.SizeOf](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.sizeof?view=net-10.0): unmanaged versus managed representation.
6. [StructLayout.Pack](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.structlayoutattribute.pack?view=net-10.0): alignment and padding.
7. [MarshalAs.SizeParamIndex](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshalasattribute.sizeparamindex?view=net-10.0): parameter index and LPArray counts.
8. [Charsets and marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/charset): version/platform-qualified DllImport table.
9. [String.Length](https://learn.microsoft.com/en-us/dotnet/api/system.string.length?view=net-10.0): Char units and embedded NUL.

## Sources: native error and loading

10. [DllImport.SetLastError](https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.dllimportattribute.setlasterror?view=net-10.0): caching and Framework distinction.
11. [Native library loading](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/native-library-loading): name variants and per-assembly resolver.
12. [Native AOT interop](https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/interop): lazy/direct binding, search attribute exception and static linking.
