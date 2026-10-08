---
id: reference-parser-pdf-object-selection-repair
title: PDF object selection, object streams, repaired indexes and active content
kind: reference
topics: [parsers, pdf, qpdf, cross-references, object-streams, javascript, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# PDF object selection and recovered views

## PDF cross-reference entries are not all file offsets

PDF cross-reference streams use the widths in /W to encode big-endian fields.
Entry type 0 denotes a free object; type 1 identifies an ordinary object's byte
offset and generation; type 2 identifies an object stream and an index within
that stream. A non-hybrid file's startxref can point to a cross-reference stream.
[1]

Investigative inference: retain object number, generation, selected cross-reference
entry and containing stream identity. Treating every entry as a file offset can
make an extractor examine unrelated bytes. A string found by scanning the whole
PDF is not necessarily in the object selected by the reader. When revisions or
hybrid table/stream structures occur, recover the reader's selection and fallback
rules; do not assume the first textual occurrence wins.

## PDF object-stream offsets use a decoded-stream base

An object stream's /N gives its object count and /First the byte offset of its
first object. Its initial pairs give object numbers and offsets relative to
that first object. Contained objects have generation zero and cannot themselves
be stream objects. The term compressed object does not require an actual
compression filter. [1]

Investigation model: after decoding the containing stream, validate /First and
each relative offset in that decoded byte extent using checked arithmetic. Do
not add those offsets to the original file address. Account for both expanded
bytes and object count; a byte limit does not necessarily bound object-processing
work. Follow referenced objects separately instead of treating one decoded stream
as the entire document.

## qpdf recovery and rewriting change the evidence view

qpdf --check checks selected syntactic, structural and stream-encoding properties;
it can miss errors in stream content. After recovery, other requested operations
can operate on the recovered file view. --show-xref reports a reconstructed table
if reconstruction occurred. Normal rewriting reorganizes the file and removes
orphaned objects. [2]

Investigative consequence: preserve original bytes and warnings alongside any
repaired or rewritten derivative. A recovered object location is not necessarily
the location declared by the original index. A successful check is neither a full
PDF-conformance proof nor evidence that another reader selects the same objects.
Do not describe absence from a rewritten PDF as absence from the original input.

## qpdf raw stream bytes differ from filtered stream bytes

With --show-object, qpdf --raw-stream-data emits stream data without decompressing it;
--filtered-stream-data applies supported decoding filters and fails if it cannot
decode the stream. Either result can be binary. [2]

Investigative inference: identify which representation a length, hash or suspicious
string describes. Do not equate an export from qpdf's parsed view with an unchanged
file carve. Preserve filter settings, encryption/decryption context and
failure status. A filter failure leaves an unexamined layer; it is not an empty
payload. Route decompressor counts and limits to
`reference-parser-decompression-stream-results` and
`reference-parser-decompression-size-memory-limits`. Rendering semantics can
require additional interpretation after stream decoding.

## PDF actions and JavaScript presence do not establish activation

Acrobat supports actions including opening links, playing media and running
JavaScript. Acrobat/Reader JavaScript controls can disable execution or restrict
APIs, with trust settings affecting permitted operations. These are Adobe product
controls, not universal behavior of every PDF reader. [3][4]

For malware analysis, bind a candidate action to its selected document object,
triggering event, script or embedded payload, host policy and downstream effect.
Distinguish an embedded capability from a reachable action and from observed
execution. For vulnerability analysis, absence of scripting does not exclude
faults in object parsing, image/font decoding or rendering. Record unsupported
features rather than calling a document safe because a preview is inert.

## Sources and scope

Reviewed 2026-10-02. qpdf 12.4.2 documentation supplies selected format explanations
and implementation contracts, not a complete PDF validator or a guarantee about
other readers' recovery policies. Workflow: `playbook-re-document-content-selection`.

1. [qpdf object and cross-reference streams](https://qpdf.readthedocs.io/en/stable/object-streams.html): object-stream layout and cross-reference entry interpretation.
2. [qpdf command-line documentation](https://qpdf.readthedocs.io/en/stable/cli.html): checking, recovery, inspection and rewriting limits.
3. [Adobe PDF actions](https://helpx.adobe.com/in/acrobat/desktop/edit-documents/apply-pdf-actions/pdf-actions.html): action categories.
4. [Acrobat JavaScript controls](https://www.adobe.com/devnet-docs/acrobatetk/tools/AppSec/javascript.html): security-policy and trust distinctions.
