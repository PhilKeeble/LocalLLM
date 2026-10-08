---
id: playbook-validation-causal-deduplication
title: Group repeated findings by evidenced cause without discarding distinct security boundaries
kind: playbook
topics: [reverse-engineering, deduplication, root-cause, crash-analysis, triage, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Separate repeated symptoms from distinct defects

## Choose the identity question before grouping

Distinguish duplicate input bytes, repeated events, similar symptoms, the same
implementation defect, and the same affected deployment. These are different
questions. Name the intended grouping level; an exact input match does not supply
missing environment or state, and an equal crash signature does not establish cause.

Use existing binary, capture and report evidence first. This workflow requires
neither specimen execution nor a particular crash-processing product. Definitions
and limits: reference-validation-finding-identity-crash-signatures.

## Keep each observation recoverable behind provisional groups

Retain input and consumed representation, initial state/history, binary identity,
platform/architecture, diagnostic configuration, raw event, capture scope and
available stacks. Record which values are captured, reconstructed or analyst-assigned.
Keep original observations even when a representative is selected for analysis.

Normalize code locations only with established module or generated-code identity.
Record the signature rule: selected frames, ignored frames, names versus offsets,
and treatment of missing information. A change in that rule changes the grouping,
not the underlying observations. Use format-debug-information-build-matching and
playbook-validation-debugger-evidence for identity and context evidence.

## Recover a causal record for each proposed defect

Connect these elements where evidence permits:

- Relevant input, identity, state and reachable entry boundary.
- Responsible operation and its operands, bounds, ownership or authority.
- Required invariant and the specific point at which it is violated.
- Propagation from that violation to the detected fault or observable effect.
- Conditions and evidence that distinguish alternative explanations.

An invariant is the condition the implementation must preserve, such as a live
owner during use or authorization for the consumed object. Record the earliest
established violation; do not invent an earlier cause merely to complete the chain.
Use playbook-validation-first-fault-cause and
playbook-re-reconstruct-operation-invariants.

## Merge only to the level supported by the common explanation

Compare the responsible operation, violated contract and relevant value/state
dependencies, not just the final instruction or weakness label. A common defect
explanation should account for every member being merged. Different symptoms can
fit that explanation; unexplained differences remain visible.

Keep a candidate relationship when causes are unresolved. Do not chain weak
similarities into certainty: A shares one stack suffix with B and B shares another
with C does not establish a single cause for all three. Retain why each member
belongs and what evidence would split it. Choosing a representative does not
establish that every unexamined member is equivalent.

## Split when distinct violating operations or contracts are evidenced

One terminal handler can receive damage from different producers. Distinguish
arithmetic underallocation, stale ownership, invalid caller prototypes and
uninitialized output even if their final crash resembles the same memory access.
Conversely, do not split solely on relocated addresses, message spelling or the
later detector that happened to observe a common corruption.

For findings without crashes, compare the decision and effect: wrong principal,
wrong object, duplicate commit, disclosed data or unbounded resource consumption.
The same denial response or status code is not an identity for those causes.
Keep unresolved members separately visible rather than forcing a binary merge/split.

## Preserve entry-point and security-impact differences within a cause group

For each affected boundary retain input control, required privileges, validation,
configuration and demonstrated consequence. A defect reachable only after trusted
local input in one binary may be reachable before authentication in another;
the common code does not transfer either reachability claim automatically.

Do not discard a new entry route because its downstream bug is already known.
Equally, a common library name is not enough to assert the affected implementation
is present. Use playbook-re-validate-library-attribution. For malware, retain the
specific sample's activation and effects; shared code does not merge operator or
campaign attribution without separate evidence.

## Use reduction and patch evidence as support, not substitutes for cause

A smaller candidate is useful only if it preserves the issue being compared.
Apply playbook-validation-failure-minimization before treating matching reduced
symptoms as corroboration. A reduction may otherwise converge on a different fault.

When existing patch evidence is available, identify the changed operation and why
the change restores the relevant invariant. Merely observing that several inputs
no longer crash cannot distinguish one correction, multiple corrections, a blocked
entry path or a changed manifestation. Absence of a new capture leaves that question
unresolved; this workflow does not require rebuilding or rerunning the target.

## Report counts and confidence without turning buckets into vulnerabilities

Label counts by their unit: retained inputs, captured events, provisional symptom
groups, supported causes and affected boundaries. Keep unresolved observations
outside confirmed defect totals while preserving their evidence and candidate links.
Do not convert a classifier's severity label into demonstrated exploitability.

Record merge/split reasons and counterevidence. For a supported cause, cite the
operations and invariant; for a provisional group, state the signature and missing
causal link. This makes the finding usable without implying that every sample was
fully analyzed or that repeated symptoms prove broader impact.

## Basis and scope

Reviewed 2026-10-02. Conceptual investigative synthesis using
reference-validation-finding-identity-crash-signatures and linked local references.
The grouping method is not a vulnerability-numbering policy. Primary research:
[Evaluating Fuzz Testing, section 7](https://arxiv.org/html/1808.09700).
