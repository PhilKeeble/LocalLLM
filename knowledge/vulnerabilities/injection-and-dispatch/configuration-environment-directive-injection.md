---
id: vulnerability-injection-configuration-environment-directive
title: Configuration, environment-variable, or directive injection
kind: vulnerability
topics: [injection, configuration, environment, directives, process-creation]
platforms: [cross-platform]
architectures: [any]
---

# Configuration, environment-variable, or directive injection

## Definition and violated invariant

Configuration or directive injection occurs when attacker-controlled data is parsed as configuration structure, directives, variable assignments, includes, substitutions, profiles, or environment-controlled behavior rather than remaining one authorized value. Trusted configuration keys, syntax, precedence, source locations, and process environment must not be created or overridden by lower-authority data.

Configuration grammars and environment consumers are component-specific. Newlines, separators, comments, quoting, interpolation, include syntax, duplicate keys, precedence, and environment-variable meanings differ. An environment variable affects security only when a reachable component consumes it in a security-relevant way under the actual execution context.

## Conditions that establish the issue

Recover every configuration source, grammar, decoding, line and value delimiters, escaping, interpolation, includes, duplicate handling, precedence, defaults, environment inheritance, startup wrappers, privilege transitions, reload behavior, and final consumer. Prove attacker input creates or changes a directive or variable whose interpreted effect crosses the intended authority boundary.

For child processes, bind the constructed environment block to the actual child and establish which variables the child, loader, runtime, or tool honors. Protected or privileged execution modes can ignore or sanitize variables; target evidence is required.

## Evidence that is not sufficient

A writable configuration file, environment variable, newline, key/value builder, include feature, duplicate key, or privileged process is not sufficient. The component may ignore the key, use a later trusted override, parse the input as one escaped value, reject reload, or sanitize the environment before the relevant consumer.

Unexpected configuration does not automatically imply injection; intended administrative customization and unsafe trust-boundary crossing require different evidence.

## Investigation sequence

Build a source-and-precedence table for defaults, files, registry or preference stores, environment, command line, remote policy, and runtime updates. Capture the exact serialized data and final parsed key/value tree, including duplicates, interpolation and includes. Follow the selected value to the operation it changes.

Trace process creation, environment inheritance or replacement, privilege transitions, service managers, containers, and reload generations. At binary level, locate configuration parser calls, key lookup strings, fallback order, and branches that consume the value.

## Constructed line-configuration example

```text
configuration = "output=/srv/reports/result.txt\nreport_title=" + submitted_title + "\n"
write_configuration(job_file, configuration)
launch_worker("--config", job_file)
```

Assume this worker uses newline-delimited `key=value` directives and later duplicates override earlier keys. A submitted title containing a newline plus `output=/shared/attacker-selected` can introduce a second directive and replace the trusted output. The finding requires that exact grammar, duplicate precedence, worker load, and a security-relevant selected path; newline has no universal configuration meaning.

## Primitive and impact limits

The direct primitive is attacker influence over configuration structure or a security-relevant environment-controlled decision. Consequences can include path or endpoint substitution, proxy or credential selection, debug/feature enablement, loader or plugin selection, weakened validation, data disclosure, or execution through a capable directive. Code execution requires a directive or consumer that actually provides it.

## Related knowledge and primary sources

Process-creation, loader-resolution, parser-differential, and authorization references provide adjacent contracts. This profile retains grammar, precedence, consumer, and execution-context requirements locally.

Reviewed 2026-10-09 against POSIX [environment-variable definitions](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap08.html) and [`exec` environment transfer](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html), Microsoft [`CreateProcess` environment handling](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw), and systemd's [environment-variable documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Environment%20Variables%20in%20Spawned%20Processes). The configuration grammar and example are constructed.
