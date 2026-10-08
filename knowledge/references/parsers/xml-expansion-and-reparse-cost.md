---
id: reference-parser-xml-expansion-reparse-cost
title: XML entity expansion, external resolution and incremental reparsing costs
kind: reference
topics: [parsers, xml, expat, entity-expansion, xxe, algorithmic-complexity, resource-exhaustion]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# XML expansion and reparsing cost

## XML entity expansion is not bounded by nesting depth alone

XML entity replacement can multiply data through nested references. Repeating a
large entity many times can also produce large expanded text without deep nesting.
Python's XML security documentation distinguishes these expansion mechanisms. [1]

Constructed model: an L-byte replacement referenced R times contributes L*R
replacement bytes before any later processing. Distinct limits on declaration
size and nesting do not imply a small product. Follow effective expansion policy,
expanded-byte accounting and callback behavior, not just input-file length.
Malformed XML is not required for resource abuse: grammar acceptance and resource
policy are different questions. Avoid labeling every large valid document an attack.

## XML external entity resolution is a different authority boundary

Expat itself does not, by default, open local files or initiate network connections.
[1] External resource effects require the wrapper/resolver path to be established.

Investigative inference: trace entity declarations to registered handlers, URI
resolution, access policy and actual file/network calls. Disabling network fetches
does not necessarily disable internal entity expansion; expansion limits do not
authorize external reads. For malware analysis, preserve the requested resource
and subsequent data use: a URI in a document is not evidence that a request ran,
and a parser's external resolver is not inherently malicious. Deferred package
relationships and other resource loaders can have separate policies.

## Expat entity amplification is a ratio with an activation threshold

Expat's entity protection calculates (direct+indirect)/direct after an activation
threshold of output bytes. Direct means primary-document bytes; indirect includes
entity expansion and external DTD bytes. The root-parser setters
XML_SetBillionLaughsAttackProtectionMaximumAmplification and
XML_SetBillionLaughsAttackProtectionActivationThreshold report success/failure.
They were added in 2.4.0. [2]

Investigative inference: a ratio setting alone is not a fixed total-output limit.
Recover both effective controls, build support, checked setter results and the
application's cumulative storage. A separate parse per embedded document can
restart local accounting while a caller keeps all results. The protection's name
does not establish limits on callbacks, object graphs or downstream rendering.

## Expat unfinished tokens can cause repeated scanning

Expat's reparse deferral waits for substantial new input before retrying an
unfinished token, avoiding quadratic rescanning across incremental calls.
XML_SetReparseDeferralEnabled, added in 2.6.0, can disable that behavior. [2]

Investigative inference: preserve input fragment sizes and parser configuration
when reasoning about cost; equal final bytes need not imply equal processing
history. A wrapper that repeatedly creates a new parser and reparses the whole
accumulated prefix has its own cost, independent of one parser's deferral.
Do not infer a current vulnerability solely from an Expat import or from a
historical issue name; identify the effective implementation and selected path.

## Expat allocation tracking is not a whole-process memory budget

Expat 2.7.2 added allocation-amplification controls. Documented exclusions include
application XML_MemMalloc/XML_MemRealloc calls, the main input buffer and returned
content-model memory. [2]

Investigative inference: count application nodes, retained text, queued callbacks
and external buffers separately. A SAX-style callback parser can stream input
while its consumer still constructs an unbounded tree. For a rejected document,
inspect whether callbacks already committed effects or retained allocations.
A protection failure establishes incomplete processing, not an empty or harmless
document. Related output/window distinctions:
reference-parser-decompression-size-memory-limits.

## Sources and scope

Reviewed 2026-10-02. Python 3.14.8 XML security guidance and Expat's latest API
documentation. Named introductions explain materially different protection paths;
they are not a claim that a release number alone establishes safety. Expat build
features, wrappers and application callbacks require target evidence.

1. [Python XML security](https://docs.python.org/3/library/xml.html#xml-security): expansion forms and default Expat external-I/O behavior.
2. [Expat API](https://libexpat.github.io/doc/api/latest/): entity amplification, reparse deferral and allocation tracking/exclusions.

Workflow: playbook-re-algorithmic-resource-boundary.
