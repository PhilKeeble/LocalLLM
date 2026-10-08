---
id: reference-validation-finding-identity-crash-signatures
title: Crash signatures, stack hashes, duplicate symptoms and root-cause identity
kind: reference
topics: [crash-analysis, deduplication, stack-hash, crash-bucket, root-cause, finding-identity, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Finding identity versus symptom similarity

## A crash bucket is an analysis grouping, not a demonstrated defect

ClusterFuzz defines crash state as a signature derived from a crash stack for
deduplication. [1] Microsoft's analysis documentation distinguishes a general
failure category from a more specific bucket and describes the proposed responsible
instruction as probable. [2] Neither label supplies the complete earlier causal
chain by itself.

Investigative consequence: retain the grouping method, available frames, build
identity and raw event beside a bucket label. Use it to select related observations
for comparison, not to conclude that every member has the same cause or severity.
An exception code classifies an event; a weakness class describes a kind of defect;
neither uniquely identifies a defect instance. A grouping is provisional until its
members are related by evidence about the responsible operation and invariant.

## Stack and coverage signatures can both split and merge defects

Klees et al.'s 2018 study found that stack-based grouping could separate symptoms
of one defect and combine symptoms of distinct defects. Its coverage-based groups
also differed substantially from the study's bug mapping. [3] These are scoped
research findings, not universal error rates for current implementations.

Constructed lifetime example: one early release leaves a queued object stale.
One completion reads its payload; another calls through its saved callback.
The terminal operations differ despite the common release error. Conversely,
independent arithmetic errors in two producers can feed invalid lengths to one
shared copy routine. A matching copy-site stack suffix can conceal the different
responsible calculations. Recover those relationships instead of equating either
matching or differing signatures with cause identity.

## A hash cannot restore information omitted from its input

A stack hash is a compact value computed from selected stack information. Distinguish
two reasons for equality: identical selected information despite different causes,
and a hash collision between different selected information. Comparing the
underlying selected frame records can distinguish the latter but cannot recover
omitted history.

Investigative consequence: using a stronger hash does not solve missing caller,
input, object-lifetime or authority evidence. If a rule keeps only a stack suffix,
retain the complete available trace separately. If only unresolved addresses exist,
do not normalize every unknown frame to one placeholder and treat the result as a
precise identity. Grouping rules should expose uncertainty rather than erase it.

## Address normalization requires code identity and a stated coordinate system

For a location known to belong to a loaded module, a module-relative coordinate
can remove its load-base difference. It is meaningful only with that module's
identity and the address-mapping convention. Same offsets in different builds
need not identify corresponding instructions. Matching names do not establish
matching code. Use format-debug-information-build-matching for PDB, build-ID and
dSYM associations, and playbook-validation-debugger-evidence for captured context.

For generated, unpacked or modified code, retain the relevant bytes and code
generation, not just a reused address. Do not normalize a heap fault address as
though it were an instruction offset. Access address, instruction address and
saved return address have different roles. Preserve raw values alongside any
normalized form so its interpretation remains reviewable.

## Access, allocation and release histories are different evidence roles

AddressSanitizer's documented use-after-free report includes the invalid access,
release and earlier allocation stacks. [4] They are not interchangeable views of
one call stack. Other captures may lack some or all of this history.

Investigative consequence: compare which operation violated ownership and which
operation later used the object. Shared allocation code alone does not establish
a shared lifetime defect; different allocation addresses alone do not establish
different defects. Record the generation and event ordering within each observation.
A snapshot's current stack need not retain an earlier corrupting call. Missing
history leaves attribution unresolved, not disproved. Use
reference-validation-core-dump-coverage and playbook-validation-allocation-lifetime-trace
for evidence scope and ownership reconstruction.

## One patch suppressing several symptoms does not prove one cause

Klees et al.'s patch-based analysis inspected changes for a single conceptual fix
and retained uncertainty when symptom disappearance lacked a causal explanation.
[3] A source revision or binary change can contain several unrelated modifications.

Constructed example: disabling an entire decoder prevents both an overflow and an
authorization mistake in that decoder. The shared nonreproduction does not merge
the defects. Conversely, one missing ownership rule may require corrections at
several exits. Compare the corrected invariant and affected operations rather than
counting changed lines, commits or disappearing crashes. A changed memory layout
can hide a symptom while leaving an invalid access possible.

For completeness of the repair rather than identity of the symptoms, use
reference-validation-patch-presence-semantic-repair and
playbook-validation-patch-variant-review.

## Shared implementation does not erase distinct exposure or attribution claims

An evidenced defect in a common library may appear in several binaries. Retain
each affected implementation and boundary: configuration, caller-controlled input,
privilege, reachable operation and supported effect. One implementation-level
cause can have different deployment impacts; similar source patterns in independent
copies can require separate corrections. State the grouping level explicitly.

In malware analysis, common helper code or a shared crashing parser does not
establish a common operator, campaign or malicious purpose. Keep code similarity,
behavior similarity and contextual attribution separate. See
playbook-re-validate-library-attribution. These are investigative distinctions,
not a rule for assigning CVE identifiers or naming malware families.

## Sources and scope

Reviewed 2026-10-02. Workflow: playbook-validation-causal-deduplication. Constructed
examples and grouping criteria are analytical guidance, not target observations.
Tool names scope supporting definitions; no particular collector is required.

1. [ClusterFuzz glossary](https://google.github.io/clusterfuzz/reference/glossary/): crash state as a stack-derived signature.
2. [Microsoft automated crash analysis](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/using-the--analyze-extension): DEFAULT_BUCKET_ID, BUCKET_ID and probable FOLLOWUP_IP interpretation.
3. [Klees et al., Evaluating Fuzz Testing](https://arxiv.org/html/1808.09700): 2018, sections 7.1-7.3, causal grouping, patch interpretation and signature limitations; not current product defaults.
4. [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): Symbolizing the Reports, distinct access/release/allocation evidence.
