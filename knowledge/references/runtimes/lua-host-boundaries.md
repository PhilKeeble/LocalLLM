---
id: reference-lua-host-boundaries
title: Lua C callbacks, value-stack recovery, userdata ownership and loader boundaries
kind: reference
topics: [lua, embedded-scripting, callbacks, userdata, ownership, bytecode]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# Lua host-boundary evidence

## lua_CFunction returns a result count, not the script's integer result

A Lua-callable C function has the signature int function(lua_State *L). It reads
arguments from Lua's value stack, pushes result values and returns their count.
Registration wraps a C function pointer as a Lua function value. [1]

Do not label a callback's return 1 as a Boolean success result without inspecting
the pushed value. Recover argument indexes and stack changes separately from the
machine call stack. Follow the registered script name to its native wrapper and
then the actual native operation; registration establishes availability, not that
a particular script invoked it.

## C closures carry upvalues; a registry index is not a memory offset

lua_pushcclosure attaches upvalues (captured Lua values) to a native callback. [2]
The registry is a shared table for C-side state, addressed through the
LUA_REGISTRYINDEX pseudo-index rather than a normal stack slot. [3]

Recover captured service objects, configuration and callback context as inputs,
not just explicit script arguments. A large negative constant used as a registry
index is not necessarily an underflow. Conversely, a registry entry shared by
multiple bindings can connect otherwise separate call paths; identify its writer
and lifetime before treating it as immutable per-request state.

## lua_tolstring and lua_tointegerx conversions need their full result contract

Lua 5.4 strings can contain NUL bytes. lua_tolstring supplies a byte length;
lua_tointegerx reports conversion success separately, returning zero on failure. [2]

Track whether the native consumer uses the explicit length or strlen. A prefix
checked by one component and a longer byte sequence used by another can invalidate
validation. For numeric input, distinguish failed conversion from a valid zero;
then check sign, narrowing and multiplication in the destination C type. A
successful conversion is not a bounds or permission check.

## lua_gettable can invoke script; lua_rawget bypasses metamethods

lua_gettable may invoke an indexing metamethod (custom behavior attached to a
value); lua_rawget performs table access without that mechanism. [2]

A native wrapper reading a script-controlled table is not necessarily performing
an inert memory lookup. Inspect possible re-entry between an earlier validation
and the eventual use of native state. Raw access removes this particular callback
edge, not every error path or security-policy requirement in the wrapper.

## Full userdata, light userdata and reference keys own different things

Lua manages full-userdata storage; light userdata is a pointer value, not managed
pointee storage. luaL_ref stores a value in a table and returns an integer key;
luaL_unref releases that entry and permits key reuse. [2]

Separate wrapper lifetime from the lifetime of a native object addressed by the
wrapper. Audit close/finalize paths for duplicate release and access after close.
A queued callback retaining only a released reference key may later identify a
different value. Trace the table, reference generation and cancellation ordering;
an integer key alone is not durable object identity.

## Protected calls contain errors, not arbitrary native cleanup

Lua's C interface supports protected execution through lua_pcall. Lua errors can
leave native code through a non-local transfer rather than the next statement. [4]
The language-author's native-binding example explicitly identifies allocation
errors bypassing a later resource close. [1]

Review cleanup on the exceptional edge, not only normal returns. Establish the
target's C/C++ error mechanism before assuming destructors run. Protected execution
does not roll back native writes or grant ownership of earlier temporaries. When
reconstructing failure handling, distinguish an error status from the Lua values
left for the caller.

## _ENV and text-only loading do not by themselves prove a sandbox

In Lua 5.4, _ENV controls free-name lookup. load defaults to accepting text and
binary chunks; mode "t" accepts text only. A binary function's first upvalue need
not be _ENV. Bytecode consistency is not fully checked; malicious bytecode can
crash the interpreter when run. [2]

Recover the actual load mode and where input bytes originate. A renamed global
table does not establish that reachable native callbacks lack filesystem,
process or network authority. Check capabilities returned by callbacks and
captured in closures as well as visible global names. A bytecode header check
does not establish safe execution or trusted provenance.

## Primary sources and scope

Reviewed 2026-10-02. Lua 5.4 contracts are explicitly named; LuaJIT, older Lua and
custom builds must not inherit undocumented layout or numeric-width assumptions.
The author's online first-edition explanations concern Lua 5.0; only the enduring
callback, registry and error concepts used here were cross-checked with 5.4.
General investigation: `playbook-re-embedded-script-boundary`.

1. [Programming in Lua: C Functions](https://www.lua.org/pil/26.1.html): callback protocol and exceptional resource cleanup, first edition (2003-2004).
2. [Lua 5.4 Reference Manual](https://www.lua.org/manual/5.4/manual.html): C closures, conversion APIs, userdata/reference APIs, environments and load.
3. [Programming in Lua: The Registry](https://www.lua.org/pil/27.3.1.html): pseudo-index and shared registry, first edition.
4. [Programming in Lua: Error Handling in Application Code](https://www.lua.org/pil/24.3.1.html): protected execution and non-local error transfer, first edition.
