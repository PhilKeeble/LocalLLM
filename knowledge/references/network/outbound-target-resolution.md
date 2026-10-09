---
id: reference-network-outbound-target-resolution
title: Outbound URL parsing, redirects, name resolution and final destination
kind: reference
topics: [urls, outbound-requests, redirects, dns, proxies, destination-identity]
platforms: [cross-platform]
architectures: [any]
---

# Outbound URL parsing, redirects, name resolution and final destination

## A URL string is not the final network destination

An outbound request can pass through input decoding, URI parsing, scheme-specific processing, proxy selection, host name resolution, address selection, connection establishment, redirects and connection reuse. Record each representation and decision. Validation of the submitted text does not establish the scheme, authority, address or peer ultimately used by the client.

RFC 3986 defines generic components as scheme, authority, path, query and fragment, but an individual scheme and client define dereferencing behavior. A parser result is therefore evidence only for that parser and stage. Compare the components used by the security decision with those consumed by the request implementation.

## Parse before decoding component data

RFC 3986 requires significant components and subcomponents to be separated before percent-decoding reserved octets; decoding first can turn data into delimiters. It also warns against decoding the same string more than once. A validator and client that apply different grammars or decoding order can disagree about authority, path or embedded credentials.

For investigation, preserve raw input, each decoded value, parsed scheme, user information, host, port, path, query and fragment. Determine whether backslashes, Unicode host labels, IPv6 literals, empty ports and scheme-relative references have special meaning in the actual parser. Do not import browser-oriented WHATWG rules into a non-browser client without evidence.

## Redirects create a new target decision

HTTP redirect responses carry a `Location` URI-reference that a client may resolve against the current target. Whether the client follows it, which method it uses next, how many hops it permits and whether it forwards credentials are client and status-code dependent. A check performed only on the initial URL does not authorize a different redirect destination.

Record every hop's parsed authority, resolved addresses, selected connection and response. A redirect to the same textual host can still resolve differently; a relative redirect can change path and query without changing authority. Conversely, presence of a `Location` header does not prove the client followed it.

## Name resolution and connection evidence

A host name can yield multiple address records, and clients may try more than one. Address policy must cover every address family and representation the connector accepts, including IPv4, IPv6 and any mapped form normalized by the actual API. A DNS answer observed at validation time does not prove the later connection used that answer if resolution occurs again or cached state changes.

The connected socket peer is strong evidence for the network endpoint, but a configured forward proxy makes that peer the proxy rather than the logical URL authority. Record proxy use, tunnel establishment, TLS server identity, connection reuse and application authority separately. No single field proves all layers of destination identity.

## Schemes and non-network effects

Generic URI parsing does not restrict a client to HTTP or HTTPS. Depending on registered handlers and client features, another scheme can address local files, IPC, mail, application activation or a different network protocol. Establish the accepted scheme and actual handler before claiming a network request or local-file access.

Likewise, fetching an internal response is not automatically disclosure: prove what response data or side effect becomes observable to the requester. Timing, status and error differences may form narrower oracles, but each requires demonstrated distinguishability and attacker control.

## Primary sources and scope

Reviewed 2026-10-09 against [RFC 3986 sections 2-3](https://www.rfc-editor.org/rfc/rfc3986.html), [RFC 9110 HTTP semantics and redirection](https://www.rfc-editor.org/rfc/rfc9110.html), [RFC 1034](https://www.rfc-editor.org/rfc/rfc1034.html) and [RFC 1035](https://www.rfc-editor.org/rfc/rfc1035.html) for DNS concepts, and [MITRE CWE-918](https://cwe.mitre.org/data/definitions/918.html) for the SSRF weakness boundary. Client-specific parsing, proxy, resolver, redirect and connection-reuse behavior must be established for the investigated implementation.
