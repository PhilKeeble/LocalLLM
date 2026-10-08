---
id: playbook-re-python-native-boundary
title: Investigate CPython native extensions and embedded interpreter boundaries
kind: playbook
topics: [reverse-engineering, python, cpython, vulnerability-analysis, malware-analysis, extensions]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# Python/native investigation workflow

## Identify the runtime and the native execution path
Record interpreter implementation, architecture, loaded extension identity and
available build/GIL evidence. Distinguish an embedded interpreter from a Python
process importing a native module. Do not assign CPython structures to another
implementation by language name alone.

Locate initialization, module execution slots, method tables, callbacks and native
dependencies. Read the artifact without importing unknown code. Determine which
script/import/call selects the native path; merely shipping an extension does
not prove it executes. Starting facts: `reference-python-extension-dispatch-arguments`.

## Repair the native signature before tracing Python arguments
Decode PyMethodDef flags or the exact vectorcall protocol. Recover self, positional
values, keywords and count flags before naming registers or stack slots. Follow
argument-format destinations and custom converters; identify borrowed objects,
acquired buffers and conversion-owned memory.

For each value entering a sensitive operation, retain original input, conversion,
native width/unit, success check and final consumer. Check error paths and omitted
optional arguments. A successful Python parse does not establish a native bounds
check, authorization decision or immutable representation.

## Audit object ownership and re-entrancy together
For each retained PyObject*, record the reference's origin, owner, steal rule,
release path and any container on which a borrow depends. Include callbacks,
__index__ conversions and DECREF-triggered finalizers as possible re-entry points.
Determine whether state can change before the next borrowed-pointer use.

Do not count pointer assignments as acquisitions or every decrement as immediate
deallocation. Follow the actual API's success/error ownership rule, especially
list and module insertion. Distinguish a demonstrated stale use from a harmless
borrow protected by a live owner. Facts: `reference-python-reference-ownership`.

## Trace buffer shape, bytes, lifetime and initialized output
Record acquisition flags, base pointer, byte length, element representation,
contiguity, mutability and owner. Keep a memoryview's lifetime distinct from raw
storage lifetime. Compare validation and native use of the same representation,
including UTF-8 expansion and embedded NULs.

For native output, identify exactly which returned bytes were written on each
path. For asynchronous use, find the final native completion before releasing
the view or owner. Neither a successful allocation nor a retained wrapper proves
initialized, contiguous, unchanged data. Facts: `reference-python-buffers-text`.

## Trace thread and interpreter lifetime around native work
Identify detached-thread intervals, callback reattachment and interpreter selection.
On free-threaded builds, inspect native shared state and borrowed acquisitions;
on GIL builds, still inspect re-entrancy and released-GIL intervals. Check whether
module state is really instance-specific or hidden in process-global caches.

During teardown, locate admission stop and completed callback/worker rundown before
destroying interpreter-owned objects. A state-query branch alone is not a lifetime
guarantee. Facts: `reference-python-interpreter-lifetime`.

## Malware analysis: connect script/configuration to native effects
Trace the actual script or configuration source, selected module/method, converted
arguments and OS/native effect. Include import-time execution and callbacks, not
only conspicuous method names. Preserve decoded bytes and unresolved dispatch
targets; distinguish a string extraction from use of that string.

Report capability present, statically feasible invocation and observed execution
separately. An embedded Python runtime or powerful extension is not malicious by
itself. Shared runtime code is not operator attribution. Use
`playbook-re-sensitive-data-flow` for cross-function path evidence.

## Finding boundary and sources
A vulnerability finding needs controlled input, reachable operation, violated
contract and supported consequence. A rejected conversion or Python exception
can be intended behavior. Record missing ownership, synchronization or reachability
evidence explicitly instead of promoting a suspicious pattern into a finding.

Reviewed 2026-10-02. This workflow applies the four CPython reference IDs above
and their official sources. It does not require execution of an untrusted
extension or assume that Python-level tests prove native memory safety.
