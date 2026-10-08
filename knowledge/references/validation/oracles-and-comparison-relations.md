---
id: reference-validation-oracles-comparison-relations
title: Result oracles, differential comparisons, metamorphic relations and equivalence limits
kind: reference
topics: [test-oracle, differential-analysis, metamorphic-testing, result-comparison, semantic-equivalence, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# What a comparison can establish

## An oracle supplies a decision rule, not necessarily an exact output

An oracle is the rule or evidence used to judge a result. It can specify an exact
answer, an allowed set of answers, or a required property. A memory bound or
authorization invariant can be evaluated even when the complete correct output
is unknown. Conversely, producing plausible output does not establish those
invariants. This library uses oracle in this general result-judgment sense.

Investigative consequence: identify the rule's basis, input domain, observed
outputs/effects and unresolved conditions. A reference implementation, previous
version or analyst-written decoder is a comparison candidate, not automatically
ground truth. An execution failure in an adapter does not establish a violation
in the target. Keep unavailable observations distinct from passing outcomes.

## Differential comparison needs a common contract

Differential analysis compares implementations or configurations on corresponding
inputs. SQLite documents comparisons against other database engines and comparisons
with selected query optimizations enabled or disabled. [1] These are examples of
cross-implementation and configuration comparisons, not proof of universal agreement.

Investigative consequence: establish the shared feature, schema, configuration,
input interpretation and required output relation first. Differences can expose
a defect, a permitted choice, incompatible extensions or a bad comparison rule.
Agreement can miss a shared error, particularly when both sides reuse the same
implementation or transformation. Majority agreement alone does not establish
the applicable contract or identify which implementation is wrong.

## Metamorphic relations constrain related inputs and results

A metamorphic relation is a necessary property connecting multiple inputs and
their expected outputs; it supports checking without requiring each complete
answer in advance. [2] Write its precondition, input transformation and expected
output relation explicitly. Related outputs need not be identical.

Constructed example: a pure operation specified to sort integers without loss
must preserve the multiset of values, including duplicate counts. Permuting its
input should not change the sorted value sequence. The same rule does not apply
unchanged to records with equal keys if record order is unspecified. A failed
relation challenges the implementation only after its premises, transformation
and observations are established. A satisfied relation is not complete correctness.

## Round-trip preservation does not imply canonical byte identity

For a lossless codec with compatible encoder E and decoder D, the intended relation
D(E(x)) = x applies to supported values x. The reverse relation E(D(b)) = b needs
stronger conditions: accepted bytes b may have several representations for the
same value. RFC 4648 requires zero pad bits in conforming base64/base32 encoders
and permits decoders to reject nonzero pad bits. [3]

Investigative consequence: distinguish value preservation, canonical encoding and
acceptance policy. An accepting decoder and canonical encoder can change a
noncanonical spelling without changing decoded bytes. Matching encoder/decoder
mistakes can also cancel each other, so a round trip alone does not establish
format conformance. For schema-dependent identity, Protocol Buffers explicitly
does not guarantee canonical serialization even with deterministic output. [4]

## Output order, multiplicity and types are separate comparison dimensions

SQLite does not define SELECT row order without ORDER BY; ties across all ORDER BY
expressions also have undefined relative order. [5] Thus a reordered result can
conform to that contract. This is not permission to ignore ordering in arbitrary
protocols, byte streams or state-changing operations.

Investigative consequence: decide whether comparison concerns a sequence, multiset
(values with counts), set, typed object or exact bytes. Converting to a set hides
duplicate-count errors. Converting all values to text can hide type distinctions.
Dropping unknown fields or collapsing duplicate keys can erase the discrepancy.
Retain raw evidence and explain every normalization, particularly when a signature,
authorization check or downstream parser consumes the original representation.

## Numeric tolerances need a domain and explicit special-value handling

Under ordinary IEEE-style comparison, NaN is unequal to itself and unordered
relative to numbers; execution/trap and compiler assumptions must still be scoped.
[6] Generic equality or an unexplained epsilon is therefore not a complete numeric
comparison rule. Record representation, precision, rounding and allowed error.

Investigative consequence: distinguish exact integers/identifiers from approximate
physical quantities. An error tolerance must not silently approve crossing a size,
quota or authorization boundary. Constructed absolute-tolerance example: with
threshold 1, 0 is close to 0.75 and 0.75 to 1.5, but 0 is not close to 1.5. Such
closeness is not transitive; chaining it into equivalence groups is misleading.
Keep NaN, infinity, signed-zero and raw-bit treatment explicit where relevant.
Detailed numeric contracts: reference-native-floating-validation.

## A response comparison can miss earlier or asynchronous effects

For security analysis, the observed result may include status, output extent,
consumed input, state changes, ownership and external effects—not just a returned
string. Constructed example: two implementations both return denial, but one writes
the protected object before returning. Equal responses do not establish equal
authorization enforcement.

Likewise, a timeout can mean incomplete observation rather than equivalent failure;
pending work can complete later. Compare the same stage of the operation and state
the capture boundary. Use reference-validation-state-observations-reset. For
malware, equal extracted configuration fields do not establish equal activation
or effects, and disagreement with an analyst decoder does not establish evasion.

## A parser disagreement can matter even when both local choices are permitted

Local conformance and end-to-end security answer different questions. If a
validator approves one interpretation but the consumer acts on another, recover
the exact representation, identity, state and effect that cross the boundary.
An implementation need not violate its own parser contract for their composition
to violate the application's security policy.

Conversely, accepting different input sets is not itself a vulnerability. Establish
input control and the forbidden consequence. Use
reference-parser-duplicate-fields-decoded-values and
reference-parser-framing-normalization-differences for scoped format rules, and
playbook-re-parser-differentials for the interpretation chain.

## Sources and scope

Reviewed 2026-10-02. Definitions and named contracts are source-backed; labeled
examples and investigative consequences are synthesis, not target observations.
Workflow: playbook-validation-differential-metamorphic-analysis.

1. [How SQLite is tested](https://www.sqlite.org/testing.html): sections 2 and 9, cross-engine and optimization comparisons.
2. [Chen et al., Metamorphic Testing: A Review of Challenges and Opportunities](https://i.cs.hku.hk/~tse/Papers/2010s/hlmtCSUR.html): authors' 2018 abstract defining necessary relations among inputs and expected outputs.
3. [RFC 4648 section 3.5](https://www.rfc-editor.org/rfc/rfc4648.html#section-3.5): canonical encoding and pad-bit acceptance.
4. [Protocol Buffers serialization is not canonical](https://protobuf.dev/programming-guides/serialization-not-canonical/): deterministic output and schema-dependent identity limits.
5. [SQLite SELECT, ORDER BY](https://www.sqlite.org/lang_select.html#orderby): unspecified row/tie order.
6. [GNU libc infinity and NaN](https://sourceware.org/glibc/manual/latest/html_node/Infinity-and-NaN.html): IEEE-style NaN comparison; not every target's floating-point mode.
