---
id: abi-data-models-api-types
title: ILP32 LP64 LLP64, size_t, wchar_t, enums and Boolean API types
kind: reference
topics: [abi, data-model, integer-width, pointers, wchar, boolean, enums]
platforms: [windows, linux, macos, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Data models and API types

## ILP32, LP64 and LLP64 are not interchangeable

The model names describe these ordinary type widths, in bits: [1,2]

| Model | int | long | pointer |
|---|---:|---:|---:|
| ILP32 | 32 | 32 | 32 |
| LP64 | 32 | 64 | 64 |
| LLP64 | 32 | 32 | 64 |

64-bit Windows uses LLP64. Ordinary System V AMD64 LP64 uses 64-bit long and
pointers, but its x32 variant uses an ILP32 model on the 64-bit instruction set.
An ISA name or a 64-bit register does not establish the process data model.
Identify executable ABI, compiler target and interface declarations. [1,2]

Constructed investigation: a four-byte write to a Windows x64 `long` is not
automatically truncation. The same interpretation of an LP64 `long` may omit
half its storage. Conversely, storing a Windows x64 pointer in a 32-bit `long`
loses information unless a separately established encoding/range makes it valid.

## size_t, ptrdiff_t and API typedefs

C++ size_t is an implementation-defined unsigned type capable of representing
object sizes; ptrdiff_t is signed and represents array-subscript differences.
Do not equate either name with `unsigned long` or `long` across ABIs. [3]
Windows DWORD/ULONG are 32-bit; ULONG_PTR and SIZE_T are pointer-precision
unsigned types. A HANDLE is an opaque API value, not permission to dereference
it merely because its typedef is pointer-sized. [4]

Investigation: maintain a type-width table per interface, including 32/64-bit
compatibility boundaries. Check narrowing in API parameters as well as storage.
Do not change a recovered four-byte protocol length into size_t just because
the parser runs in a 64-bit process. A large allocation type does not widen an
earlier multiplication performed with narrower operands.

## wchar_t width is not a character count or wire encoding

MSVC's documented wchar_t is 16 bits, while GNU libc's wchar_t is 32 bits. [5,8]
The type name does not specify a wire format or guarantee that one element equals
one displayed character. A code unit is an encoding's storage unit; a Unicode
code point is a numeric position in the codespace, not necessarily an assigned
character. [6,9]

Investigation: recover whether each count measures bytes, code units, code
points or capacity including a terminator. In UTF-16, a supplementary code point
uses a surrogate pair; do not equate code-unit count with character count. [6]
At FFI and serialization boundaries, confirm both element width and encoding.
Use actual buffer bounds and conversion output lengths, not locale assumptions.

## MSVC long double does not imply extended precision

MSVC long double has double's representation; this is not a universal 64-bit ABI
rule. [5] Do not infer a wider operand, larger memory read or more precise
comparison from that type name alone. At a native-library boundary, recover the
actual storage and calling convention before treating a mismatch as application
corruption or substituting another platform's long double prototype.

## Windows BOOL, BOOLEAN and C++ bool have different representations

MSVC bool occupies one byte; Windows BOOL is an int and BOOLEAN is a BYTE.
These are distinct interface representations, not interchangeable typedefs. [4,5]
The language type bool has true/false values; an arbitrary raw byte copied into
its storage is not validated merely because a decompiler labels it Boolean.
For an API returning BOOL, consult that API's success/error contract before
assuming that comparison to exactly 1 tests all successful outcomes.

## C++ enum storage and valid operation codes are separate questions

C++ enums have an underlying integral type. Scoped enums default to int unless
another underlying type is specified; unfixed unscoped enums are implementation-
defined within language constraints. Values need not correspond to a named
enumerator. [7] Check storage width and the protocol's accepted value set
separately; a successful cast is not semantic validation of an operation code.

## Sources and verification scope

Reviewed 2026-10-02; documentation-derived type contracts. No target layout was
measured. Compiler switches, packing and nonstandard interfaces need separate
confirmation; do not extrapolate these baseline models to every architecture.

1. [Windows abstract data models](https://learn.microsoft.com/en-us/windows/win32/winprog64/abstract-data-models).
2. [AMD64 psABI low-level system information](https://gitlab.com/x86-psABIs/x86-64-ABI/-/blob/master/x86-64-ABI/low-level-sys-info.tex): data representation and ILP32.
3. [C++ size and difference types](https://eel.is/c++draft/support.types.layout).
4. [Windows API types](https://learn.microsoft.com/en-us/windows/win32/winprog/windows-data-types).
5. [MSVC data type ranges](https://learn.microsoft.com/en-us/cpp/cpp/data-type-ranges?view=msvc-170).
6. [Unicode FAQ, UTF-16](https://www.unicode.org/faq/utf_bom.html).
7. [C++ enumeration declarations](https://eel.is/c++draft/dcl.enum).
8. [GNU libc extended characters](https://www.gnu.org/software/libc/manual/html_node/Extended-Char-Intro.html).
9. [Unicode glossary](https://www.unicode.org/glossary/#code_point): code point and code unit definitions.
