---
id: vulnerability-external-xml-resource-resolution
title: XML external entity or parser-triggered resource resolution
kind: vulnerability
topics: [xml, external-entity, xxe, external-resource, parser, ssrf]
platforms: [cross-platform]
architectures: [any]
---

# XML external entity or parser-triggered resource resolution

## Definition and violated invariant

This vulnerability occurs when less-trusted XML can make the selected parser or its resolver read a local resource, contact a network endpoint, or include external content outside the consumer's intended resource policy. The invariant is that parsing untrusted content must not resolve external identifiers, schemas, stylesheets, catalogs, or related resources beyond an explicit allowed set and authority.

External resolution is distinct from in-document entity expansion. A document can consume excessive resources without external I/O, and an external fetch can be security-relevant even when expansion is small.

## Conditions that establish the issue

Identify the exact parser, entry API, configuration, document type handling, resolver callbacks, catalogs, base URI, supported schemes, redirects, credentials, network/filesystem namespace, and final resource consumer. Prove attacker-controlled bytes select an external reference and that the effective resolver reaches a protected local object or unintended peer under the parser process's authority.

For blind behavior, establish an observable side effect or controlled destination rather than inferring access from syntax alone. Determine whether the fetched bytes are returned, parsed recursively, used only for validation, or discarded.

## Evidence that is not sufficient

`DOCTYPE`, `ENTITY`, a URL, XML parsing, schema validation, or an error naming an external identifier is not sufficient. The parser may reject document types, disable external general or parameter entities, substitute an empty resolver, use a local trusted catalog, or deny the scheme. A library default from another language or release cannot establish the target configuration.

Do not call exponential internal entity growth XXE unless an external entity or resource is involved; classify its resource effect separately.

## Investigation sequence

Trace raw bytes and base URI into parser creation and every feature/property or resolver assignment. Recover configuration order because later calls can replace earlier controls. Follow external identifiers through URI resolution, redirects, DNS, proxies, file namespaces, and resolver allowlists to the final peer/object.

At binary level, identify parser entry points, callbacks and resource-opening APIs, but confirm their relation to the same parser instance and document. A linked XML library or URL string is only a lead.

## Constructed XML example

```xml
<!DOCTYPE report [
  <!ENTITY ext SYSTEM "file:///protected/config">
]>
<report>&ext;</report>
```

The document is harmful only if the selected XML configuration accepts the declaration, resolves `ext`, permits the `file` resource in the process namespace, and exposes or security-sensitively consumes the result. Replacing the URI with an HTTP target can instead create an outbound-request primitive under the resolver's networking policy.

## Primary sources and scope

Reviewed 2026-10-09 against W3C [XML 1.0 external entity and external identifier rules](https://www.w3.org/TR/xml/), W3C [XML Base](https://www.w3.org/TR/xmlbase/), Java [`XMLConstants.ACCESS_EXTERNAL_DTD` and related properties](https://docs.oracle.com/en/java/javase/25/docs/api/java.xml/javax/xml/XMLConstants.html), and libxml2 [parser option documentation](https://gnome.pages.gitlab.gnome.org/libxml2/html/parser_8h.html). Parser defaults and feature names are implementation-specific; verify the instantiated configuration.
