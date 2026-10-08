---
id: reference-parser-office-relationships-vba-source
title: Office package relationships, external targets and VBA source boundaries
kind: reference
topics: [parsers, documents, office, opc, relationships, vba, macro-analysis]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Office content selection and VBA source evidence

## Office Open XML parts are connected by relationships

Office Open XML uses ZIP packaging and Open Packaging Conventions (OPC). The
package's [Content_Types].xml identifies part content types. Explicit package/part
relationships are stored in .rels items. A package-level relationship to a main
document, presentation or workbook part identifies the corresponding document
category. [1][2]

Investigative inference: enumerate archive members, declared types and the
relationship graph separately. Do not identify all document semantics from a
filename extension, or assume every member is XML. Compare the graph selected by
the target reader with raw member enumeration; malformed, duplicate or unreferenced
content can make those views differ. ZIP identity/duplicate-member rules belong
in `reference-parser-archive-member-identity`.

## OPC relationship identity includes its owning source

System.IO.Packaging models a relationship from a package or source part to a
target. Its properties include Id, RelationshipType, SourceUri, TargetUri and
TargetMode. Creating or deleting a relationship does not itself modify the
source or target object's content. [3]

Investigative inference: preserve the source and relationship ID together when
joining references. A relationship-type URI labels the relationship; its spelling
alone is not evidence of a network connection. Trace the consumer that selects
the relationship, resolves its target and performs an action. A dangling target
or unknown relationship can be a coverage gap without proving exploitation.

## OPC internal targets resolve against the correct source part

PackUriHelper.ResolvePartUri resolves an internal target using the source part
URI; a source of / designates the package root. Microsoft's example resolves
../picture.jpg from /mydoc/markup/page.xml to /mydoc/picture.jpg. [4]

Investigative inference: retain the owning source when normalizing an internal
target; resolving every relationship from the ZIP root can select different
content. Package URI resolution is not permission to extract to a host filesystem
path. If the application materializes a part, examine the later filesystem mapping,
link handling and destination authority separately.

## OPC External TargetMode does not require an absolute URI spelling

For Package.CreateRelationship, an External target can be absolute or relative;
a relative external target is resolved against the package URI. An Internal
target refers to a part inside the package. These are the package-level API's
rules; do not apply its base blindly to every part-level relationship. [5]

Investigative inference: record TargetMode, source, target spelling and resolved
identity. Relative syntax does not establish that a target stays inside the
archive. For a suspected external fetch, identify the handler, trigger, policy,
credentials and actual destination. A declared external relationship is a lead,
not proof that a network request happened.

## VBA MODULEOFFSET separates cached data from compressed source

In MS-OVBA module streams, MODULEOFFSET gives the byte length of the leading
PerformanceCache; CompressedSourceCode follows it. The cache is implementation-
and version-dependent, and the specification says it must be ignored on read.
Decompressed source uses the project's PROJECTCODEPAGE encoding, not universally
UTF-8. Module stream names come from MODULESTREAMNAME metadata. [6][7]

Investigative inference: recover the selected module stream, validate its source
offset against the actual stream extent, then identify the decompression and
text-decoding steps. Do not scan cache bytes as if they were source text. Preserve
the original cache and source independently; the interchange rule does not
establish every host's execution behavior or prove source/cache equivalence.
Claims of altered cached code or source/execution mismatch need target-specific
evidence, not merely the presence of a cache prefix.

## VBA source recovery is not evidence of macro execution

For a recovered VBA module, follow event/entry selection, reachable calls,
decoded strings, object creation, file/network operations and child-process
requests. Preserve uncertainty about unresolved dispatch and host controls.
Source extraction establishes available text, not whether a particular host
selected it, enabled macros or reached a sensitive operation.

Absence of recovered VBA source is not an exhaustive document safety result.
Record whether the investigation covered embedded objects, external targets,
other interpreters and native parsing/rendering paths. For a vulnerability claim,
connect controlled data to a violated bound or security invariant rather than
treating an automation API or an obfuscated string as the defect itself.

## Sources and scope

Reviewed 2026-10-02. OPC facts use Microsoft's Open XML and System.IO.Packaging
documentation; the URI examples describe those documented contracts. MS-OVBA
module layout is not a complete VBA compiler/cache specification. No claim is
made about current Office macro-policy defaults or all host versions.

1. [About the Open XML SDK](https://learn.microsoft.com/en-us/office/open-xml/about-the-open-xml-sdk): package, content types and relationships.
2. [Packages and document parts](https://learn.microsoft.com/en-us/office/open-xml/general/how-to-add-a-new-document-part-that-receives-a-relationship-id-to-a-package): main-part relationship and document category.
3. [PackageRelationship](https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.packagerelationship?view=windowsdesktop-9.0): source ownership and relationship properties.
4. [ResolvePartUri](https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.packurihelper.resolveparturi?view=windowsdesktop-9.0): source-relative internal target resolution.
5. [Package.CreateRelationship](https://learn.microsoft.com/en-us/dotnet/api/system.io.packaging.package.createrelationship?view=windowsdesktop-9.0): Internal/External and relative target rules.
6. [MS-OVBA module stream layout](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-ovba/c66b58a6-f8ba-4141-9382-0612abce9926): PerformanceCache, MODULEOFFSET and compressed source encoding.
7. [MS-OVBA module stream](https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-ovba/53b1bd2c-050c-4b5e-bf56-de71ae43b58a): MODULESTREAMNAME association.
