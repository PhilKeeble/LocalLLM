---
id: reference-wasm-linear-memory
title: WebAssembly linear-memory bounds, guest object bugs, growth and host view lifetime
kind: reference
topics: [webassembly, wasm, linear-memory, buffer-overflow, integer-overflow, memory-growth, lifetime]
platforms: [windows, linux, macos]
architectures: [wasm32, wasm64]
---
# WebAssembly linear memory and object boundaries

## A Wasm address is an offset in a selected memory, not a host pointer

Core memory is a byte array. Modules may have multiple memories; memory indices
identify them, while the memory's address type determines 32- or 64-bit addressing.
Ordinary loads/stores interpret numeric bytes little-endian. [1,2]

Record memory identity, byte offset and access width together. A file offset,
guest offset and native base-plus-offset pointer are different coordinates.
Do not assume every i32 value is a pointer or every memory operand selects memory
zero. Imported/shared storage also requires identifying who else can modify it.

## Linear-memory bounds do not enforce C/C++ allocation or object bounds

A core load/store traps if any accessed byte lies beyond the selected memory's
current extent. [1] That boundary is not the end of each guest allocation.
Emscripten illustrates detecting guest buffer overflows and use-after-free with
additional sanitizer instrumentation. [3]

Investigative consequence: a write into the next guest object can remain inside
linear memory. Recover object capacity, lifetime and aliases independently of
the engine bounds check. A lack of trap does not establish a valid source-level
access, and a guest-object violation alone does not establish a host escape.

## Guest shadow-stack data is not the engine's protected call stack

Wasmtime distinguishes compiler-managed shadow-stack storage in linear memory
from the runtime call stack holding return addresses and spills. The latter is
not directly addressable by guest memory operations. [4,5]

When reversing a stack-pointer-like global, identify which storage it manages.
A corrupted guest stack local can affect data or later dispatch without proving
that a native return address was overwritten. Conversely, protected runtime
return addresses do not protect guest-local buffers or application flags.

## i32.add wrap differs from a load/store immediate offset

Core i32.add and i64.add return addition modulo 2^32 and 2^64 respectively. [6]
For a memory instruction, combining its unsigned dynamic address with its
immediate offset uses a 33- or 65-bit effective address before bounds checking;
this combination is not the corresponding wrapping integer addition. [1]

Trace where arithmetic occurs. A wrapped count-times-stride or pointer addition
before the load may select the wrong in-bounds object. Do not report the load's
immediate-offset addition itself as wrapping at 32 bits. Wasm numeric semantics
also do not undo optimizations already performed under C/C++ source rules.

## Offset zero is not an automatic native-style null fault

Emscripten explains that offset zero is an ordinary location in Wasm memory;
its default null dereference behavior is not a native segmentation-fault rule. [3]
This does not make a C/C++ null dereference valid source code.

For a decoded zero value, distinguish null by the guest ABI from a permitted
core byte offset. Determine whether source/runtime instrumentation adds a check
and whether the executed access stays in memory. Do not infer successful error
handling merely because a failed allocation returned zero.

## memory.grow uses pages and reports failure differently from JavaScript

Core memory.grow takes a page count, returning the previous page count on success
or an all-ones integer (-1) on failure; growth can fail before a declared maximum
because of resource limits. Standard Wasm pages are 64 KiB (65,536 bytes); when
custom-page-size extensions are enabled, establish the selected memory's page
size before converting to bytes. Wasmtime documents this distinction. [4,7]
The JavaScript Memory.grow API instead throws RangeError when growth fails. [8]

Keep pages, bytes and result/error domains separate when following allocation
failure. A successful growth does not initialize an application's object metadata
or authorize a host operation. Do not substitute JavaScript exception behavior
for a guest instruction's returned sentinel.

## Native memory views can become invalid across growth or guest re-entry

Wasmtime documents that memory growth may relocate the base and invalidate raw
pointers or slices. Re-entering Wasm can change memory contents or grow it; passing
Store access elsewhere can permit the same invalidation. Safe read/write methods
avoid handing out such long-lived raw pointers. [4]

For a native binding, trace every callback between validation and use. Reacquiring
a base pointer solves neither stale validated content nor guest object lifetime.
Copy necessary input or establish the actual stability/synchronization guarantee;
a one-time bounds check is not an ownership or immutability guarantee.

## JavaScript fixed-length and resizable memory buffers differ on growth

The reviewed JavaScript interface refreshes an unshared fixed-length ArrayBuffer
by detaching it and replacing it after successful growth. For its resizable
ArrayBuffer mode, refresh instead updates backing data and byte length. [8]

Identify the actual buffer mode and engine support before diagnosing a stale view.
Do not apply the fixed-buffer detachment rule universally to resizable or shared
memory. Shared-memory backing/view behavior and concurrent mutation require the
target's threads/JavaScript contract; this unshared rule does not settle them.

## Primary sources and scope

Reviewed 2026-10-02: living core/JavaScript specs, Wasmtime API documentation and
Emscripten 6.0.11-git development documentation. Memory model facts do not prove a
particular compiler layout or embedding configuration. Workflow:
playbook-re-webassembly-boundary.

1. [Core memory instructions](https://webassembly.github.io/spec/core/syntax/instructions.html): addressing, effective address, endian and bounds.
2. [Core types](https://webassembly.github.io/spec/core/syntax/types.html): address and memory types.
3. [Emscripten sanitizer documentation](https://emscripten.org/docs/debugging/Sanitizers.html): guest buffer/lifetime bugs and null access.
4. [Wasmtime Memory API](https://docs.wasmtime.dev/api/wasmtime/struct.Memory.html): pages, shadow stack, safe access and pointer invalidation.
5. [Wasmtime security model](https://docs.wasmtime.dev/security.html): runtime stack isolation.
6. [Core numeric semantics](https://webassembly.github.io/spec/core/exec/numerics.html): modular integer addition.
7. [Core execution instructions](https://webassembly.github.io/spec/core/exec/instructions.html): memory.grow success and failure.
8. [WebAssembly JavaScript interface](https://webassembly.github.io/spec/js-api/index.html): memory growth, buffer refresh and resizable buffers.
