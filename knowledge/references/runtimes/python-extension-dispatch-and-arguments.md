---
id: reference-python-extension-dispatch-arguments
title: CPython extension discovery, native signatures, argument conversion and errors
kind: reference
topics: [python, cpython, extensions, abi, pymethoddef, vectorcall, arguments, exceptions]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv64]
---
# CPython native extension entry and conversion evidence

## PyInit and module execution: importing is an execution path
A CPython native extension is a compatible shared library, commonly .pyd on
Windows or .so on Linux. ASCII module names use a `PyInit_<name>` initialization
export. Multi-phase initialization returns a definition for subsequent creation
and execution; legacy single-phase initialization returns the module itself. [1]
Py_mod_exec slots execute module initialization code. [2]

Recover initialization as well as exported Python methods. Importing an unknown
extension merely to list its functions is not static inspection. A module name,
filename or init export is a discovery clue, not proof of the actual loaded file
or malicious behavior. Preserve loader selection and native image identity.

## Limited API, Stable ABI and object-layout limits
CPython's Limited API is a selected source interface; its Stable ABI supports
binary compatibility across applicable Python 3 versions. An abi3 filename is
not checked by the loader as proof of conformance. Macros and inlining outside
the Limited API can depend on version-specific internals. [3]

Identify the actual interpreter, architecture, build configuration and API usage
before assigning PyObject or container offsets. Lack of an imported API symbol
does not exclude an inlined operation. Stable ABI compatibility neither makes
extension code memory-safe nor promises identical behavior for every argument
across versions. These CPython contracts are not a universal Python VM layout.

## PyMethodDef flags select the native method signature
PyMethodDef associates ml_name, ml_meth, ml_flags and ml_doc. Decode ml_flags
before assigning arguments to ml_meth; its table pointer can be cast from a
different native function type. Common parameter roles are: [4]

| Calling flags | Native parameter roles |
| --- | --- |
| METH_VARARGS | self, positional tuple |
| METH_VARARGS with METH_KEYWORDS | self, positional tuple, keyword dictionary |
| METH_NOARGS | self, unused NULL argument |
| METH_O | self, single object |
| METH_FASTCALL | self, object-pointer array, positional count |
| METH_FASTCALL with METH_KEYWORDS | self, argument array, positional count, keyword-name tuple |

METH_METHOD additionally inserts the defining class after self in its supported
FASTCALL/KEYWORDS combination. Binding flags such as METH_CLASS also affect self.
Do not treat an argument array as a Python tuple or every method as two arguments.
The OS calling convention still determines where these parameters reside.

## Vectorcall nargsf contains flags, not only an argument count
CPython vectorcall takes callable, argument array, nargsf and kwnames. Positional
values precede keyword values; kwnames supplies the corresponding keyword names.
PyVectorcall_NARGS removes the PY_VECTORCALL_ARGUMENTS_OFFSET flag to obtain the
positional count. When that flag is set, the callee may temporarily use args[-1]
and must restore it. For PyObject_VectorcallMethod, the flag instead permits
temporary modification of args[0], again with restoration. [5]

Decode the exact calling API before diagnosing an apparent negative-index write
or enormous count. METH_FASTCALL's count is not automatically vectorcall's flagged
nargsf. Recover all forwarded values and keyword association when tracing an
authorization argument or a command selected by a wrapper.

## PyArg_Parse formats: destination types and optional values
PyArg_ParseTuple-style functions interpret a format string and output addresses.
For example, i targets C int, l targets C long, and n targets Py_ssize_t; O stores
a borrowed object pointer without conversion. The | marker leaves omitted optional
outputs untouched, so their defaults must already be initialized. [6]

Recover the actual format and every destination width. A correct Python-level
type does not prevent corruption from passing an incorrectly sized native output
slot. Check parse success before consuming outputs. Uninitialized optional state
can select a different native action even when all provided arguments are valid.

## PyArg O& converters can acquire resources and run cleanup
O& invokes a converter with the object and destination address. Returning
Py_CLEANUP_SUPPORTED allows a later parse failure to invoke that converter again
with a NULL object so it can release acquired resources. [6]

Follow the converter body rather than interpreting O& as a plain cast. Establish
which resources exist when subsequent arguments fail, and whether wrapper cleanup
duplicates or omits the converter's release. A converter can also invoke Python
behavior; previously checked mutable state may need reconsideration afterward.

## Python integers to C: range failure versus explicit masking
PyLong_AsLong can invoke __index__, raises OverflowError outside C long's range,
and returns -1 on failure; -1 is also a valid result, so inspect PyErr_Occurred.
PyLong_AsUnsignedLongMask instead reduces values modulo ULONG_MAX+1 and can still
fail during conversion. [7]

Do not infer a bounds check from a successful masking conversion. Track the
converted value into allocation, indexing or policy logic, with the target's
actual long width. A Python integer's range is not the range of the eventual
native operand. __index__ is also a possible re-entrancy edge, not just arithmetic.

## Python exception state and native success indicators
CPython error state belongs to the thread. Many pointer APIs signal failure with
NULL and integer APIs with -1; PyArg parsers instead use 0 for failure and 1 for
success. Most APIs do not clear an existing exception on success. Error propagation
must preserve the failure or explicitly handle and clear it. [8]

Audit the exact API, not one universal sentinel rule. A PyCFunction returns a new
reference on success and NULL with an exception on failure. [4] Follow cleanup
and the caller's decision after failure: clearing an error and continuing a
sensitive operation may create fail-open logic, not merely an exception-reporting
problem. NULL is not the Python None object.

## Primary sources and scope
Reviewed 2026-10-02 using official Python documentation identifying 3.14.8.
Version/build evidence matters for private layouts and available APIs, not as a
replacement for their enduring contracts. Investigative implications are derived
from the documented boundary rules; no target extension was imported.

1. [Defining extension modules](https://docs.python.org/3/c-api/extension-modules.html): shared-library discovery and initialization phases.
2. [Module objects](https://docs.python.org/3/c-api/module.html): execution slots.
3. [C API stability](https://docs.python.org/3/c-api/stable.html): Limited API, Stable ABI and filename caveats.
4. [Common object structures](https://docs.python.org/3/c-api/structures.html): PyMethodDef and native method conventions.
5. [Call protocol](https://docs.python.org/3/c-api/call.html): vectorcall parameters and argument-offset flag.
6. [Argument parsing](https://docs.python.org/3/c-api/arg.html): output types, optional arguments and converter cleanup.
7. [Integer objects](https://docs.python.org/3/c-api/long.html): checked and masking conversions.
8. [Exception handling](https://docs.python.org/3/c-api/exceptions.html): thread error state and propagation.
