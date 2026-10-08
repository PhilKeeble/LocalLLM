---
id: reference-dotnet-json-contracts
title: System.Text.Json binding, construction and validation contracts
kind: reference
topics: [dotnet, system-text-json, deserialization, validation, polymorphism, object-graphs]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# System.Text.Json contracts

## Scope: recover the actual serializer and options

Reviewed 2026-10-02. These are System.Text.Json rules, not Newtonsoft.Json or
BinaryFormatter defaults. Record loaded library version, reflection versus
generated contract, declared root type, options, resolver modifications and
converters. Version labels below describe documented feature introductions;
package-provided libraries can differ from the host runtime's in-box version.
Newer API availability is not evidence that an older target enables that check.
Workflow: playbook-re-dotnet-deserialization-boundary. Other serializers:
reference-dotnet-serializer-type-and-state-boundaries.

## Required presence and non-nullability are separate checks

System.Text.Json required members must occur in the JSON; missing required
members cause JsonException. C# required, JsonRequired and contract metadata
JsonPropertyInfo.IsRequired express presence requirements. A contract resolver
can modify that metadata. [1] Presence does not by itself prohibit explicit null;
required and non-nullable are independent concepts. [2]

Inference: inspect the effective contract, not only an attribute or a decompiled
non-nullable property. Distinguish absent, explicit null, empty and valid values
separately. A present empty string or zero identifier can still violate a
business invariant. Successful binding is not authorization to use that field.

## Non-optional constructor parameters were not always required input

Before .NET 9, System.Text.Json constructor binding treated parameters as
optional input, supplying defaults when absent. .NET 9 introduced opt-in
RespectRequiredConstructorParameters to require non-optional parameters;
a runtime feature switch can also supply its default. [1]

Inference: a C# constructor signature such as Request(string name, int count)
does not alone prove that JSON lacking name/count is rejected. Recover the
selected constructor, library version and effective option. Parameter presence,
nullability and the constructor's own semantic checks are different evidence.
Do not assume upgrading the runtime retroactively enables an opt-in policy.

## Nullable enforcement has a limited, versioned scope

.NET 9 introduced opt-in RespectNullableAnnotations. Its enforcement covers
supported non-generic member/constructor annotations, not root-level reference
types, collection element nullability or generic member annotations. It does
not make an omitted member required. [2]

Inference: List<string> is not proof that a null element is rejected, even when
the option is enabled. Check root null, missing members, explicit nulls and
elements independently. Annotation metadata cannot substitute for a validation
branch. Custom converters and contract changes require their own trace rather
than an assumption that one options flag validates the entire object graph.

## Constructor selection and wire names are different bindings

For ordinary System.Text.Json class binding, an available public parameterless
constructor is used by default; a sole public parameterized constructor can be
used, and JsonConstructor selects a constructor. Constructor parameter names
must match actual property names/types, with case-insensitive name matching,
even when JsonPropertyName changes the wire name. In .NET 7 and earlier,
JsonConstructor support is restricted to public constructors. [3]

Inference: follow the selected constructor, property assignments and generated
contract, not a guessed source initialization path. Non-public construction and
source-generation capabilities vary by library version. A property renamed
to wire key user_id can still bind to constructor parameter userId matching
the CLR property UserId, not to an arbitrary parameter named user_id.

## Unknown properties are not missing required properties

Default System.Text.Json ordinary object (POCO) binding ignores JSON properties
that do not map to the contract. .NET 8 introduced UnmappedMemberHandling.Disallow, configurable
through options, type attributes or contracts, to reject unmapped properties. [4]

Inference: rejecting unknown input does not require all expected properties,
and requiring expected properties does not reject unknown ones. Recover any
extension-data/custom-converter path before concluding that an extra field is
discarded. Unknown fields forwarded to another consumer can acquire meaning
there; preserve the exact input and downstream representation.

## General and web defaults need not match property names the same way

System.Text.Json general deserialization defaults use case-sensitive property
matching. PropertyNameCaseInsensitive=true changes binding; web defaults are
case-insensitive. [5]

Inference: compare the exact options at a validator and consumer. A document
object model (DOM) check for one spelling does not establish what a
case-insensitive object binder later
accepts. Naming policy, JsonPropertyName, property matching and constructor-name
binding are separate mechanisms. A helper using fresh general options can
disagree with the application's web-configured entry path.

## Duplicate property lookup does not prove unique input

JsonElement.GetProperty uses ordinal case-sensitive name matching and returns
the last matching definition when the object contains duplicates. [6]
System.Text.Json 10 introduced AllowDuplicateProperties=false for serializer
options, and separately for JsonDocumentOptions, to reject duplicates. [7]
The serializer option's default is true. [8]

Inference: a successful GetProperty or final object value is not evidence that
the input contained that property only once. Compare validators that enumerate
or take the first occurrence against consumers taking the last. The serializer
option does not automatically configure an independent DOM parse. For custom
converters, prove what duplicate checks actually run. Preserve original bytes:
reserializing the final object can erase evidence of the disagreement.

## Custom converters change which validation code runs

System.Text.Json selects a property-level JsonConverter before the options
Converters collection, then a type-level attribute; in the collection, the
first applicable CanConvert wins. Built-in conversion is used only if no custom
converter applies. [9]

Inference: locate the actual selected converter for each nested value and check its type
selection, reader advancement, coercion and side effects. Do not assume built-in
member validation governs a converter that constructs the object itself.

## System.Text.Json null can bypass a custom converter's Read

For reference and nullable value types, System.Text.Json normally bypasses custom
Read for null; overriding HandleNull=true opts into handling it. [9]

Inference: a null rejection inside Read may never run on the default null path.
Recover the converter's target type and effective HandleNull before crediting that
branch. Presence requirements and non-nullability checks are separate contracts;
finding a converter does not establish either. Do not apply this reference/nullable
rule to every non-nullable value-type converter.

## Polymorphic discriminators are configured mappings, not arbitrary CLR names

System.Text.Json's .NET 7+ polymorphism supports opted-in derived types through
JsonDerivedType/JsonPolymorphic and the contract model. A discriminator maps
input to a configured derived type; merely serializing derived members without
a discriminator does not establish round-trip derived-type reconstruction. [10]

Inference: $type in this mechanism is not automatically Newtonsoft.Json's CLR
type-name resolution. Recover the actual mapping, fallback/error options and
custom converters before claiming arbitrary type loading. An allowed type can
still contain unsafe setters or violate operation-specific rules; type selection
is neither complete graph validation nor authorization.

## System.Text.Json Populate does not clear existing collections

System.Text.Json 8+ Populate behavior reuses collection properties without
clearing them; JSON elements are added to existing elements. Mutable object
properties can be updated while their object reference remains the same. [11]

Inference: do not assume deserialization replaces preexisting privileges or
clears stale collection entries. Recover initial state, the selected creation
mode, assignments and final checks. A newly supplied collection element does not
establish that previously stored elements disappeared. The rule has type and
construction restrictions; identify whether Populate actually applies.

## System.Text.Json reference preservation reconstructs identity, not copies

ReferenceHandler.Preserve uses reference metadata to reconstruct object
identity/cycles for supported reference types, not simply equal value copies. [12]

Inference: do not assume deserialization creates a tree of independent objects.
Check the selected reference mode and aliases: mutation through one path can
affect another. Graph-wide
invariants, cycle-safe validation and state reset are separate checks. These
features have type restrictions; do not generalize reference preservation to
every immutable type, array or value type.

## Syntax acceptance and depth are not complete resource validation

System.Text.Json rejects comments/trailing commas by default; options can allow
them, and NumberHandling can permit quoted numeric values. [13] MaxDepth=0 means
an effective depth limit of 64, not unlimited depth; exceeding it throws
JsonException. [14]

Inference: valid syntax and bounded nesting do not bound total bytes, string
length, collection width, converter work or allocation. Compare number types
and coercion options at each consumer, and trace transport/decompression limits
separately. Establish which limits the reachable path enforces; a depth check
alone says nothing about a shallow, very wide collection. A parser exception
also does not prove earlier setter or converter side effects were rolled back.



## Sources: binding and validation

1. [Required properties](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/required-properties): IsRequired and .NET 9 constructor option.
2. [Nullable annotations](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/nullable-annotations): opt-in scope, omissions and limitations.
3. [Immutable types and construction](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/immutability): constructor selection/name matching; newer preview-specific extensions are not assumed.
4. [Unmapped members](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/missing-members): default skip and .NET 8 Disallow.
5. [Character casing](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/character-casing): general versus web defaults.
6. [JsonElement.GetProperty](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonelement.getproperty?view=net-10.0): ordinal matching and last duplicate.
7. [.NET 10 library changes](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/libraries): separate serializer/document duplicate controls.

## Sources: converters, state and limits

8. [AllowDuplicateProperties](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonserializeroptions.allowduplicateproperties?view=net-10.0): default true and rejection behavior.
9. [Custom converters](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/converters-how-to): precedence and HandleNull.
10. [Polymorphism](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/polymorphism): .NET 7+ opt-in mapping/discriminators.
11. [Populate initialized properties](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/populate-properties): .NET 8+ reuse without clearing.
12. [Preserve references](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/preserve-references): identity, cycles and type restrictions.
13. [JSON acceptance options](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/invalid-json): comments, trailing commas and quoted numbers.
14. [MaxDepth](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.jsonserializeroptions.maxdepth?view=net-10.0): zero sentinel and depth failure.
