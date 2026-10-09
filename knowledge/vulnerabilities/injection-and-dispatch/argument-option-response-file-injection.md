---
id: vulnerability-injection-argument-option-response-file
title: Argument, option, operand, or response-file injection
kind: vulnerability
topics: [injection, arguments, options, response-files, process-creation]
platforms: [cross-platform]
architectures: [any]
---

# Argument, option, operand, or response-file injection

## Definition and violated invariant

Argument injection occurs when attacker-controlled data reaches a child program as one or more arguments but the child interprets it as an unintended option, option argument, operand, response-file directive, configuration source, or subcommand. Correct shell quoting can preserve one argument exactly while leaving this semantic injection intact; the selected program must receive only argument roles and values authorized by the caller.

Argument syntax belongs to the target program. Many POSIX-style utilities use leading hyphens for options and may recognize `--` as the end-of-options delimiter, but conformance and placement must be checked. Some programs expand `@file` or other response-file syntax before ordinary option parsing, and Windows programs choose how to split and interpret their command line.

## Conditions that establish the issue

Recover the process API, exact child executable, raw command line where applicable, resulting argument vector, target option parser, option permutation, end-of-options behavior, response-file or configuration expansion, nested tool invocations, and effective authority. Prove attacker data occupies an unintended semantic role and enables a security-relevant behavior such as writing another path, loading configuration, selecting a plugin, changing an output, or invoking a target feature.

Separate creation-layer tokenization from target-layer interpretation. A safe argument-list API can solve shell tokenization while preserving a dangerous argument value exactly.

## Evidence that is not sufficient

A leading hyphen, `@` prefix, argument-list API, quoting routine, or user-controlled filename is not sufficient. The program may treat the value as an operand because of its position, a prior `--`, an explicit option argument, or its own grammar; it may not support response files or the selected option may have no security effect.

Adding `--` is not a universal conclusion because some tools do not implement that convention or preprocess response files first. Establish the target contract.

## Investigation sequence

Reconstruct the argument vector at the child entry point, preserving empty arguments and exact boundaries. Then emulate the target's parsing stages: response-file expansion, environment/config defaults, subcommand selection, option recognition, option arguments, `--`, operands, and any later nested invocation. Mark which stage first assigns unintended meaning.

At binary level, inspect startup argument parsing and compare branches for option prefixes, long-option tables, response-file markers, and config loaders. Connect the selected branch to an observable operation rather than inferring impact from an option-like string.

## Constructed response-file example

```c
char *argv[] = {"reporter", "--input", submitted_path, NULL};
execve("/opt/tools/reporter", argv, controlled_environment);
```

Assume this specific `reporter` expands any argument beginning with `@` as a response file before it parses `--input`. A submitted value such as `@/shared/job.args` can therefore introduce options even though `execve` receives exactly one attacker-controlled argument and no shell is involved. The finding requires the actual pre-parser expansion and a controllable response file; `@` has no universal command-line meaning.

## Primitive and impact limits

The direct primitive is attacker selection of a target-program argument role or feature. Consequences can include arbitrary file read or write, configuration substitution, output redirection, plugin loading, network access, or a nested command path. Code execution requires that the selected feature reaches an execution-capable behavior; argument control alone is not equivalent to shell command execution.

## Related knowledge and primary sources

Process-creation and prototype references define how arguments reach the child. This profile retains the separate target-parser requirement so shell escaping is not presented as a complete answer.

Reviewed 2026-10-09 against POSIX [Utility Syntax Guidelines](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html), POSIX [`exec`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html), Microsoft [`CreateProcess`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw), and GCC's documented [response-file option](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html). The `reporter` grammar and code are constructed.
