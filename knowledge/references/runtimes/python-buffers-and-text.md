---
id: reference-python-buffers-text
title: CPython buffers, memoryviews, UTF-8 pointers and native output initialization
kind: reference
topics: [python, cpython, buffer-protocol, memoryview, unicode, utf8, lengths, initialization]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# CPython buffer and text boundary evidence

## Py_buffer acquisition: lifetime protection is not immutability
A successful PyObject_GetBuffer acquisition must be paired with PyBuffer_Release.
Normally view.obj holds an owned exporter reference released by that operation;
special temporary raw-buffer cases differ. Request flags determine the accepted
view; PyBUF_WRITABLE requires writable storage or failure. [1]

Keep the acquired view live until the last native user finishes. Do not separately
consume view.obj as if it were an unrelated owned result. Storage remaining
available is not proof that another alias cannot change its contents. For a
check-then-use finding, establish the actual mutation and synchronization path.

## Py_buffer len, strides and suboffsets: logical extent is not a flat span
Py_buffer.len is a byte count for the logical contents. For noncontiguous views
it is not permission to read buf[0..len). Strides are byte displacements and may
be negative or zero; suboffsets can require pointer indirection. Flat-span access
requires a contiguity-guaranteeing acquisition or equivalent verified layout. [1]

Do not turn an arbitrary multidimensional view into memcpy(buf, len) by ignoring
its shape. Recover request flags and exporter response before assigning a native
read/write range. Check count-to-byte arithmetic separately from layout support;
an in-range total size does not prove each addressed element is valid.

## PyArg string formats: borrowed pointer versus acquired buffer
In PyArg parsing, s# and y# return borrowed pointers plus lengths; s* and y*
acquire Py_buffer views needing release. The s forms also accept Unicode via
UTF-8 conversion; y forms are for bytes-like input. Length-bearing forms can
contain embedded NULs. Borrowed storage is not generally checked for immutability. [2]

Follow the selected format, not the decompiler's char* type. A pointer/length
pair is not necessarily a terminated string or a private copy. Trace lifetime
through callbacks, thread-state detachment and native retention. See
`reference-python-reference-ownership` for object ownership versus a borrow.

## Memoryviews over raw memory do not invent an owning exporter
PyMemoryView_FromMemory wraps a native address and byte size; the memoryview's
base is NULL for this constructor and for PyMemoryView_FromBuffer.
PyMemoryView_GET_BUFFER exposes the view's private Py_buffer copy and does not
check the object's type. [3]

Investigation inference: creating a Python wrapper around a native pointer does
not establish who owns that allocation or how long it survives. Identify the
external owner, invalidation and final consumer. Returning a view of expired
stack or freed heap storage is not made safe by keeping the memoryview alive.
Distinguish view-object lifetime from backing-storage lifetime.

## PyUnicode_AsUTF8AndSize: bytes, embedded NUL and borrowed lifetime
PyUnicode_AsUTF8AndSize returns the Unicode object's cached UTF-8 pointer and
byte length, with an extra trailing NUL outside that length. Embedded NUL code
points remain; surrogate code points cause conversion failure. The caller does
not free the pointer, which becomes invalid when the Unicode object is collected. [4]

A character count is not this encoded byte length. A C string consumer can stop
at an embedded NUL even when Python validated a longer value. Compare exactly
what the validator and native path/command/protocol consumer each use. Keeping
only the pointer, without the owner's lifetime, is insufficient for delayed work.

## PyBytes output: allocated length is not initialized length
PyBytes_FromStringAndSize(NULL, n) creates bytes with uninitialized contents.
PyBytes_AsString returns internal storage with an additional trailing NUL; callers
must not free it. Mutation is permitted only for the documented freshly created
uninitialized-object construction case, not arbitrary existing bytes objects. [5]

If native code writes fewer than n bytes, returning the full object can disclose
unwritten storage. Trace the actual output count, initialized range and publication
point on success and error paths. The trailing NUL does not initialize the payload
or exclude embedded NULs. A char* return type alone does not confer writable ownership.

## Primary sources and scope
Reviewed 2026-10-02 against Python 3.14.8 C API documentation. These rules cover
CPython buffer consumers; a particular exporter still has its own format,
mutation and lifetime requirements. Inferences above are investigation checks,
not observations of an executed target.

1. [Buffer protocol](https://docs.python.org/3/c-api/buffer.html): acquisition, ownership, request flags and noncontiguous layouts.
2. [Parsing arguments](https://docs.python.org/3/c-api/arg.html): pointer-length and acquired-buffer formats.
3. [Memoryview objects](https://docs.python.org/3/c-api/memoryview.html): raw-memory constructors and unchecked access.
4. [Unicode objects](https://docs.python.org/3/c-api/unicode.html): UTF-8 size, lifetime and embedded NULs.
5. [Bytes objects](https://docs.python.org/3/c-api/bytes.html): uninitialized construction and internal-buffer contracts.
