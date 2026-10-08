---
id: playbook-re-archive-extraction-boundary
title: Recover archive extraction boundaries for vulnerability and malware analysis
kind: playbook
topics: [reverse-engineering, archives, extraction, path-traversal, overwrite, malware-analysis, vulnerability-identification]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover an archive extraction boundary

## Identify the archive consumer before interpreting its output

Use this workflow for unpackers, installers, update agents, document importers
and embedded-payload recovery. Preserve the original container and identify the
actual parsing and disk-write APIs, wrapper checks, configuration and privilege.
A familiar magic value or imported library is a lead, not proof that its normal
extraction path runs. Do not execute extracted programs or installation hooks
merely to identify them.

State the question: can untrusted content affect a forbidden object, exhaust an
intended budget, or evade the check on the eventual selected member? For malware,
ask which recovered member feeds configuration, loading, execution or persistence.
These questions require different evidence even when they share an unpacker.

## Preserve member selection and name transformations

For each relevant entry, record container identity, sequence/index, raw and
decoded name, metadata source, payload location and output identity. Follow
duplicate selection, ZIP local/central disagreement and size-width selection
using `reference-parser-archive-member-identity`.

Trace the name through decoding, separator handling, rewriting, collision checks
and filesystem resolution. Keep the checked representation beside the one used
for writing. Do not assume a pre-extraction listing, signature check or scanner
selected the same member as the eventual consumer. A mismatch is a candidate
bypass only when it defeats the check's actual scope and purpose.

## Reconstruct ordered writes, links and metadata restoration

For relevant entries, recover entry type, link target/base, destination root,
creation disposition, existing object handling and result. Model earlier entries
and preexisting filesystem state before interpreting later ones. Track partial
writes, close/finalization and metadata changes, not only successful function calls.
Use `reference-parser-archive-extraction-effects` for scoped API contracts.

For an overwrite/traversal finding, connect attacker influence to the actual
object affected under the extractor's authority and identify the violated policy.
Record missing preconditions explicitly. A dot-dot string, symlink member or
powerful open API alone is insufficient. A race claim additionally needs a
feasible competing actor and timing window; lexical mismatch alone is not a race.

## Follow accounting and failure through the eventual consumer

Recover checks on produced bytes, member count, nested extraction, retained
outputs and work. Inspect whether failures cancel further work and whether
partial files remain visible or are later reused. Route budget and incomplete
evidence questions to `reference-parser-archive-expansion-partial-evidence`.

For malware identification, follow recovered content to an actual selection or
use site. Report “contains a candidate executable” separately from “loads this
member” and “observed executing it.” If encryption, unsupported formats or limits
stop analysis, state the unexamined scope rather than making a clean verdict.

## Evidence to retain and factual basis

Retain original/member/output identities, decisive offsets or call sites, option
values, representation changes, affected objects, authority, error behavior and
limits on conclusions. Distinguish static recovery from observed runtime effects;
this workflow does not require executing the sample.

Reviewed 2026-10-02. Workflow synthesized from the primary-source contracts in
`reference-parser-archive-member-identity`,
`reference-parser-archive-extraction-effects` and
`reference-parser-archive-expansion-partial-evidence`; those references contain
the offline facts and source URLs. No universal extraction policy is assumed.
