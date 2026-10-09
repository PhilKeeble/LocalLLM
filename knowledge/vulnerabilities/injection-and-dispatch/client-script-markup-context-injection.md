---
id: vulnerability-injection-client-script-markup-context
title: Client-side script or markup injection from output-context mismatch
kind: vulnerability
topics: [injection, xss, html, javascript, markup, output-encoding, browsers]
platforms: [cross-platform]
architectures: [any]
---

# Client-side script or markup injection from output-context mismatch

## Definition and violated invariant

Client-side script or markup injection occurs when attacker-controlled data is parsed as active HTML, SVG, CSS, JavaScript, URL, event-handler, or another browser grammar instead of remaining inert content in the intended output context. Encoding or sanitization must match the exact parser state and every later DOM or script sink; one generic HTML-escape operation is not valid for all contexts.

HTML text, quoted and unquoted attributes, URL-valued attributes, style content, script strings, JavaScript template literals, JSON embedded in HTML, SVG, and DOM parsing APIs have different delimiter and execution rules. Browser policies such as Content Security Policy or Trusted Types can constrain consequences but do not change which grammar a sink parses.

## Conditions that establish the issue

Recover the response or DOM construction path, character encoding, HTML insertion context, attribute quoting, entity decoding, URL parsing, script and CSS parsing, sanitizer configuration, DOM sink, event or navigation trigger, origin, frame, CSP and Trusted Types policy, and reachable application capabilities. Prove attacker data crosses into active syntax and causes a security-relevant DOM change, script execution, navigation, request, or user-interface effect.

For DOM-based cases, trace sources and transformations in the client rather than assuming the server response contains the final syntax. For stored cases, retain the storage-to-render path and affected origin.

## Evidence that is not sufficient

Reflected text, angle brackets, an `innerHTML` call, a script-looking substring, sanitizer, CSP header, or changed DOM is not sufficient. The data may be inserted as text, the parser context may keep it inert, the sink may reject it, policy may block the relevant execution path, or the resulting markup may have no security effect.

Do not claim script execution merely because a `script` element appears in markup inserted through a particular API; insertion and execution rules depend on the sink and construction path. Trace the actual trigger.

## Investigation sequence

Capture bytes at the response and the DOM sink, then identify the parser state at the exact insertion point. Build a context chain through URL/JSON/template decoding, HTML tokenization, attribute parsing, DOM construction, and any later script, style, or URL evaluation. Record encoding or sanitization applied at each transition and whether it is valid for the next grammar.

Map origin, frame, document lifecycle, policy headers, nonces or hashes, event triggers, navigation, and exposed native/web bridges. Connect any execution to the victim origin and reachable data or action before assigning impact.

## Constructed attribute-context example

```javascript
card.innerHTML = '<img src="placeholder" alt="' + submitted_caption + '">';
```

If `submitted_caption` can close the quoted `alt` value and add another attribute, the HTML fragment parser can create attributes the caller did not intend. An event-handler attribute could become an execution path only if the browser accepts it in this context, the event fires, and policy permits it. Using the same bytes with `textContent` would invoke a text-node contract instead of HTML parsing.

## Primitive and impact limits

The direct primitive is attacker control over active client-side syntax or DOM structure in an affected origin or embedded application. Consequences can include script execution, credentialed requests, data access, navigation, UI deception, or native-bridge calls. Impact depends on origin, frame isolation, policy, available credentials, user interaction, and exposed capabilities; markup injection alone is not proof of script execution.

## Related knowledge and primary sources

URI, parser-layer, browser-origin, and native-web-bridge references provide supporting contracts. This profile repeats output-context and actual-trigger requirements locally.

Reviewed 2026-10-09 against the WHATWG HTML [parsing model](https://html.spec.whatwg.org/multipage/parsing.html) and [dynamic markup insertion APIs](https://html.spec.whatwg.org/multipage/dynamic-markup-insertion.html), the DOM [`textContent` contract](https://dom.spec.whatwg.org/#dom-node-textcontent), Content Security Policy [Level 3](https://www.w3.org/TR/CSP3/), and the W3C [Trusted Types specification](https://www.w3.org/TR/trusted-types/). The example is constructed and its conditional execution limits are explicit.
