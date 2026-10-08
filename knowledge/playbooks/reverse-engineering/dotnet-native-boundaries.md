---
id: playbook-re-dotnet-native-boundaries
title: Reverse engineering .NET and native boundaries
kind: playbook
topics: [reverse-engineering, dotnet, pinvoke, marshalling, encoding, metadata]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Reverse engineering .NET and native boundaries

## Scope

Reviewed 2026-10-02. Use when managed data reaches P/Invoke, COM, unsafe code, a
native library, or a native callback. Read the managed declaration and native
prototype independently; matching names do not prove an ABI match.

For artifact identity, token scope, IL control flow and runtime dispatch, start
with playbook-re-dotnet-method-dispatch. Its factual homes are
reference-dotnet-metadata-il-evidence and reference-dotnet-loading-code-identity.
ReadyToRun, Native AOT and JIT-generated code do not share one address model.
Use reference-dotnet-interop-representations for conversion/layout facts and
reference-dotnet-unsafe-memory-lifetimes for pins, spans, pools and SafeHandle.

## Establish the active interop implementation

Identify runtime/SDK, architecture and declaring assembly. Separate a
runtime-marshalled DllImport from LibraryImport-generated code, custom marshallers,
disabled runtime marshalling and hand-written unmanaged function-pointer calls.
Read the generated/compiled adapter and its cleanup; attributes from another
assembly or another marshalling system are not proof of the active conversion.

Recover the actual module/export and any NativeLibrary resolver. Join managed
MVID/token/IL coordinates to the native module hash/RVA. A familiar DLL name is
not proof of the loaded artifact or an exploitable search path.

## Record the managed contract

Preserve assembly hash/MVID, type and method, metadata token, IL offset,
DllImport/LibraryImport attributes, entry point, calling convention,
CharSet/StringMarshalling, SetLastError, and each parameter's managed type and marshalling
attributes. For structures record `StructLayout`, sequential/explicit layout,
`Pack`, `Size`, field offsets, fixed buffers, unions, nested structs, Boolean and
enum underlying widths, and architecture-dependent fields such as `IntPtr`.

For arrays/strings record direction, ownership, null-termination, element type,
`SizeParamIndex`/`SizeConst`, and whether a count means elements, UTF-16 code
units, Unicode scalar values, encoded bytes, or capacity including a terminator.
Do not assume the marshaller validates a native length against a managed array.

## Compare the native contract

Recover the exact imported/exported symbol and native call site. Compare
calling convention, parameter order, pointer indirection, signedness, integer
width, structure size/alignment, character width, return/error convention, and
allocation/free ownership. On x64 Windows the platform ABI reduces calling-
convention differences but does not correct type/layout mistakes.

Trace counts through conversions and arithmetic before allocation and copy.
Make every narrowing conversion explicit. A value validated while wide can
change after cast; a multiplication can overflow before assignment to a wider
destination if its operands are narrow.

Compare managed storage, runtime-marshalled layout, generated surrogate and
native sizeof/offsetof separately. Include Boolean representation, inline-array
versus pointer fields, packing and nested offsets. Marshal.SizeOf is not a
measurement of every managed allocation or proof that a pinned struct is native-ready.

## Encoding and native message extents

For Windows UTF-16 APIs distinguish character/code-unit counts from encoded
byte counts. `WideCharToMultiByte` takes an input count in wide characters and
an output capacity in bytes; `MultiByteToWideChar` takes input bytes and output
wide characters. Where the API supports a zero-destination size query, distinguish
that required capacity from the later actual output count and terminator policy.

For serialized/native messages compare framing and field units on both sides.
Do not infer the native buffer size from the managed string length, or the
managed object graph from a native length field.
Account for embedded NUL, non-ASCII and supplementary characters when comparing
native consumed length with encoded byte count. For output, prove
initialized logical length independently of capacity or a rented array's Length.
These checks cover byte/native representations, not managed object deserialization.

## Trace lifetime through the last consumer

For each native pointer record backing allocation, extent, root, pin, borrower,
owner and release function. Follow asynchronous storage beyond submission;
fixed, a pin lease or a SafeHandle add-reference ending at return may be too
short for retained native use. Trace callback unregister/quiescence and actual
terminal completion, not merely a cancellation request.

For Unsafe.AsPointer or pointer/ref-created spans, establish real storage bounds
before relying on a span index check. For ArrayPool buffers locate Return and
all aliases/queued users. For raw SafeHandle extraction recover successful
acquisition and matching release on every path. KeepAlive does not exclude
explicit disposal, and a nonzero pointer does not establish ownership.

## Reconstruct failure and cleanup as separate branches

Apply the native success predicate, then capture the applicable error channel
before another transition can replace it. Separate HRESULT, errno/Win32 error,
managed exception and conversion failure. Inspect copy-back, partial allocation
and cleanup if native execution succeeds but conversion fails afterward.

For every resource identify allocator-compatible release and exactly one owner.
A wrapper's Dispose/finalizer is not proof of timely native completion or the
correct deallocator. Compare successful, rejected, cancelled and exceptional
paths using an ownership timeline. The finding must identify a mismatched
allocation/release or an invalid use interval, not just a suspicious API name.

## Static-to-runtime handoff

Map managed locations with assembly/MVID + metadata token + IL offset. Map
native locations with module hash + RVA. A P/Invoke transition should preserve
both coordinate sets and the actual resolved module/export. Metadata supplies
managed identity; runtime context can supply the selected method/code version,
managed values and native argument state. Obtain whichever evidence the question
requires using the available capabilities. A native instruction address does not
by itself identify the managed frame or survive later code replacement/unload.

## Verification

Separate facts established by the adapter's IL/instructions and API contract from
native values, active JIT mapping or library selection requiring runtime evidence.
If those observations are unavailable, keep the corresponding premise unresolved.
Treat decompiled C# and C-like native output as reconstructions. Confirm
security-relevant widths, offsets, and branches in IL/metadata or instructions.

Sufficiency check: can the evidence explain the exact converted bytes/extent,
active native artifact, lifetime interval, success predicate and release owner
for one boundary call? Counterevidence includes a checked generated adapter,
an independently owned copy, a full-operation lease or rejection before native
use. Report missing facts as hypotheses, not a P/Invoke vulnerability merely
because unsafe code or a conversion attribute exists.

For malware behavior recovery, follow the actual native target and arguments into
their effects, including retained callbacks and returned data. Interop enables
ordinary applications as well as malicious behavior; a P/Invoke declaration or
unsafe block alone establishes neither execution nor malicious intent.

## Sources and factual homes

- [.NET native interoperability best practices](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices)
- [Customize structure marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/customize-struct-marshalling)
- [Type marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/type-marshalling)
- [Platform Invoke](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke)
- [P/Invoke source generation](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke-source-generation)
- [Disabled runtime marshalling](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/disabled-marshalling)

Version-qualified API rules and reviewed source sections are kept in
reference-dotnet-interop-representations, reference-dotnet-unsafe-memory-lifetimes
and reference-dotnet-delegates-async-lifetimes. This workflow is an investigative
method, not a claim that a particular binary exhibited a defect.
