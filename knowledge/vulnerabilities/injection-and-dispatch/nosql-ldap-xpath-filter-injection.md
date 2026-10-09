---
id: vulnerability-injection-nosql-ldap-xpath-filter
title: NoSQL, LDAP, XPath, XQuery, or directory-filter injection
kind: vulnerability
topics: [injection, nosql, ldap, xpath, xquery, filters, directories]
platforms: [cross-platform]
architectures: [any]
---

# NoSQL, LDAP, XPath, XQuery, or directory-filter injection

## Definition and violated invariant

Filter or query injection occurs when attacker-controlled data becomes operators, paths, predicates, attribute names, function calls, or other syntax in a NoSQL query, LDAP filter, XPath/XQuery expression, or directory lookup. Values intended as data must be encoded or bound under the exact selected grammar, and attacker-controlled structured objects must not gain query operators or override trusted constraints.

These languages are not interchangeable. LDAP search-filter escaping differs from LDAP distinguished-name encoding; XPath string-literal rules differ from XML escaping; a document database's structured query operators and JavaScript-capable features depend on the actual driver and server. Apply only the target grammar.

## Conditions that establish the issue

Recover the engine, protocol and dialect, API overload, raw string or structured query object, parse and binding stages, escaping routine, attribute and identifier selection, namespace and function environment, implicit type conversion, server-side features, account authority, and returned objects. Prove attacker input acquires syntactic meaning or overrides a trusted query constraint and changes a security-relevant result or operation.

For structured NoSQL input, trace deserialization and merge behavior so operator keys, nested objects, arrays, nulls, and type changes remain visible. For LDAP, distinguish a search filter from a distinguished name and bind/authentication operation.

## Evidence that is not sufficient

Special characters, a JSON object, filter construction, LDAP/XPath API, escaped text, or unusual result is not sufficient. The API may bind variables, use a typed builder, reject operators, escape under the correct grammar, or apply an independent authorization filter that cannot be overwritten.

A broad query result does not establish injection without the attacker-controlled parse or merge path. Query capability also does not establish server-side code execution.

## Investigation sequence

Capture the final expression or structured query plus a provenance map for each node. Identify grammar, string-literal and escape rules, variable binding, operator recognition, attribute or path resolution, namespaces, functions, merge order, and trusted constraints. Compare what the caller intended as a value with what the engine parsed.

Trace connection identity, directory base or collection, scope, aliases/referrals where relevant, result handling, and later object-level authorization. At binary boundaries, recover API prototypes and distinguish text expressions from precompiled or structured query objects.

## Constructed LDAP-filter example

```c
string filter = "(&(objectClass=person)(uid=" + submitted_uid + "))";
ldap_search(connection, base_dn, subtree_scope, filter);
```

RFC 4515 assigns syntactic meaning to parentheses, `*`, backslash, and NUL in the string representation of LDAP search filters. If `submitted_uid` reaches this position without assertion-value escaping, it can terminate or extend the intended equality filter. The finding requires actual filter construction, accepted syntax, and a changed directory result; distinguished-name escaping is a different contract.

## Constructed structured-query merge example

```text
trusted_filter = { tenant_id: current_tenant, status: "visible" }
final_filter = merge(trusted_filter, submitted_filter)
results = collection.find(final_filter)
```

If the merge permits attacker keys or nested operators to replace `tenant_id`, change `status`, or introduce a broader logical expression, the submitted object controls query structure rather than one value. The finding requires the actual merge and driver semantics; accepting a structured filter can be intentional when equivalent authorization is enforced elsewhere.

## Primitive and impact limits

The direct primitive is attacker control over query structure or trusted constraints. Consequences can include authentication or authorization-filter bypass, unintended search scope, data disclosure or modification, expensive queries, or invocation of exposed query functions. Code execution requires a separately reachable engine feature or host callback with suitable authority.

## Related knowledge and primary sources

Schema, duplicate-field, parser-differential, and authorization references provide supporting contracts. This profile keeps each query grammar separate and requires the parsed operation to be recovered.

Reviewed 2026-10-09 against [RFC 4515](https://www.rfc-editor.org/rfc/rfc4515.html) for LDAP search-filter strings, [RFC 4514](https://www.rfc-editor.org/rfc/rfc4514.html) for the distinct distinguished-name string form, W3C [XPath 3.1](https://www.w3.org/TR/xpath-3/), and MongoDB's [query and projection operators](https://www.mongodb.com/docs/manual/reference/operator/query/). The examples are constructed and do not assert one grammar for all NoSQL systems.
