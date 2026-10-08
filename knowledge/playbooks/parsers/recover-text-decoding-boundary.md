---
id: playbook-re-text-decoding-boundary
title: Trace text decoding, comparison and final object selection
kind: playbook
topics: [reverse-engineering, unicode, decoding, normalization, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Trace text from original bytes to its actual consumer

## Recover representations and units at every transformation

Preserve original bytes. For each conversion, record input/output encoding,
explicit length or terminator mode, length unit, flags, error policy and actual
returned count. Separate character decoding, grammar unescaping, Unicode
normalization, case mapping and filesystem/URL resolution.

Follow widths and units through allocation and access, including terminator space
and output expansion. A count of displayed characters is not byte capacity, and
a successful replacement conversion does not prove valid original input.
Facts: `reference-native-text-encoding-size-units` and
`reference-parser-unicode-validity-boundaries`.

## Locate the comparison and the later interpretation of the same value

Identify what is compared: raw bytes, UTF-16 units, normalized text, folded keys,
parsed URL components or an opened object's identity. Recover locale, Unicode
tables, options and result-code handling. Trace the exact value version used
after the check; do not silently substitute an analyst-normalized copy.

Compare omitted/explicit lengths, embedded NUL, escaped versus literal syntax,
invalid-sequence policy and concatenation boundaries where relevant. A name
comparison does not freeze filesystem state or establish containment. Route
native object-resolution evidence to the platform's path/handle reference.

## Explain the precise disagreement and security consequence

For a vulnerability, identify controlled bytes, the validator's interpretation,
the consumer's different interpretation, the missing guard and the resulting
violated bound or policy. Distinguish a storage overrun from selecting the wrong
object or permitting an unintended operation. Legal alternative spellings,
replacement characters and parser disagreement alone are not findings.

For nested formats, identify which layer owns each escape sequence. Do not label
all repeated decoder calls erroneous or assume a generic decode-until-stable
operation matches the application protocol. Facts:
`reference-parser-escaping-nul-url-layers` and
`reference-parser-unicode-normalization-comparison`.

## Preserve display ambiguity without treating it as proof of malware

Record logical code-point order and escaped invisible/control characters beside
rendered text. For suspicious filenames, domains or configuration strings, recover
the actual resolver, selected object and downstream behavior. Visually similar
strings may be distinct, and differently encoded strings may compare equally
under the target's actual rules.

Distinguish deceptive-looking presentation, stored capability, reachable behavior
and observed execution. A failed analyst decoder or unusual script mix is not a
benign/malicious verdict. Report unknown code pages, unsupported transformations
and unresolved destinations as evidence limits.

## Evidence and scope

Retain original and transformed identities, decisive offsets/calls, counts with
units, comparison outcomes, selected objects and error paths. Constructed examples
explain contracts; they do not establish that a target follows those paths.

Reviewed 2026-10-02. The referenced factual homes provide primary-source rules.
This workflow is not a universal canonicalization recipe: the intended protocol,
namespace and consumer determine which transformations are appropriate.
