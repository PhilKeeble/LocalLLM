---
id: reference-windows-ndr-marshaling-contracts
title: Windows MIDL NDR counts, pointer classes and marshaling checks
kind: reference
topics: [windows, rpc, midl, ndr, marshaling, bounds, pointers]
platforms: [windows]
architectures: [x86, x64, arm64]
---

# Windows MIDL NDR counts, pointer classes and marshaling checks

## Scope: wire validity is not application validity

Scope: Microsoft MIDL attributes and generated Network Data Representation (NDR)
contracts, reviewed
2026-10-02 against the linked Microsoft sources. The contract must be matched
to the actual compiled stub and selected transfer syntax. IDL found elsewhere
is a hypothesis until tied to the target build. A successfully unmarshaled
argument can still violate an application's capacity, ownership, authorization
or state-machine rule. Conversely, a malformed packet rejected before manager
dispatch is not evidence of an application memory corruption.

Use `reference-windows-rpc-interface-stub-evidence` for syntax and descriptor
recovery; `reference-windows-rpc-context-callback-lifetime` for retained state.
Constructed examples below illustrate arithmetic, not observed target defects.

## size_is counts allocated elements; length_is counts transmitted elements

For MIDL arrays, `size_is` specifies allocation in elements, not bytes;
`length_is` specifies how many elements are transmitted. These are different
quantities. `size_is(n)` corresponds to `max_is(n-1)`, not `max_is(n)`.
Recover element type, indirection level, direction and any first-element offset
before deriving buffer extents.

Constructed zero-offset example: capacity 8 of two-byte elements is 16 bytes of
element storage; transmitted length 3 describes 6 payload bytes. It does not
establish that all 16 bytes contain received data, or that the complete encoded
RPC message is only 6 bytes. Application copies using capacity instead of valid
length require separate initialization and destination-bound evidence.
[size_is](https://learn.microsoft.com/en-us/windows/win32/midl/size-is),
[length_is](https://learn.microsoft.com/en-us/windows/win32/midl/length-is).

## Array indirection and variance must retain their own coordinates

In MIDL, comma positions in `size_is` attach expressions to different pointer
levels: `size_is(,m)` describes a pointer to a sized array; `size_is(m,)` describes
a sized array of pointers. Flattening both into one contiguous byte buffer loses
the contract. `length_is = last_is - first_is + 1`; an offset and count are not
both absolute ending indices.

Constructed application-range check: for capacity C, first index F and count L,
require nonnegative values, F <= C and L <= C-F in a representation that does not
overflow. C=8,F=2,L=3 covers indices 2,3,4; F=7,L=2 exceeds that capacity even
though each value alone is <=8. Prove the stub's own correlation checks and the
manager's later arithmetic separately; this model is not an NDR wire decoder.
[size_is indirection](https://learn.microsoft.com/en-us/windows/win32/midl/size-is),
[length_is relation](https://learn.microsoft.com/en-us/windows/win32/midl/length-is).

## Counted character arrays are not implicitly terminated strings

MIDL `[string]` tells the stub to determine a string length using the language's
string convention. It cannot be combined with `length_is`, `first_is` or
`last_is`. A counted string instead uses a character array/pointer with explicit
counts, without `[string]`. C-style string storage needs space for a terminator.

Investigation implication: a received counted character array does not acquire
a trailing NUL merely because a decompiler calls it `char *`. Trace the exact
consumer: explicit-length processing and terminator scanning have different
requirements. Character elements, encoding code units and bytes must remain
separate, including any conversion or appended terminator. An IDL string rule
also does not validate a later application path, command or name policy.
[MIDL string contract](https://learn.microsoft.com/en-us/windows/win32/midl/string).

## ref and unique describe RPC pointer contracts, not C++ ownership

MIDL `[ref]` pointers are non-NULL and use existing client storage; the pointer
does not change during the call and does not represent aliasing. Unannotated
top-level pointer parameters default to `[ref]`, even with
`pointer_default(unique)`. Nested pointer attributes still require inspection.
[ref](https://learn.microsoft.com/en-us/windows/win32/midl/ref),
[unique defaults](https://learn.microsoft.com/en-us/windows/win32/midl/unique).

`[unique]` can be NULL and can change nullness across the call. NULL-to-non-NULL
can allocate client storage; non-NULL-to-non-NULL uses the existing referent's
storage under the documented rules. Changing to NULL can orphan memory unless
the client retains a way to free it. This attribute is not `std::unique_ptr`
ownership and does not mean automatically freed. Inspect generated and caller
cleanup. Do not treat a remote pointer contract as proof that every direct
native caller supplies valid pointers.
[unique behavior](https://learn.microsoft.com/en-us/windows/win32/midl/unique).

## Full pointers can carry aliasing and cycles

MIDL `[ptr]` full pointers can be NULL and represent aliases and cycles. A graph
containing only ref/unique edges is non-aliasing under those contracts, but a
ref/unique edge can lead to an object containing full-pointer edges. Therefore
seeing a unique outer pointer does not prove the entire reachable graph is a
tree. Mixed pointer classes require following the complete reachable layout.

Investigation implication: preserve referent identity when modeling manager
writes and cleanup. Two parameters that reach the same full-pointer referent
cannot be assumed independent allocations. A double-free candidate requires
actual ownership and release paths, not merely repeated pointer values; a
recursive traversal candidate requires feasible cycles and missing termination
or resource bounds. A client address is not a server-local address to dereference.
[MIDL full-pointer and mixed-graph rules](https://learn.microsoft.com/en-us/windows/win32/midl/ptr).

## robust correlation checks do not supply an application's own bounds

MIDL `/robust` adds metadata for NDR integrity checking, including correlations
between values repeated in the wire representation. Agreement between an array's
declared size parameter and its conformance information is not an application
quota, destination capacity or resource authorization. Follow accepted values
into later conversions, allocations and copies.
[robust](https://learn.microsoft.com/en-us/windows/win32/midl/-robust).

MIDL `[range(low,high)]` specifies inclusive bounds, but the attribute is ignored
without `/robust`; range checking for conformant-data array dimensions also
requires `/target NT60` or later. Recover actual generation/runtime evidence,
not just an IDL annotation. Constructed example: n=32 meets range 0..1024 but
does not fit a separate 16-element destination. Even an enforced range would
not justify that copy. This is a conditional mismatch, not a finding that all
robust stubs accept unsafe input.
[range requirements](https://learn.microsoft.com/en-us/windows/win32/midl/range).

## A union's selected arm must match the manager's interpretation

MIDL `switch_is` identifies the discriminant selecting a union member. For a
union parameter the discriminant is another parameter; for a union field it is
another field in the same structure. The discriminant need not precede the
union in declaration order. Recover its expression, type, case values and
default behavior rather than assuming the nearest preceding integer is the tag.

Investigation implication: compare the stub-selected arm with each manager read,
copy and cleanup path. Reinterpreting an accepted arm as another type, changing
the tag without rebuilding the value, or choosing cleanup from an unrelated tag
requires separate application evidence. Successful discriminant validation does
not prove correct downstream use. Conversely, a bad tag rejected in the stub
does not establish that the manager dereferenced the wrong arm.
[switch_is](https://learn.microsoft.com/en-us/windows/win32/midl/switch-is).

## User marshaling adds executable size, decode and cleanup paths

MIDL `user_marshal` associates a local type with a distinct wire type. Supplied
routines size, marshal, unmarshal and free the representation; embedded custom
types also need servicing. If the local user type is a full pointer, custom code
must manage aliasing. A local class layout is not necessarily its wire layout.
[user_marshal](https://learn.microsoft.com/en-us/windows/win32/midl/user-marshal).

Investigation implication: inspect all four routines, not only the final manager.
Compare calculated size against bytes consumed/emitted, alignment and integer
conversions; trace partial-decode failure cleanup and allocation provenance.
Generated outer framing does not prove that a custom inner decoder is safe.
Keep MIDL user/wire marshaling distinct from COM `IMarshal`; finding one is not
evidence that the other mechanism is present. This section describes review
targets, not a blanket assertion that custom marshaling bypasses all checks.

## NDR64 wire array counts are not native argument-stack offsets

MS-RPCE section 2.2.5 requires NDR64 PDUs to use data-representation label 0x10:
little-endian integers/floating-point byte order, IEEE floating point and the
specified ASCII character representation. This label does not convert every
application string to ASCII or every scalar to 64 bits. Match each declared type.
[NDR64 representation](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/b1af93c7-f988-4a1a-ac74-063179942f32).

For an NDR64 conformant-varying array, three unsigned 64-bit integers precede
elements: maximum count, first-element offset and actual count. Offset and actual
count remain present even when maximum count is zero. Constructed aligned byte-
array example (8,0,3) has 24 count bytes plus 3 element bytes; 27 is not the size
of the complete RPC message. Outer framing, other arguments and alignment remain
separate. Empty (0,0,0) still needs its 24 count bytes. Do not parse these using
native stack offsets from a MIDL procedure descriptor.
[MS-RPCE 2.2.5.3.2.3](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/0559c108-7705-448c-82a7-1c1a56e02650).

## An NDR64 embedded reference pointer includes an in-place marker

MS-RPCE 2.2.5.3.5.1 represents an NDR64 embedded reference pointer with a
nonzero eight-octet in-place value and a possibly deferred referent. NDR64 does
not use the DCE NDR special case for arrays of reference pointers: the in-place
value must still be transmitted. The marker is not a server-local address to
dereference. Referent deferral changes where data is consumed, not its ownership.

This rule concerns embedded reference pointers, not a universal claim that every
top-level parameter emits eight pointer bytes. Recover pointer class and nesting
before advancing a wire cursor; distinguish in-place markers from deferred
referents and native metadata pointers. A native pointer-size match alone does
not establish a valid parse. Reviewed 2026-10-02 against
[MS-RPCE embedded references](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rpce/620a5cbd-c53d-4dee-97a0-22b3538553e1).

## Server input storage is not automatically manager-owned heap memory

Microsoft's RPC server-stub model can reuse received buffer storage when layouts
permit, or allocate storage when conversion/layout requires it. An incoming
pointer therefore does not prove an allocation the manager may independently
free or reallocate. The force_allocate attribute changes allocation behavior;
recover the actual contract and cleanup path instead of guessing from an address.

For out-only reference pointers the stub initializes required referents,
recursing through reference pointers but stopping at unique/full-pointer edges.
That does not prove all application-produced output or descendants are valid.
Partial failures must leave a representation the actual cleanup can safely walk.
Direct COM calls may bypass MIDL stubs; do not transfer stub-initialization
assumptions to every native caller. Retaining per-call storage for queued work
needs separate lifetime evidence. These are allocation-model distinctions, not
a claim that every received graph is separately allocated or always zeroed.
[Server stub memory management](https://learn.microsoft.com/en-us/windows/win32/rpc/server-stub-memory-management).
