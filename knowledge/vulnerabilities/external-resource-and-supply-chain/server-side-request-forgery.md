---
id: vulnerability-external-resource-server-side-request-forgery
title: Server-side request forgery and outbound-target confusion
kind: vulnerability
topics: [ssrf, outbound-requests, urls, redirects, dns, network-boundary]
platforms: [cross-platform]
architectures: [any]
---

# Server-side request forgery and outbound-target confusion

## Definition and violated invariant

Server-side request forgery occurs when a less-trusted requester can cause a server-side component to send a request to a destination or resource outside the authority intended for that feature. The invariant is that every accepted scheme, authority, resolved address, port, redirect target and final resource remains within the permitted destination set under the credentials and network position used by the requester component.

The direct primitive is server-originated interaction with an unintended target. Disclosure, internal service access, state change, credential exposure and remote code execution are separate consequences that require their own evidence.

## Conditions that establish the issue

Prove attacker influence over a URL or equivalent destination input, a reachable server-side fetch, inadequate restriction of the destination actually used, and interaction with a forbidden target. Trace raw input through decoding, parser components, scheme handling, proxy selection, name resolution, address choice, connection reuse and every followed redirect.

Identify the server's network reachability and credentials. A target inaccessible to the original requester may be reachable from the server, but that topology must be established. If the response is not returned, determine whether timing, status, content length or a target-side state change is observable before claiming blind SSRF impact.

## Evidence that is not sufficient

An HTTP client call, user-supplied URL, internal-looking hostname, DNS lookup or redirect support is not sufficient. A closed destination allowlist, connector-level address policy, outbound proxy policy or final-peer validation may constrain the path. A parser accepting `file:` or another scheme does not prove the selected client dereferences it.

Do not classify ordinary open redirect in the server's response as SSRF unless the server itself follows or issues the attacker-directed request. Likewise, a failed connection demonstrates an attempted destination only when the failure can be tied to the resolved target and request path.

## Investigation sequence

Recover the entry field and every preprocessing stage. Record parsed scheme, user information, host, port, path, query and fragment under the actual URL library. Trace allow/deny decisions and compare their representation with the one passed to the client. For host names, record all accepted address families, resolution times and addresses attempted.

Follow redirect policy hop by hop, including relative `Location` resolution, scheme changes, credential forwarding and maximum hops. Identify proxy and connection-pool behavior: the connected socket may lead to a proxy, while reused connections can decouple a later logical authority from a fresh DNS lookup. Confirm the final logical target, peer and resource effect.

## Constructed request example

This pseudocode validates only the initial scheme and then follows redirects without reapplying destination policy:

```text
target = parse_url(request.url)
if target.scheme not in {"http", "https"}:
    reject
response = http_client.get(target, follow_redirects = true)
return response.body
```

The path is vulnerable only if a reachable requester can make the initial or redirected request reach a forbidden destination and obtain an unauthorized effect. An HTTP(S)-only check is not a destination policy. Conversely, a client hook that validates every resolved address and redirect under an adequate allowlist can refute this constructed path.

## Destination chain

```text
submitted representation
  -> decoded URL
  -> scheme and authority
  -> proxy decision
  -> host resolution and candidate addresses
  -> selected connection or reused connection
  -> request target and credentials
  -> redirect Location and next-hop resolution
  -> final peer/resource
  -> response or side effect visible to requester
```

Keep logical authority, DNS answer, socket peer and TLS identity separate. With a forward proxy, the socket peer is the proxy; with a tunnel, both proxy and tunneled destination matter. Textual host equality alone does not prove the same resolved destination across hops.

## Primitive and impact limits

The direct primitive can be a request to an internal service, a different tenant endpoint, a local handler, or an unintended external host. Report method, headers, body control, credentials, response visibility and repeatability. Port scanning requires a distinguishable oracle; sensitive data exposure requires returned or otherwise observable data.

Remote code execution requires a vulnerable reachable target or a stronger protocol/action chain and cannot be inferred from SSRF alone. Cloud or service credentials are exposed only if the request reaches a credential-bearing endpoint and the result becomes usable by the attacker.

## Related knowledge and primary sources

`reference-network-outbound-target-resolution` owns URI, redirect, DNS, proxy and peer distinctions. `reference-parser-escaping-nul-url-layers` owns decoding disagreements. This profile repeats the full target chain because the destination used, not the submitted string, decides SSRF.

Reviewed 2026-10-09 against [MITRE CWE-918](https://cwe.mitre.org/data/definitions/918.html), [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html), and [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html). Client-specific parser, resolver, proxy, redirect and connection-reuse behavior remains an implementation question.
