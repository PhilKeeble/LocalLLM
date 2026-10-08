---
id: reference-parser-regex-work-limits
title: Regular expression backtracking, matching engines and resource limits
kind: reference
topics: [parsers, regex, redos, pcre2, re2, dotnet, resource-exhaustion]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Regular expression work and limits

## Backtracking cost depends on the pattern, input and engine

Backtracking revisits earlier matching choices when a later condition fails.
PCRE2 documents nested indefinite repetitions as a source of excessive work,
especially on failing matches. Its optimizations can reject some such inputs
without exploring the full search tree. [1]

Investigative inference: recover the effective pattern after escaping or dynamic
assembly, options, subject length, start offset and actual matching engine.
A suspicious repetition is a candidate, not proof of exponential execution in
every build. A fixed application pattern can be expensive on attacker-controlled
text even when the attacker cannot supply the pattern. Successful examples alone
do not characterize the failure path. Imports or embedded patterns do not prove
the relevant call is reachable.

## PCRE2 match limits are work counters, not whole-request deadlines

In interpreted pcre2_match, the match limit counts main matching-loop iterations;
for unanchored matching it restarts at each candidate subject position. Reaching
it returns PCRE2_ERROR_MATCHLIMIT. JIT matching also uses the limit, with different
counting. [2]

Investigative inference: a value described as a match limit is not milliseconds,
and does not by itself cap repeated calls by the wrapper. Record how many
positions, fields and patterns the application examines. Follow the exact error
branch: converting a resource-limit result to ordinary no-match can hide incomplete
scanning; treating it as validation success can accept unchecked input. Neither
consequence follows merely from the library returning an error.

## PCRE2 depth and heap controls do not describe every matching path

PCRE2's depth limit restricts nested backtracking in interpreted pcre2_match,
but is ignored for JIT matching. The heap limit is measured in KiB and does not
apply to JIT matching. Pattern LIMIT settings can lower corresponding caller
limits, not raise them. [2]

Investigative inference: establish whether this match actually uses JIT,
interpretation or pcre2_dfa_match before crediting a configured control. A JIT
support flag or successful compilation of another pattern is not sufficient.
Keep compile-time costs, match workspace, subject storage and application-retained
results separate. Do not infer an application-wide memory cap from one context.

## PCRE2 compilation and retained match storage have separate lifetimes

PCRE2 documents expansion of groups with bounded repetition in compiled patterns. In its
10.41-and-later described interpreter, backtracking storage is retained with the
match-data block for reuse; lowering the heap limit does not shrink a block
already retained. [1]

Investigative inference: account for simultaneous compiled patterns and pooled
match-data objects, not just one call's temporary allocation. Trace whether
untrusted pattern variations bypass cache reuse or whether eviction frees the
associated storage. A large persistent block can be an intentional reuse policy;
an exhaustion claim needs reachable growth or an unaffordable retained bound.
Do not apply these interpreter storage details to JIT or historical PCRE1.

## RE2 linear matching does not bound an application's total matching work

RE2 documents matching time linear in subject length, with constants affected by
pattern complexity. It budgets parser/compiler/engine memory and avoids recursive
execution; it does not support every backtracking-engine feature. [3]

Constructed model: matching K independent fixed patterns against N-byte text can
still require work proportional to K*N. Repeatedly searching overlapping suffixes
can add further work. This is a wrapper cost model, not an allegation about RE2's
single-match guarantee. Recover pattern count, compilation frequency, application
loops and retained captures. A linear-time engine removes one class of growth,
not input-size, concurrency or output-accounting obligations.

## .NET Regex timeout is approximate and scoped to matching

Regex.MatchTimeout is an approximate maximum interval for one matching operation;
the engine throws RegexMatchTimeoutException at a subsequent timing check.
InfiniteMatchTimeout disables timeout. Effective configuration can come from an
explicit timeout or the application-domain default. [4]

Investigative inference: inspect the selected overload/instance and effective
default rather than assuming every .NET regex times out. Follow exception handling,
retry counts and any increase to the timeout. A timeout is incomplete evaluation,
not proof that the input would never match. A per-operation timeout does not
bound a sequence of matches, compilation or work performed outside the engine.

## Sources and scope

Reviewed 2026-10-02. PCRE2 API and performance documentation, RE2 upstream README,
and Microsoft .NET 10 API view. PCRE2's performance page is dated 2022 and explicitly
describes relevant 10.30/10.41 transitions; do not infer all target internals from
rolling documentation. Investigative models are constructed, not measured results.

1. [PCRE2 performance](https://www.pcre.org/current/doc/html/pcre2perform.html): compilation, retained frames and failing matches.
2. [PCRE2 API](https://www.pcre.org/current/doc/html/pcre2api.html): match-context resource controls and matching paths.
3. [RE2 upstream](https://github.com/google/re2): safety goals and complexity guarantee.
4. [Regex.MatchTimeout](https://learn.microsoft.com/en-us/dotnet/api/system.text.regularexpressions.regex.matchtimeout?view=net-10.0).

Workflow: playbook-re-algorithmic-resource-boundary.
