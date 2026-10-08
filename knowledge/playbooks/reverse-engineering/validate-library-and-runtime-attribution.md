---
id: playbook-re-validate-library-attribution
title: Validate static-library, template and compiler-runtime attribution
kind: playbook
topics: [static-linking, signatures, compiler-runtime, templates, provenance, triage]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Turn component-recognition clues into bounded evidence

## Preserve match provenance before assigning a contract
Reviewed 2026-10-02. Local workflow based on the sources below; it does not
require executing a specimen. Record binary hash, machine coordinates,
function extent, tool/database version, enabled filters and candidate matches.
Separate original symbols from names introduced by an analyzer or analyst.
Retain ambiguous component versions instead of selecting the most familiar one.

For matching limits, retrieve reference-native-library-signatures-templates.
For helper semantics, retrieve reference-native-compiler-runtime-helpers.
Do not use a second tool repeating the same database label as independent
confirmation. Prefer an independently matched implementation, meaningful
instruction/constant comparison or exact build evidence.

## Verify the behavior needed by the investigation
Recover inputs, result encoding, memory outputs, side effects, error/exception
paths and preconditions at the actual call boundary. Examine constants and
callees that affect the suspected behavior even if a signature matcher ignores
them. Check whether an apparent thunk redirects or adapts that interface.

Constructed helper identification: a comparison routine is named __cmpdi2.
Before summarizing it, verify its 0/1/2 behavior and the caller's operand modes
and branch. Do not import strcmp-like semantics from the word compare. For a
copy-like routine, prove source/destination/length roles independently from
buffer capacities at its callers. Keep a provisional descriptive name when
identity is unresolved; uncertainty about origin need not erase observed facts.

## Prove affected implementation before transferring a vulnerability
Distinguish archive membership, member extraction, surviving output sections,
reachable functions and the executed path. Use
format-dependency-evidence-symbol-resolution for linker and loader distinctions.
For a known issue, locate the changed checks/operations in the actual component;
record possible backports, local changes and missing configuration evidence.

A matching unaffected helper does not date the affected parser. A retained
vulnerable-looking body does not prove the relevant input reaches it. Conversely,
no dynamic import does not rule out a static or header-generated copy. Follow
callbacks, initialization and wrappers without assuming the original library's
public entry point is the only way to reach retained code. Report confirmed
implementation facts separately from candidate vulnerability applicability.

For a proposed fix, use reference-validation-patch-presence-semantic-repair and
playbook-validation-patch-variant-review to distinguish artifact identity,
the corrected operation, exposure restrictions and unresolved related paths.

## Malware attribution: shared library code is not shared operator identity

An implementation match supports code origin only to the extent of the match;
it does not by itself identify an operator, campaign or malicious purpose.
Separate standard-library and compiler-generated routines from application
configuration and behavior before comparing specimens. A shared helper can be
irrelevant to both the suspected vulnerability and the malware's distinguishing
behavior.

Keep the match's address range and uncertainty, then trace the relevant callers.
Do not exclude third-party code from investigation if it supplies the actual
parser, decoder or sensitive operation. Report code similarity, reachable
capability and contextual attribution as different conclusions requiring
different evidence.

## Use reference builds as scoped experiments
If a reference build is authorized and available, record source revision,
patches, target triple, ABI, compiler/linker versions and build flags. Compare
the whole relevant operation, not just a prefix. Account for different layouts,
optimization, inlining and relocated addresses using their actual evidence.

An experiment matching one helper validates that comparison only; it does not
reconstruct the target's complete build history. If exact inputs are unavailable,
state the differing variables and preserve multiple hypotheses. Do not download
or execute unidentified code merely to improve a label. Static parsing of
untrusted objects still needs an appropriately constrained environment.

## Handoff with semantic and provenance confidence separated
Deliver the address range, proposed origin, candidate version set, observed
contract, caller assumptions and unresolved differences. State what evidence
would change the interpretation. Do not suppress investigation of a function
because it is likely third-party or compiler-generated; reduce repetitive
analysis only after its relevant contract and use have been verified.

Data-flow follow-through: playbook-re-sensitive-data-flow. Optimizer and folding
effects: reference-native-compiler-transformations. Keep ordinary helper calls
separate from EH funclets and C++ adjustment thunks described in
reference-native-cpp-lifecycle-unwind and playbook-re-recover-cpp-lifecycle.

## Source basis
Sources reviewed 2026-10-02; the investigation sequence is local synthesis.

- [Ghidra Function ID](https://raw.githubusercontent.com/NationalSecurityAgency/ghidra/master/Ghidra/Features/FunctionID/src/main/help/help/topics/FunctionID/FunctionID.html): matching and ambiguity limits.
- [GCC runtime](https://gcc.gnu.org/onlinedocs/gccint/Libgcc.html) and [integer helpers](https://gcc.gnu.org/onlinedocs/gccint/Integer-library-routines.html): implicit calls and distinct helper contracts.
- [GNU ld options](https://sourceware.org/binutils/docs/ld/Options.html): archive extraction and section retention, not path feasibility.
