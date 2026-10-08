---
id: reference-native-text-encoding-size-units
title: Text encoding, terminators, and size units
kind: reference
topics: [encoding, utf-16, utf-8, windows-api, buffer-sizing, integer-units]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Text encoding, terminators, and size units

## Text units are not interchangeable allocation sizes

UTF-8 encodes a Unicode scalar value in one to four bytes; UTF-16 uses one or
two 16-bit code units. A supplementary character's UTF-16 pair corresponds to
one scalar value, not two UTF-8 characters. [3][4]

Keep bytes, code units, scalar values, grapheme clusters and destination capacity
distinct. Recover each API's actual unit before multiplying or narrowing a count.
A display-oriented character limit does not establish an encoded byte bound.
Use `reference-parser-unicode-validity-boundaries` for invalid encodings, surrogate
boundaries and grapheme counts; native wchar_t width is ABI-specific.

## WideCharToMultiByte input units differ from output bytes

On Windows, WideCharToMultiByte.cchWideChar counts UTF-16 WCHAR units;
cbMultiByte is destination bytes. Success returns output bytes. With cbMultiByte=0,
the API reports required bytes without writing the output buffer; failure returns
zero. [1]

Investigative inference: an allocation based only on the input unit count may be
too small. Check the sizing result before allocation and use the same code page,
flags and input for the conversion. If input can change between sizing and use,
the old result does not establish current capacity. Trace the second call's result
rather than assuming that the sizing call guaranteed success.

## MultiByteToWideChar output capacity is in WCHAR units

On Windows, MultiByteToWideChar.cbMultiByte counts input bytes; cchWideChar counts
destination WCHAR units. Success returns WCHAR units, not bytes. A zero destination
capacity requests the required unit count; failure returns zero. [2]

Investigative inference: multiply a successful required count by sizeof(WCHAR)
with checked arithmetic when allocating raw bytes. Keep the element count when
passing capacity back to this API. Treat failure as an error path, not permission
to consume an empty or previously populated destination. Do not substitute an
arbitrary bytes-per-character multiplier for the actual selected conversion.

## Windows conversion count -1 includes the terminating NUL

For WideCharToMultiByte and MultiByteToWideChar, input count -1 scans through NUL
and includes it in the output and returned count. A positive input count processes
exactly that extent; omitting NUL from the input extent does not automatically
append one to the output. Input count zero fails. [1][2]

Investigative inference: distinguish the -1 sentinel from a narrowed large length.
For positive counts, separately prove termination before later C-string use.
For -1, prove that the source has a terminator in readable storage. Do not add
or subtract a terminator twice when recording a returned count or framing output.

## Windows UTF-8 conversion flags select rejection versus replacement

For CP_UTF8, Windows conversion flags must be zero or the applicable error flag:
MB_ERR_INVALID_CHARS when decoding, WC_ERR_INVALID_CHARS when encoding. On Vista
and later, these flags reject invalid sequences; without them, invalid sequences
are replaced by U+FFFD. Older Windows behavior differs. [1][2]

Investigative inference: successful conversion with replacement is not proof of
valid original text. Preserve the original bytes and error policy when comparing
validator and consumer. Distinct malformed inputs can lose identity during
replacement. A recovered flag check must apply to the actual code page and call,
not an unrelated conversion elsewhere in the binary.

## Legacy code-page best-fit conversion can alter security-sensitive names

WideCharToMultiByte's WC_NO_BEST_FIT_CHARS suppresses approximate mappings for
applicable legacy code pages, using a default character instead. lpUsedDefaultChar
reports default substitution. CP_UTF8 requires both default-character pointers
to be null and does not accept this flag. [1]

Investigative inference: disabling best fit does not prove lossless conversion;
default substitution still needs an explicit policy. Trace the converted name
into the actual file, resource or identity lookup and compare it with the checked
name. Record the selected code page; a system-dependent default is not a portable
encoding label. Do not apply a legacy-code-page flag recipe to UTF-8.

## Sources and scope

Reviewed 2026-10-02. Windows API rules are not portable contracts for every text
library. Unicode representation rules are shared; normalization and equality are
separate in `reference-parser-unicode-normalization-comparison`.

1. [WideCharToMultiByte](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte): units, count modes, flags and substitution.
2. [MultiByteToWideChar](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-multibytetowidechar): destination units, count modes and invalid input.
3. [RFC 3629 §3](https://www.rfc-editor.org/rfc/rfc3629.html): UTF-8 scalar encoding.
4. [Unicode UTF FAQ](https://www.unicode.org/faq/utf_bom.html): UTF-16 pairs and corresponding encodings.
