---
id: vulnerability-parser-embedded-nul-counted-terminated-mismatch
title: Embedded NUL and counted-versus-terminated string disagreement
kind: vulnerability
topics: [parsers, strings, nul, ffi, paths, authorization, truncation]
platforms: [cross-platform]
architectures: [any]
---

# Embedded NUL and counted-versus-terminated string disagreement

## Definition and violated invariant

An embedded-NUL semantic vulnerability occurs when one component treats a string as a counted sequence that can contain zero-valued code units while another treats the first zero code unit as the terminator, causing validation and use to select different text or objects. Every security check and consumer must agree on encoding, unit width, length, termination, and the exact path, identity, extension, host, field, or operation represented.

This is distinct from reading past a missing terminator. A buffer can be correctly bounded and terminated yet still carry two semantic interpretations. Some language bindings and APIs reject embedded NUL rather than truncate, so the actual conversion and native call contract must be recovered.

## Conditions that establish the issue

Recover the input grammar and decoded value, whether NUL can be represented, string storage and explicit length, encoding conversions, FFI marshaling, native API signature, termination scan, validator, resolver, and final selected object. Demonstrate both interpretations of attacker-controlled data and connect their difference to the security decision and resulting use.

For paths and names, establish actual namespace resolution rather than relying on displayed text. For multibyte or wide strings, distinguish a zero byte from a zero code unit and track lengths in bytes versus code units.

## Evidence that is not sufficient

A NUL byte, escaped `\u0000`, `c_str()` call, pointer-only API, counted string, FFI boundary, or differing printed value is not sufficient. The producer may reject NUL, the validator may operate on the terminated prefix, the native API may take an explicit length, or the changed suffix may not affect identity or authority.

Truncation alone does not imply memory corruption. Establish a separate invalid memory access for that claim.

## Investigation sequence

Record the raw bytes, decoded code points or code units, explicit count, first terminator position, conversion output, and exact argument form at each boundary. Compare the value checked for extension, prefix, identity, host, member, or permission with the value passed to resolution or use. Preserve escaped and hexadecimal forms so logs or user interfaces do not hide the terminator.

At binary level, distinguish pointer-plus-length calls from pointer-only calls and locate any `strlen`-like scan or marshaling stub. Follow the consumer's returned handle or resolved object to prove which prefix was selected.

## Constructed counted-to-C-path example

```cpp
std::string path(reinterpret_cast<const char *>(payload), payload_length);
if (!ends_with_counted(path.data(), path.size(), ".jpg"))
    reject();
FILE *file = fopen(path.c_str(), "rb");
```

For bytes representing `secret.db\0.jpg`, the counted C++ string ends with `.jpg`, while a conforming C string consumer observes `secret.db` because the first null character terminates the string. The finding requires that the input path can retain the embedded NUL, the suffix check authorizes access, `fopen` receives that same storage, and opening `secret.db` changes the permitted object. A binding that rejects embedded NUL before the call changes the conclusion.

## Constructed x86-64 boundary shape

```asm
; Illustrative System V AMD64 shape. r12 = data pointer, r13 = counted length.
mov     rdi, r12
mov     rsi, r13
lea     rdx, [.jpg]
call    ends_with_counted         ; check consumes pointer and explicit length
test    eax, eax
jz      .reject
mov     rdi, r12
lea     rsi, [mode_rb]
call    fopen                     ; use consumes a null-terminated path
```

The differing argument shapes identify a boundary to inspect; they do not prove that `r12` contains an embedded NUL or that the two functions disagree. Confirm helper semantics, storage termination, platform ABI, and the object returned by the native call.

## Primitive and impact limits

The direct primitive is validator-consumer disagreement about a string's value or selected object. Consequences can include extension or path-policy bypass, wrong-certificate or identity selection, host confusion, hidden fields, log/evidence ambiguity, or authorization of a different resource. Code execution requires the selected object or operation to provide an execution path.

## Related knowledge and primary sources

`reference-parser-escaping-nul-url-layers` and native string references define decoded-NUL and termination behavior. This profile keeps both required interpretations and the changed consumer object local.

Reviewed 2026-10-09 against [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259.html) for JSON escaped control characters, the ISO C draft [N1570 section 7.1.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf) for the null-terminated string definition, and POSIX [`fopen`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/fopen.html) and [pathname resolution](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html#tag_04_16) for the constructed C boundary. The length-aware suffix helper is constructed.
