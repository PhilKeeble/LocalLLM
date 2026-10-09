---
id: vulnerability-injection-uncontrolled-format-string
title: Uncontrolled format string and format-directed memory access
kind: vulnerability
topics: [injection, format-strings, printf, varargs, memory-write, information-disclosure]
platforms: [cross-platform]
architectures: [any]
---

# Uncontrolled format string and format-directed memory access

## Definition and violated invariant

An uncontrolled format-string vulnerability occurs when attacker-controlled text is interpreted as a formatting program rather than supplied as data under a fixed format. A format controls how variadic arguments are fetched and interpreted; conversion specifications can read pointed-to data, consume arguments the caller did not supply, request large output, or use `%n` to store the output count through a pointer argument where that conversion is supported.

Format grammars differ across C libraries, logging frameworks, managed runtimes, localization systems, and custom formatters. `printf`-style conclusions require the actual formatter and conversion support. A fixed format such as `%s` with attacker data as a corresponding argument is a different boundary, though string length and output accounting still require review.

## Conditions that establish the issue

Recover the actual formatter, format-parameter position, attacker control after localization or wrapper expansion, every variadic or structured argument, default promotions, ABI register/stack placement, supported conversions, positional-argument behavior, output destination and capacity, runtime restrictions, and reachable result. Prove the controlled format selects an unintended read, write, allocation, disclosure, or resource effect.

For `%n`, identify the consumed pointer, conversion length modifier, writable target, and output count. If the caller supplied no matching argument, behavior is undefined; a reliable write primitive requires concrete ABI and runtime state rather than the conversion text alone.

## Evidence that is not sufficient

A formatting call, percent character, logger, variadic function, `%n` substring, crash, or attacker-controlled formatted value is not sufficient. The format may be constant, percent signs may be escaped, the formatter may reject `%n`, or the relevant call may be unreachable.

Decompiler prototypes often omit ellipsis arguments or infer incorrect types. Reconstruct the call and ABI before claiming a missing argument or pointer target.

## Investigation sequence

Trace the format string through translations, wrappers, prefix construction, and any second formatting pass. Parse it using the selected formatter's grammar and map every conversion, width, precision, length modifier, and positional selector to the exact promoted argument and ABI location. Follow resulting reads, writes, allocation sizes, truncation, return values, and subsequent sends or logs.

At binary level, recover fixed arguments, the variadic-call ABI state, register-save area or stack arguments, and formatter implementation or import. Treat an uncontrolled call with no extra arguments as undefined until the actual consumed locations are known.

## Constructed C example

```c
void audit_message(const char *submitted_message) {
    printf(submitted_message);
}
```

Conversion specifications in `submitted_message` become the format program. A `%s` can cause the formatter to fetch a pointer-like variadic argument and read through it; `%n` can request a write through a fetched pointer. Because the caller supplied no such arguments, the C behavior is undefined and neither a stable address disclosure nor arbitrary write follows without target-specific evidence.

## Constructed System V AMD64 call shape

```asm
; r12 = submitted_message. For a variadic call, al reports the vector-register count.
mov     rdi, r12                ; attacker-controlled format parameter
xor     eax, eax                ; no vector arguments
call    printf
```

This establishes attacker control of the `printf` format only if `r12` has the proven provenance. It does not identify values later fetched for conversions; recover call-site registers, stack state, libc behavior, and the selected format before claiming a read or write primitive.

## Primitive and impact limits

The direct primitive can be format-directed memory reads, count writes, excessive output, crashes, or disclosure through formatted results. Exploitability depends on supported conversions, available arguments or ABI state, writable/readable targets, mitigations, output visibility, and control flow. Uncontrolled native `printf`-style interpretation can produce memory-unsafe behavior, but a specific arbitrary-write or code-execution claim requires its additional evidence.

## Related knowledge and primary sources

`reference-native-strings-copy-format`, ABI calling-convention references, and output-accounting profiles provide the underlying contracts. This profile repeats `%n`, fixed-format, and missing-argument limits locally.

Reviewed 2026-10-09 against ISO C draft [N1570 section 7.21.6.1](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), GNU libc [output conversion syntax](https://sourceware.org/glibc/manual/latest/html_node/Output-Conversion-Syntax.html), and the System V AMD64 [processor supplement](https://gitlab.com/x86-psABIs/x86-64-ABI). The source and assembly are constructed.
