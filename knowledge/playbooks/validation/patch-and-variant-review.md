---
id: playbook-validation-patch-variant-review
title: Investigate patch completeness and neighboring vulnerability variants
kind: playbook
topics: [patch-analysis, binary-diffing, invariant, guard-analysis, variant-analysis, regression, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Follow the repaired rule, not only the changed bytes

## Establish the comparison and the original defect

Identify the before/after artifacts, architecture, component, available provenance
and configuration differences. Separate a vendor's affected-release statement from
what has been established about these binaries. Preserve unresolved backports,
embedded copies, generated code and loaded-image identity.

State the suspected original defect as input or event -> transformation/state ->
invalid operation -> supported effect. Name the invariant that fails and the
evidence for each link. If only a changed function is known, treat its intended
security purpose as a hypothesis. A security update can contain several repairs
and unrelated changes. Facts and limits: reference-validation-patch-presence-semantic-repair.

## Map corresponding operations through compiler changes

Use available instructions, data references, call relationships, constants and
validated symbols to locate the operation in each artifact. Compare its inputs,
outputs, branches and effects even when addresses, function boundaries or local
variable names differ. Record confidence in each correspondence.

Distinguish an absent operation from a failure to recover its inlined or redirected
form. Inspect relevant callers and exceptional exits, not only a matching byte
prefix. If compilation differences obscure the comparison, state what remains
unknown; do not infer repair from the absence of a familiar instruction pattern.
Use reference-native-compiler-transformations for those interpretation limits.

## Explain exactly how the change protects the sensitive operation

For a new guard, recover the accepting/rejecting edges, compared value and width,
units, object identity and all paths from the check to the use. Determine whether
the rejecting path can still reach the operation through cleanup, retry or another
entry. A dominating comparison is not enough if both outcomes lead to the sink.

For a lifetime or concurrency change, identify the ownership/protection interval
and the participants covered by it. For authorization, connect the subject and
object checked to the actual action. For a parser change, follow the representation
consumed downstream, including decoding or normalization after validation. State
whether the change repairs the invariant, restricts exposure or changes detection.
Retain deployment assumptions; do not silently turn a conditional mitigation into
an unconditional fix.

## Search arithmetic and representation neighbors by mechanism

Starting from the evidenced defective rule, inspect plausible neighbors rather
than treating every similar instruction sequence as vulnerable:

- Lengths: lower and upper bounds, signedness, narrowing, multiplication,
  header/terminator additions, element-versus-byte units and inclusive ends.
- Representations: raw versus decoded fields, normalization order, duplicate-field
  policy and the identity ultimately used by the consumer.
- Copies: scalar/vector paths, alternate allocators, compatibility layouts and
  separate callers of a shared helper.

These are candidate dimensions, not assertions that each exists in the target.
For each relevant location recover its own accepted domain and consumed value.
A similar calculation protected by a sufficient earlier bound may be unaffected.
Record that reason rather than counting every pattern match as a finding.

## Search temporal and authority neighbors by invariant

For a lifetime flaw, inspect aliases, callbacks, reentry, cancellation, late
completion and exceptional cleanup that touch the same ownership rule. For a
state or authorization flaw, inspect alternative entry points, retry/reconnect,
object replacement, cache identity and partially completed operations.

Recover the specific transition or schedule required at each candidate. A second
call site is not a second demonstrated defect until its preconditions and invalid
operation are supported. A safe common helper does not establish that every caller
supplies the required state; an unsafe-looking helper can still have constrained
callers. Keep missing edges explicit. Routes: playbook-re-sensitive-data-flow,
playbook-re-reconstruct-operation-invariants and playbook-validation-error-path-investigation.

## Interpret before/after observations without equating silence with repair

When authorized observations are available, identify whether the relevant path
was reached, the invalid operation occurred, the required effect changed, or the
input was rejected earlier. Keep those outcomes separate from a missing crash.
Retain input, state, build, configuration and collection differences that could
explain the observation. No new execution is required merely to fill an evidence
field; a static semantic claim and its unresolved assumptions can be reported.

For legitimate inputs, compare behavior against the applicable contract, not an
assumption that every old output must remain identical. Intended stricter rejection
can be part of a repair. Conversely, a new failure response may conceal an earlier
unauthorized effect. Use reference-validation-oracles-comparison-relations for the
comparison rule and playbook-validation-first-fault-cause for causal evidence.

## Hand off bounded conclusions and unresolved variants

Report separately: identified artifact/patch presence; corrected operation and
invariant; demonstrated or inferred protection; exposure conditions; related
locations reviewed; and candidates still unresolved. For a regression claim,
retain evidence of the earlier repaired state as well as the later defective one.
Do not describe a plausible variant as confirmed or an inspected subset as a
complete audit of every component.

Constructed reporting form: "The new guard constrains this copy's byte count for
the reviewed entry and unchanged buffer. The asynchronous consumer reloads a
separate field; its protection remains unresolved." This conveys useful evidence
without inventing a defect at the second site. For malware, label all forced
conditions and preserve the distinction between original behavior and behavior
under analyst intervention.

## Source basis and scope

Reviewed 2026-10-02. Local investigation synthesis; the examples and candidate
dimensions are analytical guidance, not observations about a target.

- [Project Zero patch and variant analysis](https://projectzero.google/2022/06/2022-0-day-in-wild-exploitationso-far.html): root-cause analysis as the basis for assessing completeness and related defects.
- [Red Hat backporting](https://access.redhat.com/solutions/57665): why upstream-version labels alone cannot settle patch presence.
- Scoped technical contracts and additional source bases: reference-native-path-feasibility-guards,
  reference-native-compiler-transformations and reference-validation-patch-presence-semantic-repair.
