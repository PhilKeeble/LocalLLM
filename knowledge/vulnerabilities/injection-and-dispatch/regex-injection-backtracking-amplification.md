---
id: vulnerability-injection-regex-backtracking-amplification
title: Regular-expression injection and attacker-amplified matching work
kind: vulnerability
topics: [injection, regex, redos, backtracking, resource-exhaustion, parsers]
platforms: [cross-platform]
architectures: [any]
---

# Regular-expression injection and attacker-amplified matching work

## Definition and violated invariant

A regular-expression vulnerability occurs when attacker-controlled pattern syntax changes the intended match semantics or when attacker influence over the pattern or subject causes matching work, recursion, memory, compilation, or repeated searches to exceed an authorized budget. Pattern injection and denial of service are related but distinct: a fixed unsafe pattern can be amplified by attacker-controlled subjects, while a controlled pattern can change selection without causing excessive work.

Cost depends on the effective pattern, subject, options, engine, execution path, and wrapper. Backtracking engines can revisit alternatives; automaton-oriented engines may provide different complexity guarantees and feature sets. A timeout or match limit usually scopes one operation rather than all work for a request.

## Conditions that establish the issue

Recover the final pattern after all escaping or concatenation, pattern/subject provenance, selected engine and mode, flags, anchoring, Unicode behavior, compilation and cache lifecycle, subject length, start offsets, global or repeated matching, captures, callbacks, match/depth/heap/time limits, exception/error handling, retries, concurrency, and outer request budget. Prove attacker control changes a security-relevant match or drives work beyond the required bound.

For backtracking amplification, identify the ambiguous or repeated match choices and a reachable failing or late-success path under the actual engine. For pattern injection, identify the unintended operator, grouping, assertion, alternation, character class, or replacement meaning.

## Evidence that is not sufficient

A regex API, nested quantifier, long input, timeout setting, wildcard, user-selected search term, high CPU sample, or match error is not sufficient. Optimizations or another engine may avoid the suspected path, the input may be bounded, or the wrapper may enforce an aggregate deadline.

A linear-time single-match guarantee does not bound repeated matching across many patterns or suffixes. Conversely, an expensive-looking pattern is not proof of exponential behavior in every implementation.

## Investigation sequence

Reconstruct the exact compiled pattern and engine configuration. Mark attacker-controlled pattern and subject regions, then trace compilation, cache keys and eviction, matching entry points, restart positions, replacement processing, exceptions, and retries. Account for pattern length, subject length, pattern count, fields, repeated calls, retained match data, concurrency, and downstream result size.

At binary or managed-code level, distinguish compile from match APIs, JIT from interpreted paths where relevant, and effective per-call controls from defaults. Follow limit errors to see whether incomplete evaluation becomes rejection, ordinary no-match, retry, or acceptance.

## Constructed pattern-injection example

```text
pattern = "^account:" + submitted_name + "$"
if regex_match(pattern, candidate_record):
    authorize(candidate_record)
```

If `submitted_name` is intended as literal text but reaches the regex grammar unescaped, operators such as alternation or grouping can change which records match. The finding requires the engine's actual grammar and an authorization-relevant changed match. Literal-quoting APIs are engine-specific and must cover the whole intended literal span.

## Constructed work-amplification example

```text
pattern = "^(a+)+$"
subject = attacker_supplied_bytes
matched = backtracking_engine.match(pattern, subject)
```

A long run of `a` followed by a nonmatching byte can force some backtracking engines to explore many partitions before failure. This is not a universal complexity claim: optimizations, engine choice, limits, and input bounds can change the result and must be recovered from the target.

## Primitive and impact limits

The direct primitive can be unintended match selection, validation or authorization bypass, excessive CPU, stack or heap use, cache growth, or worker starvation. Service-wide denial requires reachable workload, concurrency and resource impact beyond one bounded call. Memory corruption requires a separate implementation defect.

## Related knowledge and primary sources

`reference-parser-regex-work-limits` contains PCRE2, RE2, and .NET control distinctions. This profile repeats the fixed-pattern versus controlled-pattern and per-call versus aggregate-budget distinctions locally.

Reviewed 2026-10-09 against PCRE2 [performance](https://www.pcre.org/current/doc/html/pcre2perform.html) and [API](https://www.pcre.org/current/doc/html/pcre2api.html) documentation, RE2's [syntax and complexity scope](https://github.com/google/re2), and Microsoft [.NET regular-expression timeout](https://learn.microsoft.com/en-us/dotnet/api/system.text.regularexpressions.regex.matchtimeout). The examples are constructed; actual work requires the target engine and configuration.
