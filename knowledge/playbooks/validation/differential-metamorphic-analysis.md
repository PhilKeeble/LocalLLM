---
id: playbook-validation-differential-metamorphic-analysis
title: Compare implementations and transformed inputs with justified result oracles
kind: playbook
topics: [reverse-engineering, differential-analysis, metamorphic-testing, test-oracle, semantic-equivalence, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Establish what a difference means

## Define the question and the comparison boundary

Name the property being investigated: decoded value, consumed extent, bounds,
authorization decision, committed state or observable behavior. Identify the
implementation/configuration and representation at each side. Compare existing
code and captures before seeking new observations; no particular tool or target
execution is required by this workflow.

Define the oracle: an applicable contract, invariant, supported expected result
or justified relation. An oracle is the rule used to judge an outcome, not a
synonym for a trusted tool. Use reference-validation-oracles-comparison-relations.
Mark a recovered proprietary rule as a hypothesis when its evidence is incomplete.

## Establish shared semantics before comparing implementations

Match the relevant format edition, schema, features, limits, input units, initial
state and configured policy. Distinguish two independent implementations from
wrappers over the same library or two copies of the same decoder. Neither
agreement nor disagreement alone identifies a correct side.

For compiler, emulator or architecture comparisons, establish the modeled behavior,
operand widths, ABI, environment and defined input domain. Source-level undefined
behavior is not a portable expected-output contract; the emitted binary still
needs its own instruction-level interpretation. Different instruction sequences
can implement the same observable rule. Do not compare bytes as a proxy for semantics.
Use reference-native-compiler-transformations for source/binary and optimization
distinctions, and reference-validation-emulation-execution-models for model limits.

## State a transformation's premises and expected relation

Metamorphic analysis compares related inputs/results. Select a relationship only
when the target contract supports it. These are conditional examples, not universal
transformations:

| Candidate relation | Required premise and main pitfall |
| --- | --- |
| Encode then decode preserves a value | Compatible lossless domain; paired mistakes can cancel |
| Canonicalize twice equals once | Operation is a canonicalizer, not an arbitrary decoder |
| Permuting input preserves a sorted result | Same ordering contract; duplicate records and tie order matter |
| Different stream chunking preserves final parse | API promises chunk independence; datagram boundaries, timeouts and EOF may change meaning |
| Alternate spellings select the same field | The actual format/consumer defines those spellings as equivalent |

Record what may change as well as what must remain equal. Do not assume removing
permissions, increasing resource limits or reordering requests preserves behavior
without recovering the applicable state and policy rules.

## Define the observable result and its equality rule

Keep status, consumed/produced lengths, typed values, residual input, state changes
and effects that matter to the claim. Separate attempted, accepted, committed and
acknowledged operations. A common error message does not prove common side effects.
For pending work, record the observation boundary rather than assuming completion.

Decide whether order and multiplicity matter. Preserve type, missing-versus-present
fields, duplicate occurrences and unknown data where relevant. Normalize only
distinctions proven irrelevant to the question; retain raw evidence. For approximate
numeric outputs, justify tolerances and treatment of NaN/infinity/signed zero.
Never round away an exact object identifier or a security-boundary difference.

## Separate deterministic differences from uncontrolled conditions

Compare matching initial conditions and identify differences in time, randomness,
locale, persistent state, scheduling and dependencies. A different observation
can be permitted nondeterminism, incomplete capture or an adapter artifact. Do not
force a deterministic expected answer onto a contract that permits several results.

If the evidence cannot distinguish these explanations, report an unresolved
discrepancy. A timeout is not automatically a completed rejection or proof of
nontermination. A null/missing display value is not proof the target produced null.
Use playbook-validation-faithful-harness and reference-validation-state-observations-reset
for adapter and state boundaries.

## Trace a discrepancy to the first relevant divergence and consequence

Find where bytes, values, consumed extent, decisions or state first differ in the
available evidence. Work forward to the security-relevant effect and backward to
the operation or assumption responsible. Different parser policies can be locally
permitted yet unsafe when composed; a compatibility difference with no evidenced
security consequence remains a compatibility finding or lead.

For malware, distinguish target interpretation from the analyst's extraction or
emulation model. An altered sample/configuration is a constructed condition, not
unmodified behavior. Establish which handler and effects the actual specimen can
reach; differing decoded outputs alone do not prove concealment or attribution.
Route parser chains to playbook-re-parser-differentials.

## Preserve the relation when simplifying and reporting

Keep both observations, corresponding inputs, transformation, oracle premises,
comparison rule and relevant conditions. Reduction must retain the discrepancy
and its meaning on all compared sides, not merely one crash. Use
playbook-validation-failure-minimization; group resulting findings by evidenced
cause using playbook-validation-causal-deduplication.

State whether the evidence supports contract violation, unsafe composition,
permitted variation, faulty oracle or unresolved difference. Agreement means only
that the selected observations satisfied that relation; it does not prove safety
or completeness. Existing evidence can establish the conclusion without a fresh run.

## Basis and scope

Reviewed 2026-10-02. Conceptual synthesis based on
reference-validation-oracles-comparison-relations and linked local references.
Conditional examples are investigation aids, not observations of a particular target.
