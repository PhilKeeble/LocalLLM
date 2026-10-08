---
id: reference-native-library-signatures-templates
title: Library fingerprints, ambiguous matches and C++ template attribution
kind: reference
topics: [static-linking, function-identification, signatures, templates, comdat, provenance]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Identify compiled components without overclaiming provenance

## A fingerprint match is not semantic equivalence or an API contract
Reviewed 2026-10-02. A code fingerprint summarizes selected properties of a body.
Equality of that summary does not establish equality of omitted constants, callees
or interface preconditions. Record what the particular comparison includes.

Scoped implementation example: Ghidra Function ID hashes instructions against known functions.
Its full hash omits constant values; its specific hash selectively includes
constants judged not to be addresses. Parent/child matches help disambiguate. [1]
These are matching rules, not formal equivalence checking.

Constructed candidate: two routines have the same instruction shape but compare
an input against different constants. A shape match alone cannot establish the
same accepted range. Inspect the actual compare, branch and error path before
transferring a validation contract. Conversely, a relocation-adjusted address
need not imply different behavior. Save the function extent, database identity,
hash/match kind and relevant operand differences. A name assigned by analysis
is a hypothesis; do not silently convert it into a trusted sanitizer summary.

## One assigned function name need not identify one library version
Ghidra Function ID can group candidates sharing a base function name into a
Single Match. Ambiguous version/variant fields can be omitted even when a name
is assigned. Name grouping removes namespace and parameter information. [1]

Constructed evidence: helper H occurs unchanged in releases A and B; only B
fixes a separate parser P. Matching H does not distinguish A from B and does
not show whether P's fix is present. Retain the unresolved version set and
inspect the affected implementation. A version string elsewhere in the binary
is corroboration only when tied to this component/build. Do not report a CVE
as present or absent solely from one library label; establish affected code,
patch state, relevant configuration and the path being investigated.

## No signature hit does not establish custom code
An identification miss leaves provenance unresolved: the reference collection,
selection rules and recovered function boundaries limit what can match.
For example, Ghidra Function ID databases target a processor and can filter by compiler or
language. Compilation changes can defeat matching; thresholds suppress some
small ambiguous matches. [1] Database coverage and matching failure differ.

Investigative consequence: record the enabled databases, filters and function
boundary evidence before treating a miss as meaningful. An inlined fragment
may not be a candidate whole function at all. Do not label an unmatched loop
as proprietary cryptography or unknown application logic solely because no
name appeared. Follow inputs, outputs, callees and constant use, preserving
unknown provenance separately from observed semantics. Similar code in a
reference build can narrow a hypothesis without proving an exact source release.

## Inline and template bodies can originate in several translation units
GCC 14.1 describes out-of-line copies of needed inline functions and analogous
template instantiations. Supported COMDAT linking discards duplicate copies;
other target mechanisms differ. [2] This is not a universal layout rule.

Constructed investigation: app1.o and app2.o both contain a header-defined helper
for the same instantiation, and the final image retains one copy. The retained
body does not uniquely identify which application source file supplied its
logic. Nor does a demangled template name prove the exact standard-library
release, allocator policy or object representation. Recover actual layout and
call behavior separately. A header implementation can exist without a dynamic
library dependency; archive selection facts live in
format-dependency-evidence-symbol-resolution.

## Template instantiation does not guarantee unique body identity
GCC's template/inline emission rules describe why multiple object files can
contain copies. [2] Subsequent optimization and identical-code folding are a
different issue: see reference-native-compiler-transformations for their facts.

Investigative consequence: do not count distinct recovered names as distinct
machine implementations, or infer equal source types from equal body addresses.
Constructed case: two wrappers each return their argument unchanged. Even if
their body bytes match, callers may use different units or ownership contracts.
A shared return instruction does not establish interchangeable API semantics.
Preserve call-site contracts and any specialization-dependent constants instead
of replacing all template-like routines with one unchecked generic summary.

## Provenance and security-relevant semantics need separate records
Use three independent claims: candidate component origin; observed operation;
validated contract under stated preconditions. Constructed example: a routine
looks like a known copy helper, performs a byte copy, and is called with a
length derived from untrusted input. Library attribution does not establish
that the destination has that capacity or that caller length units are correct.

Similarly, a recognized third-party function is not automatically irrelevant
to review. Prioritize its boundary conditions and actual affected code rather
than excluding it as trusted. For evidence of inclusion versus runtime lookup,
use format-dependency-evidence-symbol-resolution; for a verification sequence,
use playbook-re-validate-library-attribution. These are investigative inferences,
not a claim that a signature database proves security properties.

## A recognized library does not classify its caller as benign or malicious

For malware analysis, library provenance and application behavior are separate
claims. A known decompressor, document parser or networking helper can support
many different callers. Follow the selected input, configuration, decoded output
and subsequent operations before assigning behavioral significance.

Constructed example: two callers use the same decompressor body; one renders an
image, while the other passes output into a dynamic-loading path. The library
match does not distinguish them. Conversely, a parser bug in a recognized library
still needs the affected code and reachable input path; its reputation does not
validate the caller's sizes or configuration. These are attribution inferences,
not evidence about an actual specimen.

## Sources and scope
1. [Ghidra Function ID help, official source](https://raw.githubusercontent.com/NationalSecurityAgency/ghidra/master/Ghidra/Features/FunctionID/src/main/help/help/topics/FunctionID/FunctionID.html): overview, hashes, parent/child matching, library fields, Single Match, thresholds and name grouping. Rolling main-branch documentation reviewed 2026-10-02; not a claim about every installed release/database.
2. [GCC 14.1 vague linkage](https://gcc.gnu.org/onlinedocs/gcc-14.1.0/gcc/Vague-Linkage.html): inline functions, template instantiations and target-dependent duplicate elimination; reviewed 2026-10-02.

Examples are constructed identification counterexamples, not specimen findings.
