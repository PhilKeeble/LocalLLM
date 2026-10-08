---
id: reference-parser-unicode-normalization-comparison
title: Unicode normalization, case folding, ordinal comparison and visual ambiguity
kind: reference
topics: [parsers, unicode, normalization, case-folding, comparison, confusables, bidi]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Unicode equivalence and comparison contracts

## NFC/NFD and NFKC/NFKD enforce different equivalence relations

Unicode normalization distinguishes canonical from compatibility equivalence.
The four forms apply these operations: [1]

| Form | Operation |
| --- | --- |
| NFD | Canonical decomposition |
| NFC | Canonical decomposition, then canonical composition |
| NFKD | Compatibility decomposition |
| NFKC | Compatibility decomposition, then canonical composition |

Compatibility forms can erase meaningful distinctions and are not an appropriate
universal rewrite of arbitrary text. [1] Investigative inference: recover the
specific form at both comparison and use. Do not assume NFC removes every visual
variation, or that normalization authorizes a filesystem object. Preserve original
text when evaluating a changed identifier or suspicious displayed name.

## Normalized fragments do not guarantee a normalized concatenation

None of Unicode's four normalization forms is closed under string concatenation:
joining two individually normalized strings can require normalization at the join.
[1]

Constructed NFC example: the separate strings U+0065 and U+0301 are individually
NFC, but their concatenation normalizes to U+00E9. An incremental normalizer needs
the relevant boundary context. A check on each stored component does not prove
the combined comparison key has the same property. Recompute output extents
after transformation; input offsets and lengths are not automatically preserved.

## Full case mapping can change length and depend on locale

ICU distinguishes single-character mappings from full string mappings. Full case
mapping can change code-point/unit counts and depend on language and surrounding
text. Locale-independent case folding supports caseless matching; ICU also exposes
a Turkic-mapping option. [2]

Investigative inference: identify the actual mapping API, locale and options.
ASCII lowercasing, full Unicode lowercasing and case folding are not interchangeable
contracts. Recover output sizing and compare the exact keys used at validator,
cache and consumer. A flag named ignoreCase does not establish a universal Unicode
equivalence relation or the target filesystem's case behavior.

## CompareStringOrdinal equality is a status value, not any nonzero return

Windows CompareStringOrdinal performs ordinal rather than linguistic comparison.
Its success results distinguish less-than, equal and greater-than; zero signals
failure. Equality must be distinguished through CSTR_EQUAL. [3]

Investigative inference: a branch accepting every nonzero return accepts unequal
successful comparisons too. Recover lengths and bIgnoreCase as well as the result
test. Ordinal comparison does not by itself normalize canonically equivalent
strings. Do not assign strcmp's zero-means-equal convention to this Windows API.
Whether equality is the correct authorization rule still depends on the object
namespace and operation being checked.

## Confusable skeletons are detection aids, not canonical identifiers

UTS #39 uses skeletons to compare potential visual confusability, and explicitly
warns against using them as normalized identifiers or display strings. [4]

Investigative inference: a visually similar filename, domain or symbol may still
have different underlying code points and select a different object. Record
escaped code points and the actual resolver result. A skeleton match is a lead
for possible deceptive presentation, not evidence of equal identity, malicious
intent or execution. Unicode normalization alone does not solve visual spoofing.

## Bidirectional display order differs from stored logical order

The Unicode bidirectional algorithm operates on logically ordered text and
determines display ordering. Directional controls affect presentation; characters
remain interpreted in logical order. [5]

For malware investigation, preserve escaped control characters and stored code-point
order alongside screenshots or rendered strings. A displayed suffix is not enough
to establish the actual filename extension or a command's token order. Locate the
real path/parser input and resulting object. Bidirectional text also has legitimate
uses; a control character's presence alone does not establish concealment intent.

## Sources and scope

Reviewed 2026-10-02. UAX #15 revision 58 and UTS #39 revision 34 are the inspected
Unicode 18.0.0 documents; the rules here are selected mechanisms, not assumptions
about a target's Unicode table version. ICU and Windows comparisons retain their
own API scope. Workflow: `playbook-re-text-decoding-boundary`.

1. [UAX #15](https://www.unicode.org/reports/tr15/tr15-58.html): forms, compatibility limits and concatenation.
2. [ICU case mappings](https://unicode-org.github.io/icu/userguide/transforms/casemappings.html): simple/full mappings, locale and folding.
3. [CompareStringOrdinal](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-comparestringordinal): comparison and return contract.
4. [UTS #39](https://www.unicode.org/reports/tr39/tr39-34.html): confusable-skeleton limits.
5. [UAX #9](https://www.unicode.org/reports/tr9/): logical versus display order.
