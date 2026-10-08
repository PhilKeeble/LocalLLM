---
id: reference-parser-yaml-tags-construction-aliases
title: YAML tag resolution, loader constructors, aliases and document boundaries
kind: reference
topics: [parsers, deserialization, yaml, pyyaml, tags, aliases, object-graphs]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# YAML representation and object construction

## YAML tag resolution determines value types before application use

YAML tags describe node types. Plain scalars can receive implicit tags through
schema-dependent resolution. In YAML 1.2.2's core schema, recognized true/false
spellings resolve to Boolean, an empty plain scalar to null, and unmatched plain
scalars to strings. Quoted empty text is not the same as null. [1]

Investigative inference: record the parser, selected schema and resulting type,
not just displayed scalar text. A text-level check may disagree with the value
the application receives. Do not transfer YAML 1.2 core resolution to every
installed YAML loader; implementation defaults and custom resolvers can differ.
Explicit tags and application-specific constructors require a separate trace.

## PyYAML SafeLoader restricts default construction, not application extensions

PyYAML safe_load selects SafeLoader, whose default constructors handle standard
YAML types rather than arbitrary Python classes; unsafe_load selects UnsafeLoader.
The constructor registry maps tags to conversion functions. The documented
YAMLObject mechanism can register application classes with SafeLoader, and
custom constructors/resolvers can change the effective conversion path. [2][3]

Investigative inference: establish the actual loader class and registrations
present before the call. A function name containing safe does not prove custom
construction is absent or that returned values meet business rules. Conversely,
do not classify every YAML parse as arbitrary object activation: identify an
accepted tag, reached constructor and controlled arguments. Loader type controls,
resource bounds and operation authorization answer different questions.

## PyYAML aliases can reconstruct shared and cyclic objects

PyYAML supports anchors and aliases for repeated object references, including
recursive structures. An alias is not necessarily a freshly copied subtree. [2]

Investigative model: trace object identity as well as values. A validator that
recurses without cycle handling may fail to terminate; mutation through one alias
can affect another path. A visited set alone is not complete semantic validation
when the same object must satisfy different rules at different paths. Track the
relevant validation context with identity. Bound total work as well as nesting:
repeated traversal of shared subgraphs can be expensive without deep syntax.

## PyYAML registered object construction can bypass __init__

In the inspected PyYAML SafeConstructor implementation, construct_yaml_object
allocates with cls.__new__(cls), then uses __setstate__ if present or updates
the instance dictionary. This helper does not call cls.__init__. [4]

Investigative inference: apply this rule only when the selected registered
constructor reaches that helper. Follow __new__, state restoration and subsequent
consumers; neither a valid YAML node nor an unused validating __init__ proves
the object invariant. Custom constructors can implement different behavior,
including side effects before a later parse or application check fails.

## PyYAML single-document loading differs from lazy multi-document loading

In the inspected PyYAML source, load uses get_single_data; the composer rejects
another document before completing that single-document operation. load_all
instead yields successive objects through a generator. safe_load/safe_load_all
select those paths with SafeLoader. [3][5]

Investigative inference: determine how far a multi-document iterator is consumed.
Obtaining an iterator or consuming one object does not establish validation of
the remaining stream. If the application applies earlier objects before a later
document fails, inspect the surviving state and intended transaction boundary.
Do not infer silent first-document acceptance from the documentation's shorthand
that load parses the first document; the actual single-document path checks for
additional documents.

## Sources and scope

Reviewed 2026-10-02. YAML 1.2.2 supplies the named core-schema rules. PyYAML's
documentation contains historical examples; current main-branch source was
inspected for loader selection, construction and single/multiple-document paths.
These are scoped implementation observations, not a claim about every installed
release, C-backed variant or other language's YAML library.

1. [YAML 1.2.2](https://yaml.org/spec/1.2.2/): section 10.3.2 core tag resolution.
2. [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation): tags, aliases, recursive objects and constructor registration.
3. [PyYAML public entry points](https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/__init__.py): load, load_all, safe_load and unsafe_load.
4. [PyYAML constructors](https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/constructor.py): construct_yaml_object and tag registrations.
5. [PyYAML composer](https://raw.githubusercontent.com/yaml/pyyaml/main/lib/yaml/composer.py): get_single_node and additional-document rejection.
