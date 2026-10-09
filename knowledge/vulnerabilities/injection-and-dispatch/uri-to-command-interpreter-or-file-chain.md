---
id: vulnerability-injection-uri-to-command-interpreter-file-chain
title: URI-to-command, interpreter or filesystem injection chain
kind: vulnerability
topics: [uri-schemes, command-injection, argument-injection, interpreters, filesystem]
platforms: [windows, linux, macos, ios, android]
architectures: [any]
---

# URI-to-command, interpreter or filesystem injection chain

## Definition and violated invariant

A URI-to-command or file chain exists when externally controlled URI data crosses into a command language, argument vector, interpreter, loader or filesystem operation without preserving the intended data boundary. The invariant is that decoded URI components remain data for one defined consumer and cannot change executable selection, argument structure, command grammar or the resolved filesystem object beyond the authorized scope.

URI activation is the entry mechanism, not the final vulnerability type. Classify the decisive transition as command injection, argument injection, unsafe file selection, path traversal, handler confusion or another specific condition.

## Conditions that establish the issue

Prove external control of a URI component, every decoding transformation, the exact string or object passed to the next consumer, that consumer's grammar, and a feasible input that changes interpretation or selects a forbidden object. For command execution, identify executable selection, argument construction, shell or interpreter involvement and the target program's argument parser.

For file chains, identify the final decoded path, base directory, namespace, link or mount traversal, canonicalization timing, access mode and application or parser that consumes the file. A validated extension, MIME label or URI prefix does not establish final object identity.

## Evidence that is not sufficient

A command-line string, quoted placeholder, `ShellExecute`, `CreateProcess`, `system`, file URI or percent-decoding call is not sufficient. Separate argument APIs can preserve boundaries, a downstream program may treat metacharacters as data, the handler may reject malformed input, or filesystem policy may constrain resolution.

Do not assume one quoting rule applies to Windows process creation, a C runtime's `argv` parser, POSIX shells, PowerShell, `cmd.exe`, scripting languages and application-specific option parsers. Recover the actual consumer chain and apply each grammar once.

## Investigation sequence

Start with the raw activation URI and record component parsing before decoding reserved octets. Trace repeated decoding, Unicode and path normalization, concatenation, quoting and delimiter insertion. At every boundary, write down the intended data item and the grammar that will consume the produced representation.

For a process path, recover whether the API receives an explicit executable plus argument array, an executable plus mutable command-line string, or text evaluated by a shell/interpreter. Trace option terminators, response files, environment expansion and working directory only when the target supports them. For a file path, continue through final handle creation and object identity rather than stopping at string comparison.

## Constructed interpreter example

This platform-neutral pseudocode assumes `run_via_shell` evaluates its argument using a command-language grammar:

```text
on_uri_activation(uri):
    value = percent_decode(parse_uri(uri).query["file"])
    command = "viewer --open " + value
    run_via_shell(command)
```

The path is command injection only if external input reaches `value`, the selected shell recognizes attacker-controlled syntax in that position, and execution reaches an unintended command or argument. If `viewer` and `value` are passed as separate arguments to a non-shell API and the viewer does not reinterpret `value`, this constructed shell-injection conclusion does not apply.

## Constructed filesystem example

```text
on_uri_activation(uri):
    relative = percent_decode(parse_uri(uri).path)
    candidate = join(application_data_root, relative)
    open_with_registered_handler(candidate)
```

The issue requires a feasible value that resolves outside the authorized root or selects an unintended handler/object after all normalization and link traversal. Textual `application_data_root` prefixing is not final-object proof, but neither is a `..` substring proof of escape when the path API rejects or confines it.

## Binary and call-site evidence

At a native call site, recover parameter roles from the applicable ABI and API prototype before interpreting adjacent strings. A call to `ShellExecute` may invoke a registered verb or extension; a call to `CreateProcess` has different executable and command-line rules; a shell-launch helper adds another parser. Inspect the actual callee and values, not an import name alone.

Managed IL or bytecode often preserves calls to URI parsers, string builders and process APIs more clearly than final JIT assembly. Use native assembly only when interop marshalling, truncation or a native helper materially changes the boundary.

## Primitive and impact limits

The direct primitive may be altered arguments to a fixed executable, command-language evaluation, opening an unintended local file, or dispatching a file to an unsafe handler. These have different authority and impact. An injected option is not automatically arbitrary command execution; prove what the target option enables.

Privilege escalation requires the receiving process or downstream handler to have greater authority and the selected operation to use it. Remote code execution requires remote reachability plus a demonstrated execution path. Do not infer either from a custom scheme registration alone.

## Related knowledge and primary sources

`reference-activation-uri-handler-selection-delivery` owns handler selection, `reference-parser-escaping-nul-url-layers` owns decode ordering, and filesystem and process references own platform-specific resolution. This profile keeps the decisive cross-grammar chain local.

Reviewed 2026-10-09 against [RFC 3986 sections 2-3](https://www.rfc-editor.org/rfc/rfc3986.html), Microsoft [`ShellExecuteW`](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shellexecutew) and [`CreateProcessW`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw) documentation, and the [POSIX shell command language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html). Both examples are constructed and intentionally omit payload strings.
