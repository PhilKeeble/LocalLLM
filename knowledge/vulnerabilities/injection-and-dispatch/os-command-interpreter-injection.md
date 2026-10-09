---
id: vulnerability-injection-os-command-interpreter
title: OS command injection through shell or command-interpreter syntax
kind: vulnerability
topics: [injection, commands, shell, process-creation, interpreters]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# OS command injection through shell or command-interpreter syntax

## Definition and violated invariant

OS command injection occurs when attacker-controlled data reaches a shell or command interpreter as syntax and changes the commands, expansions, redirections, pipelines, substitutions, or control operators that are executed. Data intended as one literal operand must remain data under the exact interpreter grammar and every preceding decoding or interpolation layer.

Shell syntax is interpreter-specific. POSIX shells tokenize, parse, expand, redirect, and execute under their own rules; Windows command interpreters and scripting hosts use different grammars. A process-creation API does not imply a shell, but wrappers, batch files, `system`-style functions, or explicit interpreter arguments can introduce one.

## Conditions that establish the issue

Recover the exact execution API, executable or interpreter, command string or argument vector, working directory, environment, wrapper layers, decoding and expansion order, quoting routine, and effective identity. Prove attacker-controlled characters occupy a syntactic position in the selected interpreter and produce a reachable command or interpreter effect beyond the intended fixed operation.

If a program constructs a command string but invokes an executable directly, distinguish target-program argument interpretation from shell interpretation. If the executable itself embeds an interpreter, follow that later boundary.

## Evidence that is not sufficient

A command string, metacharacter, process launch, shell import, quoting function, or privileged process is not sufficient. The input may never reach an interpreter, may be supplied as a literal argument under a correct contract, or may be constrained to a grammar position where the characters have no syntactic meaning.

Escaping for one shell, quoting context, or decoding stage does not prove safety in another. Conversely, suspicious characters do not establish execution without the actual parser and branch.

## Investigation sequence

Trace input bytes through decoding, validation, formatting, environment expansion, wrapper APIs, interpreter startup, and final command parsing. Reconstruct the complete command and mark trusted syntax separately from attacker-controlled spans. Identify whether the input is parsed as a command name, word, option, redirection target, script source, variable expansion, or nested interpreter string.

At binary level, recover the callee prototype and arguments at the process-creation or interpreter call. Follow builders and format operations backward; an imported `system` or process API without a reachable attacker-controlled call site is capability evidence only.

## Constructed POSIX-shell example

```c
char command[1024];
snprintf(command, sizeof command, "analyze --input '%s'", submitted_name);
system(command);
```

If `submitted_name` can contain a single quote followed by shell syntax, it can terminate the intended quoted word and introduce additional syntax. The finding requires actual truncation handling, the `system` call, attacker control, and a syntactically valid interpreter path. The quote characters in the format string are not an escaping algorithm.

## Constructed x86-64 call shape

```asm
; Illustrative System V AMD64 shape after command construction. r12 = command buffer.
mov     rdi, r12
call    system                  ; one interpreter command string, not an argv array
```

This call shape identifies an interpreter boundary; it does not reveal which bytes are attacker-controlled, whether construction truncated, or whether a reachable command is introduced. Recover the buffer data flow and platform's `system` contract before concluding injection.

## Primitive and impact limits

The direct primitive is attacker influence over interpreter syntax and therefore over one or more commands or interpreter operations. Impact depends on reachable syntax, executable availability, sandboxing, environment, filesystem access, credentials, and process identity. Command injection in an unprivileged isolated worker does not itself establish host or privilege escalation.

## Related knowledge and primary sources

`reference-windows-process-creation-context`, native argument references, and interpreter evidence references provide process and call-boundary detail. This profile keeps the necessary shell-versus-direct-execution distinction local.

Reviewed 2026-10-09 against POSIX [Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html), [`system`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/system.html), and Microsoft [`CreateProcess`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw). The source and assembly are constructed; no one quoting rule is asserted for all interpreters.
