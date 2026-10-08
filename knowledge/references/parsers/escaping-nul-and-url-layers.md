---
id: reference-parser-escaping-nul-url-layers
title: JSON escapes, decoded NULs, form decoding and URL separator differences
kind: reference
topics: [parsers, escaping, json, nul, urls, percent-encoding, separators, decoding]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Escaping and text-consumer boundaries

## JSON escapes are syntax for decoded values, not literal substrings

JSON strings escape quotation marks, backslashes and control characters.
The \u form uses four hexadecimal digits; supplementary characters can be
represented by two escaped UTF-16 surrogate units. [1]

Investigative inference: record whether a filter inspects raw JSON bytes or the
decoded string. An escaped delimiter is data in the JSON string but may become
syntax if the application later supplies that string to another parser. Apply
the grammar of that later consumer; JSON escaping is not shell, SQL, HTML or URI
escaping. Decoded property-name equality and duplicate handling are covered in
`reference-parser-duplicate-fields-decoded-values`.

## JSON can represent NUL without containing a literal zero byte

JSON's escaped U+0000 represents a NUL character in the decoded value; raw control
characters are not allowed unescaped in JSON strings. [1]

Constructed boundary: a counted decoded string contains prefix, U+0000 and suffix.
A validator examines the whole value, while a later NUL-terminated consumer may
use only prefix. Establish the actual interop/API behavior: some wrappers reject
embedded NUL instead of truncating. The candidate issue is a demonstrated check/use
disagreement, not merely the presence of an escape. Buffer bounds and semantic
identity need separate evidence; see `reference-native-strings-copy-format`.

## JSON syntax acceptance does not guarantee valid surrogate structure

RFC 8259's grammar permits escaped unpaired surrogate code units and warns that
receivers can disagree about such values. This is distinct from a well-formed
Unicode scalar sequence. [1]

Investigative inference: preserve whether the parser rejects, retains or replaces
the code unit and what happens during later UTF-8 conversion. Do not call an
escape a valid Unicode character solely because JSON parsing succeeded. A raw
signature match, text log and reserialized result may describe different
representations of the same submitted input.

## Form decoding treats a literal plus differently from percent-encoded plus

WHATWG application/x-www-form-urlencoded parsing first splits name/value fields,
replaces literal plus bytes with spaces, then percent-decodes and UTF-8-decodes
the fields. [2]

Constructed example: A+B yields A space B, while A%2BB yields A+B. A later extra
form-decoding pass can change the second result again. This is a form-encoding
rule, not a universal meaning of plus in URL paths or arbitrary URI components.
Recover the actual entry API and media type before assigning decoding semantics.

## WHATWG special-URL parsing treats backslash as a separator in path state

In WHATWG's path state for special schemes such as https, U+005C backslash acts as
a separator and reports a validation error; that error does not inherently mean parsing returns failure.
This rule is conditional on the scheme/parser state. [2]

Investigative inference: a validator implementing a different URL grammar can
disagree with a browser-oriented consumer about path or authority boundaries.
Inspect the parsed components and selected destination, not a raw prefix alone.
Do not generalize this rule to every URI scheme, POSIX path or Windows namespace.
Native filesystem resolution remains a later boundary with its own contracts.

## Multiple decoding stages need distinct grammar and ownership

RFC 3986 separates URI component parsing from decoding reserved octets and warns
against decoding the same representation repeatedly. The detailed rules and a
constructed %252F example live in
`reference-parser-framing-normalization-differences`.

Investigation model: name every stage's input/output representation and the
grammar it removes. Decoding a JSON string that contains a URL and then parsing
the URL can be legitimate layered processing. Reinterpreting already decoded
application data as another escape layer needs evidence of an intended grammar.
Locate the security check relative to the final separator, NUL and name resolution;
the number of decoder calls alone is not a vulnerability.

## Sources and scope

Reviewed 2026-10-02. RFC 8259 (2017) supplies JSON string rules. WHATWG is a living
URL standard, not the contract of every URL library. URI generic-syntax facts
remain in the linked RFC 3986 reference to avoid duplicate conflicting homes.
All short input examples above are constructed.

1. [RFC 8259 §§7-8](https://www.rfc-editor.org/rfc/rfc8259.html): escaping, controls, surrogate pairs and unpaired values.
2. [WHATWG URL Standard](https://url.spec.whatwg.org/): URL path-state validation and application/x-www-form-urlencoded parsing.
