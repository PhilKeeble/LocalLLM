---
id: reference-jvm-serialization-filters
title: Java ObjectInputFilter decisions, composition, installation and coverage limits
kind: reference
topics: [jvm, java, deserialization, serialization-filters, allowlists, resource-limits]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# Java deserialization filters

## Scope and no-default-filter distinction

Reviewed 2026-10-02 against JDK 25 contracts. General Java serialization filtering
is not enabled merely because the runtime supports it. Application/subsystem
configuration must be established; subsystem filters are not proof that every
ObjectInputStream is protected. [1]

This document is specific to Java Object Serialization, not a global policy for
JSON/XML/data-binding libraries. Construction/graph facts:
reference-jvm-serialization-construction-and-graphs. Workflow:
playbook-re-jvm-deserialization-boundary. Separate documented guarantees from
target-specific behavior and the application's actual effective configuration.

## UNDECIDED permits continuation; null status does not

For ObjectInputStream filtering, REJECTED, a null returned status or a thrown
RuntimeException causes InvalidClassException; ALLOWED and UNDECIDED permit
continuation. [2]

Investigation: distinguish no installed filter from an installed filter returning
null. An allowlist-shaped predicate that returns UNDECIDED for everything else
does not reject those classes by itself. ALLOWED is a filter decision, not proof
that class resolution, graph restoration or application authorization succeeds.
Recover the entire composed decision before classifying any individual result.

## Pattern ordering and syntax can change the effective allowlist

Config patterns are semicolon-separated with significant whitespace. Limits
(maxdepth/maxrefs/maxbytes/maxarray) are checked first; duplicate limits use the
last value. Class rules use the first match; no match yields UNDECIDED. [3]

Constructed example: `demo.Safe;!*` allows a matching demo.Safe class and rejects
other matching class names; `!*;demo.Safe` rejects it first. Neither expression
validates field contents or creates callbacks where the filter is not invoked.
Preserve exact configured bytes and order, not a prettified list with inserted
spaces. A later restrictive rule does not override an earlier class match.
Decode actual startup/programmatic configuration before testing the pattern.

## Array, package and module patterns are not arbitrary Java predicates

Pattern arrays match their base element type regardless of dimensions. `p.*`
covers that package, `p.**` includes subpackages, and a terminal `*` otherwise
matches a name prefix. `module/name` also constrains the module. [3]

Investigation: distinguish array element allowlisting from array length limits
and total graph size. `demo.*` does not restrict input to one data-transfer object
(DTO) type,
and module membership is not proof that every member type is suitable input.
Name/module patterns do not express arbitrary loader identity or inheritance
policy. For a custom predicate, inspect its actual Class checks instead of
assuming it implements the pattern grammar. Keep defining loaders with class
identity when same-named definitions matter.

## merge is reject-dominant, not a requirement that both filters allow

ObjectInputFilter.merge short-circuits a first rejection; either rejection wins,
otherwise either ALLOWED wins, otherwise the result is UNDECIDED. [4]

Constructed decision: ALLOWED merged with UNDECIDED becomes ALLOWED, not rejection.
Two incomplete allowlists therefore do not automatically produce their
intersection. Conversely, an explicit rejection cannot be overridden by an
allow from the other merged filter. Inspect side effects and ordering in custom
combiners; do not apply merge's contract to code that merely has a similar name.
The JDK 17+ helper's availability is separate from old runtime behavior.

## rejectUndecidedClass has explicit null-class and array exceptions

The JDK 17+ wrapper preserves decided results. For UNDECIDED, null class stays
UNDECIDED; nonarray classes reject. Primitive-base arrays stay UNDECIDED;
reference-base arrays are accepted only if rechecking the base type allows it. [4]

Investigation: it is not a blanket conversion of every undecided event into
rejection. Ensure resource-limit checks still run for reference-only callbacks
and primitive arrays. Do not infer a primitive-array size limit from wrapping a
class predicate. When diagnosing a rejected array, keep both array and base-type
decisions rather than assuming only one filter invocation occurred.

## The filter factory controls replacement versus composition

The built-in factory installs the JVM-wide filter at stream construction;
setting a stream filter replaces it, rather than automatically merging it.
A custom factory can compose filters. Factory installation is once-only and
must precede creation of any ObjectInputStream. [3]

Investigation: a JVM-wide setting is not proof it remains effective on a stream
whose owner sets its own filter. Preserve current, requested and returned filter
at the actual factory call. Context-selected policy must correspond to the
operation's real thread/caller/loader context, including asynchronous work and
stream reuse. Because installation is process-wide and once-only, a later
configuration string is not evidence that an already-created stream changed
policy. Reconstruct the effective factory and its installation outcome.

## Configuration presence is not successful timely installation

System properties override corresponding security properties during Config
initialization. Later System.setProperty calls do not install either filter or
factory. [3] setObjectInputFilter is once-only before object reads; its resulting
filter cannot change an existing nonnull filter to null. [2]

Investigation: record startup values, initialization order, setter outcomes and
getObjectInputFilter's effective result, not just a string found in configuration.
Inspect caught configuration exceptions: a logged attempt is not evidence that
the desired policy took effect. Do not interpret a nonnull returned filter as
proof it retains all restrictions of the prior policy; inspect its decisions.

## Strings and field values are outside ordinary class-filter coverage

ObjectInputStream does not call the filter for primitives or concretely encoded
strings. It checks arrays with requested lengths, proxy classes/interfaces and
nonnull readResolve/resolveObject replacements. [2]

Investigation: a class allowlist cannot by itself validate string contents,
numeric ranges, tenant relations or permitted operations. Replacement rejection
occurs after the code producing that replacement has run; do not infer prevention
of all earlier effects. A proxy interface name is not the complete callback path.
Trace nested deserializers independently; their streams and libraries may have
different filtering rules. A final object cast is later than reconstruction.

## Filter metrics are not a complete transport or resource budget

FilterInfo can have null serialClass; arrayLength is an element count or -1,
depth begins at 1, and streamBytes is implementation-specific and need not align
with the object causing the callback. [5]

Investigation: returning early for null class can skip reference/size checks.
A maxbytes decision runs only at applicable filter callbacks, not at every
underlying read; it is not an independent bounded transport reader. Array count
does not directly equal heap bytes, and graph metrics do not bound arbitrary
callback CPU, external I/O or decompression before ObjectInputStream. Preserve
independent byte/time/allocation budgets and their enforcement locations. Verify
reset/reuse accounting on the exact target rather than inferring it from handles.

## Primary sources and inspected sections

1. [Java serialization filters, JDK 25](https://docs.oracle.com/en/java/javase/25/core/java-serialization-filters.html): configured versus default filtering and stream/JVM scope.
2. [ObjectInputStream](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputStream.html): get/setObjectInputFilter, rejection and callback coverage.
3. [ObjectInputFilter.Config](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputFilter.Config.html): initialization, factory behavior, installation and createFilter syntax.
4. [ObjectInputFilter](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputFilter.html): merge and rejectUndecidedClass contracts and availability.
5. [FilterInfo](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/io/ObjectInputFilter.FilterInfo.html): null class, element count, depth and streamBytes qualifications.
