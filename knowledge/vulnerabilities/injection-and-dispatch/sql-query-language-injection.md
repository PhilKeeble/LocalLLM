---
id: vulnerability-injection-sql-query-language
title: SQL and query-language injection across parameterization boundaries
kind: vulnerability
topics: [injection, sql, queries, databases, parameterization]
platforms: [cross-platform]
architectures: [any]
---

# SQL and query-language injection across parameterization boundaries

## Definition and violated invariant

SQL or query-language injection occurs when attacker-controlled data is incorporated into query syntax and changes the parsed statement, expression, identifier, operator, clause, or command. Data values must be bound through the query engine's parameter mechanism, while dynamic structural elements that cannot be parameters require an explicit closed mapping under the selected query grammar.

Parameterization is API- and position-specific. Host parameters ordinarily represent literal values, not table names, column names, keywords, sort directions, or arbitrary fragments. A prepared statement protects only the values actually bound; concatenated clauses before preparation remain query syntax.

## Conditions that establish the issue

Recover the exact query text reaching preparation or execution, engine and dialect, encoding, statement-boundary behavior, placeholder syntax, bind calls and indexes, dynamic identifiers or clauses, stored procedure construction, escaping mode, connection role, transaction context, and returned or modified objects. Prove attacker-controlled input occupies a syntactic position and changes a security-relevant query operation or result.

For second-order cases, trace stored data back into later query construction. For multi-stage query builders or object-relational layers, recover the final statement and parameter bindings rather than inferring safety from a high-level API name.

## Evidence that is not sufficient

A database call, string concatenation, quote character, prepared statement, stored procedure, unusual query result, or error is not sufficient. Concatenated input may be a validated closed identifier; a parameterized value may be safe; the suspected branch may be unreachable; or the connection may lack the relevant operation.

An error-based response does not by itself establish data extraction or modification. Connect parser control to the claimed database effect and authority.

## Investigation sequence

Reconstruct the final query bytes and a separate binding table containing placeholder, type, length, encoding, lifetime, and value source. Mark all input-derived text that remains in query syntax. Identify statement preparation, reprepare, batch or multi-statement behavior, dynamic SQL inside procedures, and any later query generated from stored values.

At binary level, distinguish prepare calls from bind and step/execute calls, recover lengths rather than assuming termination, and follow error paths and retries. Validate the database identity and effective role before assigning impact.

## Constructed SQLite example

```c
string sql = "SELECT object_id FROM objects WHERE owner = '" + submitted_owner + "'";
sqlite3_stmt *statement = NULL;
sqlite3_prepare_v2(database, sql.data(), (int)sql.size(), &statement, NULL);
sqlite3_step(statement);
```

Here `submitted_owner` becomes SQL source text before preparation, so a quote can change the expression under SQLite's grammar. Preparing the already-concatenated string does not turn that span into a bound value. The finding still requires a reachable input, accepted syntax, the actual connection role, and a security-relevant result.

## Constructed parameter boundary

```c
sqlite3_prepare_v2(database, "SELECT object_id FROM objects WHERE owner = ?1", -1, &statement, NULL);
sqlite3_bind_text(statement, 1, submitted_owner, submitted_length, SQLITE_TRANSIENT);
```

This separates the owner value from SQL syntax under the documented binding API, but it says nothing about other concatenated fragments or dynamic identifiers. Binding length, return codes, statement lifecycle, and any embedded-NUL semantics still require their own review.

## Primitive and impact limits

The direct primitive is attacker control over query syntax or structure. Consequences can include authorization-filter bypass, unintended reads or writes, metadata access, transaction changes, resource exhaustion, or invocation of database features. Operating-system code execution requires an engine feature, extension, external procedure, or other reachable capability and suitable database authority; SQL injection alone does not establish it.

## Related knowledge and primary sources

Parser-differential, string-boundary, authorization, and database-runtime references provide related evidence. This profile keeps value binding and structural query control distinct within the retrieved chunk.

Reviewed 2026-10-09 against SQLite [statement preparation](https://www.sqlite.org/c3ref/prepare.html) and [value binding](https://www.sqlite.org/c3ref/bind_blob.html), and PostgreSQL [prepared statements](https://www.postgresql.org/docs/current/sql-prepare.html) and PL/pgSQL [dynamic command execution](https://www.postgresql.org/docs/current/plpgsql-statements.html#PLPGSQL-STATEMENTS-EXECUTING-DYN). The examples are constructed and engine-specific syntax must be recovered for the target.
