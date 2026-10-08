---
id: playbook-re-document-content-selection
title: Recover document content selection, nested parsing and activation paths
kind: playbook
topics: [reverse-engineering, parsers, documents, pdf, office, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover document content selection and effects

## Identify the original container and the reader's selected view

Preserve original bytes, hashes and acquisition context. Distinguish the outer
container from an extracted/repaired/decrypted derivative. Identify the reader,
parser library, format detection and recovery path. A PDF object listing, CFB
stream listing and OPC ZIP member listing describe different structures.

For PDF, retain selected cross-reference/object identities and repair warnings.
For CFB, retain full storage paths, directory entries and reconstructed stream
extents. For OPC, retain archive-member identity, content types and source-owned
relationships. Determine which view reaches the target application; a forensic
carver's output need not match the application's selected content.

## Follow each nested representation to its actual consumer

Record a mapping from original location to decoded object/stream/part and then
to its parser or interpreter. Preserve decompression, text encoding, encryption
context, external dependencies and partial failures. An offset in a decoded
PDF object stream or CFB mini stream is not an offset in the original file.

For vulnerability identification, trace controlled lengths, indices and counts
through allocation, copying, record iteration and rendering. Check both parent
containment and inner object bounds. For resource exhaustion, distinguish encoded
bytes, expanded bytes, number of objects, recursion/repetition and retained state.
Recover the actual failing operation rather than reporting a malformed field alone.

## Separate content presence, trigger selection and observable effect

For a candidate script, VBA module, embedded object or external relationship,
identify its owning object, trigger or selecting call, relevant host policy and
downstream action. Trace decoded strings and parameters to the actual operation.
Record whether evidence is static reachability, a conditional capability or an
observed effect; do not convert one into another.

Lack of recovered script does not eliminate native parser/rendering defects.
Conversely, an automation API, class identifier or URL alone is not proof of
malicious behavior. Examine who supplies the data, what authority the consumer
has and which file/network/process or security-state change the path can produce.
Do not activate an untrusted document merely to inventory its contents.

## Compare disagreements without normalizing away the decisive evidence

When a scanner, extractor and reader disagree, record their selected object/part,
duplicate policy, repair decisions, decoding support and external context.
Preserve both outputs and the original byte ranges that explain the difference.
Do not substitute a rewritten document for the original vulnerability input.

Treat unsupported filters, encrypted streams, missing external targets and
unresolved macro dispatch as explicit limits. A clean rendering or successfully
extracted source module does not establish that all embedded content was examined
or that the same representation controls host execution.

## Evidence and technical reference routes

Retain original/derived identities, selected paths/object IDs, lengths and units,
decisive call sites, host/policy scope and limits on conclusions. A defensible
vulnerability claim ties input control to a reachable violated invariant and
effect; malware identification additionally needs behavioral/contextual evidence.

- `reference-parser-pdf-object-selection-repair`: indexes, decoded object streams and recovery limits.
- `reference-parser-compound-file-streams-sectors`: CFB chains, mini streams and logical extents.
- `reference-parser-office-relationships-vba-source`: OPC target resolution and VBA source/cache distinctions.
- `playbook-re-media-font-decoding`: embedded image, font and audio/video consumers.
- `reference-parser-archive-member-identity`: archive selection versus raw enumeration.

Reviewed 2026-10-02. This workflow draws on the primary-source contracts in those
references. It is not a complete document-format validator, a macro-policy matrix
or proof that every host follows the same recovery and activation rules.
