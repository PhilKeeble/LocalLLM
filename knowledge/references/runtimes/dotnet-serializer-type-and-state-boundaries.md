---
id: reference-dotnet-serializer-type-and-state-boundaries
title: .NET legacy formatters, Json.NET and data-contract type and state boundaries
kind: reference
topics: [dotnet, deserialization, binaryformatter, newtonsoft-json, data-contracts, type-resolution]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---

# .NET serializer type and state boundaries

## Scope and noninterchangeable serializer families

Reviewed 2026-10-02. Identify the actual library, version, API overload, contract,
converter/binder and deployment before applying a rule. Framework-only types
below do not imply availability on every tagged platform/runtime. Json.NET API
pages inspected identify Newtonsoft.Json 12.0.1; settings guidance is the
publisher's current documentation, not a reproduction of every later release.
System.Text.Json has separate contracts in reference-dotnet-json-contracts.
Workflow: playbook-re-dotnet-deserialization-boundary.

## BinaryFormatter binders do not make untrusted deserialization safe

Microsoft states that BinaryFormatter.Deserialize is unsafe for untrusted input
and cannot be made secure through configuration. Its denial-of-service risks
cannot be eliminated with SerializationBinder; custom binders also do not
provide a general guarantee against other attack categories. The same security
guide warns against SoapFormatter, NetDataContractSerializer, LosFormatter and
ObjectStateFormatter because of unrestricted polymorphic deserialization. [1]

Inference: a binder, authenticated sender or locally stored file is not blanket
evidence of safety. Establish who can influence bytes and the executed sink.
Presence of a dangerous API still does not prove a particular remote-code-
execution path: document reachability, selected implementation and consequence.
Do not enable a disabled formatter or run an unknown payload for inspection.

## BinaryFormatter API presence differs from an active implementation

Starting with .NET 9, in-box BinaryFormatter APIs remain present but throw
PlatformNotSupportedException on use; prior enablement flags no longer restore
that implementation. The unsupported compatibility package can replace it with
a functioning implementation retaining the original risks. [2]

Inference: a metadata reference is not proof that the target executes vulnerable
deserialization. Conversely, a .NET 9+ runtime label is not proof that a separately
supplied compatibility implementation is absent. Inspect loaded assemblies,
package/deployment evidence, actual call resolution and rejection before use.
Earlier Framework/Core enablement behavior needs its own version/configuration.

## NRBF record decoding is not general object activation

NRBF is the .NET Remoting Binary Format used by BinaryFormatter. Decoding its
records and constructing the application types they describe are separate steps.

System.Formats.Nrbf's NrbfDecoder reads serialization records without loading or
instantiating arbitrary custom types. Applications can map a known closed set
of records to their own objects; reintroducing general type loading negates that
separation. TypeNameMatches ignores assembly names and does not validate member
names/types. Record graphs can contain cycles. [3]

Inference: matching a printed type name is not authenticated assembly identity
or complete schema validation. Validate member contracts, array rank/extents,
graph references and resource budgets before constructing an approved domain
object. Reading a record safely does not authorize its requested operation.
For an unknown specimen, preserve bytes and inspect bounded records rather than
calling BinaryFormatter.Deserialize to discover what it contains.

## Json.NET TypeNameHandling controls an activation surface

Json.NET TypeNameHandling uses $type metadata for concrete .NET type selection;
None is the documented default. The publisher requires careful type validation
with a custom ISerializationBinder when using other settings with external data.
Per-property/item settings and metadata handling can alter the effective path. [4]

Inference: Auto is not a security allowlist merely because it emits names only
where runtime and declared types differ. Recover actual accepted types and
assembly instances, including nested values; a friendly display-name check is
not enough. A $type string alone proves neither that metadata is enabled nor
that an attacker can instantiate arbitrary types. A custom converter can supply
another activation path even when the serializer's TypeNameHandling is None.

## Json.NET missing-member policy means unknown input, not absent fields

Json.NET MissingMemberHandling concerns JSON properties with no corresponding
object member; Ignore is the default, Error rejects such input. [5]
The Required enum separately distinguishes AllowNull (presence required, null
allowed), Always (presence required, null forbidden) and DisallowNull (presence
optional, explicit null forbidden); Default is optional. [6]

Inference: MissingMemberHandling.Error does not prove required fields exist.
Recover attribute/contract overrides and distinguish omission from explicit null.
Do not translate these enum values into System.Text.Json settings by name;
their APIs and null/presence enforcement are different contracts.

## Json.NET population and ignored nulls can retain earlier state

Json.NET's default ObjectCreationHandling.Auto can populate existing objects
and add to collections; Replace recreates them. NullValueHandling.Ignore skips
assigning input null. [4]

Inference: a returned object does not prove fresh state. Trace initial values,
property-level overrides and final validation before use. An existing collection
may retain entries absent from the new input. A preserved privilege flag after
an ignored null is only a flaw if it violates the operation's intended semantics.

## Json.NET lifecycle callbacks run application code during reconstruction

Json.NET supports OnDeserializing and OnDeserialized callbacks around object
deserialization. [7]

Inference: inspect the selected callback bodies and their order relative to field
assignment, graph checks and the consumer. A post-Deserialize check cannot prevent
earlier callback effects. A callback's existence does not establish unsafe behavior;
identify its controlled values, reachable calls and resulting state or external
operation. Do not confuse callbacks on one object with completed validation of
every object reachable from it.

## Json.NET handled errors can leave a partially accepted result

Marking Json.NET ErrorContext.Handled can allow deserialization to continue with
successfully processed values. [8]

Inference: trace the installed error handler and which values survive. A logged
conversion error does not prove the caller abandoned the object. Determine whether
missing/rejected members leave defaults, retained state or an incomplete collection,
and whether final validation accounts for that result. Neither exception handling
nor a successful return establishes rollback of earlier setters or callbacks.

## DataContractSerializer differs from NetDataContractSerializer

The documented DataContractSerializer contract does not directly accept CLR
assembly/type names from input as arbitrary activation instructions. Its expected
types and configured known types define the usual deserialization surface;
known types can come from attributes, methods, configuration or constructor
arguments. [9] NetDataContractSerializer instead embeds CLR type identity and
is specifically warned against. [1]

Inference: examine root/member types, known-type providers, custom resolvers and
surrogates rather than equating both class names. An admitted type can still
have side effects; restrictions on type selection do not validate member values
or graph-wide business invariants. Do not apply older Framework loading advice
as modern strong-name authentication; see reference-dotnet-loading-code-identity.

## Data-contract object construction can bypass constructor invariants

Microsoft's DataContractSerializer guidance states that constructors do not
run for most classes during deserialization. Members bound directly to fields
can bypass validation in public property setters; callbacks can validate the
deserialized state, but graph-wide consistency must also be checked. [9]

Inference: for an attributed data-contract class, locate actual DataMember
targets and OnDeserializing/OnDeserialized paths. Constructor defaults or a
validating setter not used by that contract do not prove the reconstructed
object is valid. This is not a universal rule for System.Text.Json, XmlSerializer,
custom factories or every DataContractSerializer-supported programming model.

## Data-contract extension data and quotas are separate boundaries

DataContractSerializer can retain unknown data through IExtensibleDataObject
and re-emit it on a later round trip unless the relevant configuration suppresses
that behavior. Its object-count quota counts array entries but alone does not
bound every object's memory footprint. [10]

Inference: an older endpoint can forward fields it never validated to a newer
consumer. Record extension-data handling and downstream effects. Recover actual
object/reader/transport quotas instead of assuming one count limits bytes,
nesting, external XML resources or processing cost. XML reader/entity policy is
a separate parser contract, not guaranteed by the serializer's class name.


## Sources: formatters and records

1. [BinaryFormatter security guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide): binder limitations and related unsafe serializers.
2. [BinaryFormatter migration](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/): .NET 9 throwing implementation and unsupported compatibility package.
3. [Read NRBF payloads](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-migration-guide/read-nrbf-payloads): records, TypeNameMatches and closed-set reconstruction.

## Sources: Json.NET and data contracts

4. [Json.NET settings](https://www.newtonsoft.com/json/help/html/SerializationSettings.htm): type metadata, null handling and object creation.
5. [MissingMemberHandling](https://www.newtonsoft.com/json/help/html/P_Newtonsoft_Json_JsonSerializerSettings_MissingMemberHandling.htm): unknown input members.
6. [Required enum](https://www.newtonsoft.com/json/help/html/T_Newtonsoft_Json_Required.htm): distinct presence/null requirements, API page version 12.0.1.
7. [Json.NET callbacks](https://www.newtonsoft.com/json/help/html/SerializationCallbacks.htm): lifecycle hooks.
8. [Json.NET error handling](https://www.newtonsoft.com/json/help/html/SerializationErrorHandling.htm): handled errors and continued deserialization.
9. [WCF data security](https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/security-considerations-for-data): DataContractSerializer type selection and construction/graph caveats; Framework-specific context.
10. [Data-contract serialization](https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/serialization-and-deserialization): extension data and object quota limitations; do not infer a universal default quota across API versions.
