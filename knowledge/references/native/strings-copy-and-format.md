---
id: reference-native-strings-copy-format
title: C strings, copy overlap, NUL termination, snprintf lengths and format arguments
kind: reference
topics: [strings, null-termination, overlap, truncation, snprintf, format-strings, varargs]
platforms: [windows, linux, macos, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# String, copy and formatting contracts

## Counted byte sequences are not necessarily C strings

A counted range can contain embedded NUL bytes and need not end in NUL. A
C-string consumer instead needs a reachable terminator within valid storage.
Trace each conversion between the two representations; an accepted byte count
does not authorize an unbounded scan. A substring/view may end before the
underlying string's terminator. [1]

Constructed differential: validation examines all 12 bytes of a name containing
NUL, while a later C-string API sees only its prefix. This is a candidate object-
selection disagreement, not automatically memory corruption. Establish what
the validator accepted and which exact name the consumer uses. For encoded
strings, preserve bytes/code units separately; see `abi-data-models-api-types`.
Decoded JSON NUL and interop rejection-versus-truncation are covered in
`reference-parser-escaping-nul-url-layers`.

## memcpy and memmove: overlap is separate from bounds

memcpy copies a byte count and requires nonoverlapping source and destination;
memmove permits overlap. Neither interface knows the available sizes from the
pointers alone. Both source readability and destination writability must cover
the full count. [2,3]

Constructed investigation: shifting bytes right inside one buffer creates an
overlap even when both ranges fit. A memcpy implementation that happened to
produce the desired bytes in one run does not establish its contractual safety.
Conversely, changing to memmove addresses overlap, not an oversized count or
stale pointer. In a binary, identify the resolved implementation or inlined
copy sequence as well as the library-level contract.

## strncpy is fixed-width padding, not guaranteed termination

With valid buffers, strncpy writes n destination bytes, padding with NULs when
the source string ends earlier. If the source has no NUL among the first n bytes,
the n-byte result need not be NUL-terminated. It is not a universal safe-string
replacement. [4]

Constructed example: copying the eight bytes `abcdefgh` with n=8 produces no
terminator in an eight-byte destination. A later strlen can scan beyond it;
an eight-byte counted consumer may be correct. Prove the later consumer rather
than labeling all unterminated fixed-width records vulnerable. An added
`dst[n-1]=0` needs n>0 and sacrifices one payload byte; test whether truncation
changes an identifier, path or authorization decision.

## snprintf return value is not the stored byte count

For C99-style snprintf, including documented current GNU libc behavior, a
nonnegative return r is the length that would have been produced excluding NUL.
With valid capacity n>0, truncation is indicated by `r >= n`; n=0 writes no bytes.
Negative results are errors and must be handled before conversion to an unsigned
size. Do not use r as the readable length of a truncated output buffer. [5]

Constructed example: capacity 8 and return 12 means the buffer does not contain
12 output bytes. Passing 12 to a sender can disclose adjacent bytes. Check the
actual success/error path, initialized extent and transmitting operation. A
bounded formatting call prevents neither this later overread nor semantic
damage from a truncated filename or policy string.

## Windows snprintf versus _snprintf

Starting with the VS2015 UCRT, snprintf follows C99 behavior. Microsoft
_snprintf differs: truncation can return -1 and leave output unterminated.
The exact-fit legacy case also needs its documented termination rules. A count
of zero is not a request to write a terminator. Wide variants count wchar_t
elements, not raw bytes. [6]

Investigation: resolve the imported symbol, wrapper and runtime generation.
Do not transfer snprintf return handling to _snprintf merely because names look
similar. Follow negative values through size_t conversions and inspect whether
the error path still sends or logs the partially formed output.

## Format controls versus formatted data

A printf-family format controls argument interpretation. An untrusted string
used as format is different from untrusted bytes passed under a fixed `%s`.
Ordinary field width is a minimum, not an output bound; `*` width/precision
consumes an int, and negative precision is treated as omitted. [7]

Inspect logging wrappers to locate the real format parameter and any second
formatting pass. Recover the variadic ABI and actual promoted argument types;
a decompiler prototype can hide missing or mismatched arguments. For `%.*s`,
prove that the precision converted to int is nonnegative and bounded and the
source is readable for the portion that may be scanned. A large size_t narrowed
to a negative int can defeat the intended precision bound.

## Variadic promotions, mismatches and output side effects

For C++ ellipsis arguments, default argument promotions apply: ordinary float
promotes to double, and narrow integer types undergo integral promotion. Template
parameter packs are not this ellipsis mechanism. [8] Recover the promoted type
and ABI slot used by the callee; changing only a decompiler's format string does
not repair an actually mismatched call.

printf-family `%n` stores a count through a pointer argument rather than printing
that value. `%s` consumes pointed-to characters. [9] A controlled format can
therefore change reads/writes or consume arguments the caller did not supply.
Prove control reaches the format parameter, determine actual supported
conversions and runtime restrictions, and separate this defect from a confirmed
disclosure/write impact. A constant format plus untrusted string data is not
format-string injection, though termination, size and sensitive logging still
need review. Do not assume custom logger syntax is printf-compatible.

## Sources and verification scope

Reviewed 2026-10-02: Linux man-pages 6.19, current GNU libc manual and Microsoft
UCRT documentation. This does not equate all legacy libc formatting behavior.
Examples are constructed, not measured in a specimen.

1. [C++ string_view](https://eel.is/c++draft/string.view.template): ranges and data.
2. [memcpy](https://man7.org/linux/man-pages/man3/memcpy.3.html).
3. [memmove](https://man7.org/linux/man-pages/man3/memmove.3.html).
4. [strncpy](https://man7.org/linux/man-pages/man3/strncpy.3.html).
5. [GNU libc formatted output functions](https://sourceware.org/glibc/manual/latest/html_node/Formatted-Output-Functions.html).
6. [Microsoft snprintf family](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/snprintf-snprintf-snprintf-l-snwprintf-snwprintf-l?view=msvc-170).
7. [GNU libc format syntax](https://sourceware.org/glibc/manual/latest/html_node/Output-Conversion-Syntax.html).
8. [C++ function-call promotions](https://eel.is/c++draft/expr.call).
9. [Linux printf conversions](https://man7.org/linux/man-pages/man3/printf.3.html).
