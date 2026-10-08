---
id: reference-validation-patch-presence-semantic-repair
title: Patch presence, semantic repair, incomplete fixes and related variants
kind: reference
topics: [patch-analysis, binary-diffing, backports, root-cause, incomplete-fix, variant-analysis, regression, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Patch evidence and the property being repaired

## Root-cause repair differs from blocking one trigger

Project Zero distinguishes root-cause analysis, patch-completeness analysis and
searching for related vulnerabilities. Blocking the path used by one demonstration
does not establish that the underlying vulnerability was removed. [1,2]

For investigation, define the invariant: a condition that must hold for the
operation to be valid. Examples include a consumed byte range staying within a
live object, or an action being authorized for the same object actually changed.
Compare how that condition is established before and after the change. A new
branch alone does not identify its security purpose or prove sufficient repair.

Distinguish repairing the invalid operation from restricting exposure, detecting
a later violation, or reducing its consequences. An exposure restriction may be
effective under its stated conditions without repairing the retained implementation.
These are different claims, not a ranking of every possible remediation strategy.

## A version string is not patch-presence evidence by itself

Red Hat documents backporting security fixes into older upstream package versions;
version-only comparisons can therefore misclassify its patched packages. [3]
This establishes why upstream version ordering alone is insufficient, not that
every old build contains a fix or that all vendors use the same release scheme.

For a binary investigation, distinguish the identified package/build, the bytes
available on disk, the implementation retained in each component, and the code
selected in the observed execution. A vendor advisory supplies a release claim;
matching that claim to the actual artifact is another evidence step. A fixed
shared component does not by itself establish the status of a separately embedded
copy. Keep uncertain build provenance separate from an observed instruction-level
guard. See playbook-re-validate-library-attribution and
format-debug-information-build-matching for component and symbol evidence.

## Changed addresses and function counts are not semantic changes

Inlining, code folding, specialization and altered loop structure can change the
mapping between source operations and machine-code regions. The scoped compiler
facts are in reference-native-compiler-transformations. Neither equal offsets nor
matching function names establish corresponding operations across builds.

Analytical consequence: compare inputs, transformations, predicates, ownership and
effects. Record candidate correspondences using callers, constants, data references
and relevant instruction semantics. Preserve ambiguity where a function was split,
merged or inlined. A changed region may combine the intended repair, unrelated
features and build changes; its size does not measure the number of fixed defects.
An unchanged helper does not establish that its callers retained the same checks.

## A new length check must constrain the value actually consumed

Constructed example: unsigned 32-bit n is narrowed to unsigned 16-bit m; storage
of m bytes is allocated, while a later operation copies n bytes. A new check
m<=capacity does not connect the original n to that capacity. For n=65537,
m=1; checking 1 does not establish room for 65537 bytes.

To credit a repair, trace the checked value through the actual conversion and
consumer. A bound n<=65535 removes this particular narrowing discrepancy, but
does not independently establish successful allocation, sufficient source extent,
correct units or lifetime. A repaired size calculation must also account for
headers, terminators and alignment where those are actually consumed. Numeric
contracts: reference-native-integer-size-buffer-arithmetic. Guard/path conditions:
reference-native-path-feasibility-guards. This example is not a target finding.

## Revalidation and ownership changes have temporal scope

Constructed example: a pointer is checked before invoking a callback, and the
callback can cause the pointed-to object to be released. Adding another check
before that callback does not establish lifetime at the later use. Conversely,
retaining a valid ownership reference through the use may repair lifetime without
making the pointer's address change.

For such a candidate, identify the object generation, ownership transitions,
possible reentry and the exact interval protected by the change. Copying a request
field stabilizes that copy; it does not automatically preserve objects reached
through pointers in it. Repeating authorization is meaningful only for the
identity, operation and object subsequently used. Follow each contract separately;
do not call a patch complete because one added check looks security-related.

## A variant and a regression require different supporting evidence

Project Zero's analyses discuss both related vulnerabilities and previously fixed
vulnerabilities becoming possible again. [1,2] Use explicit working distinctions:
a variant shares a relevant defective rule or mechanism; a regression reintroduces
behavior that an earlier repair had removed. Similar symptoms alone prove neither.

For a variant candidate, show the related invariant and independently establish
its input, path and violation. For a regression claim, also establish the earlier
repaired state and the later change in behavior or semantics. Two endpoints with
different configurations are insufficient to identify the introducing revision.
Missing history leaves the historical claim unresolved even if the current defect
is well supported. Different weakness classes or common library names alone do
not identify a relationship between defect instances.

## Nonreproduction supports less than a semantic explanation of repair

Constructed example: changing allocation layout leaves an invalid subobject write
in mapped storage, so a previous crash disappears while the violation remains.
Conversely, rejecting the request before decoding may prevent the invalid operation
without exercising the changed decoder at all.

Report the observed outcome separately from the inferred reason. Compare the
relevant operation, object extent, state and effects, not only exception status.
If only one input/configuration was observed, do not promote that result to all
paths or all similar inputs. See reference-validation-finding-identity-crash-signatures
for why disappearing symptoms do not establish one cause, and
reference-validation-oracles-comparison-relations for justified comparisons.

## Analyst-modified malware is a different evidence condition

An analyst change that forces a branch, substitutes a response or bypasses a
check can help explain reachable capability under that intervention. It does not
show that the original specimen naturally met the same condition. Preserve the
original and modified code identities, changed condition and resulting effects.

A vulnerability fix in a component neither proves nor disproves malicious intent
in its callers. Common patched library code is not operator attribution. Keep
security-defect status, recovered program behavior and contextual malware
classification as separate conclusions. Route intervention provenance through
playbook-validation-controlled-observation; patch analysis does not authorize
executing or modifying an otherwise out-of-scope specimen.

## Sources and scope

Reviewed 2026-10-02. This reference combines the following primary-source
methodological distinctions with explicitly constructed examples and local
investigative reasoning. It does not reproduce any vulnerability or establish
patch status for a particular product. Workflow: playbook-validation-patch-variant-review.

1. [Project Zero, 2022 in-the-wild review](https://projectzero.google/2022/06/2022-0-day-in-wild-exploitationso-far.html): June 2022, root-cause, variant and patch-analysis distinctions; historical observations, not current prevalence estimates.
2. [Project Zero, Deja vu-lnerability](https://projectzero.google/2021/02/deja-vu-lnerability.html): February 2021, introductory distinction between correcting a flaw and covering relevant paths/variants; no case-study reproduction claimed.
3. [Red Hat, backporting](https://access.redhat.com/solutions/57665): security-fix backports and upstream-version interpretation; page updated June 2025, Red Hat-specific release practice.
