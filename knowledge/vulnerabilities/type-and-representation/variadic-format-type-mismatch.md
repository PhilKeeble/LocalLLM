---
id: vulnerability-type-variadic-format-type-mismatch
title: Variadic argument and format-type mismatch
kind: vulnerability
topics: [varargs, format-strings, calling-convention, type-confusion, memory-safety]
platforms: [cross-platform]
architectures: [any]
---

# Variadic argument and format-type mismatch

## Definition and violated invariant

A variadic type mismatch occurs when a variadic consumer interprets an argument using a type or width different from the promoted value actually supplied. A printf-family format string defines expected argument consumption but cannot change the caller's values. Default promotions apply before ABI placement: ordinary `float` promotes to `double`, and eligible narrow integers promote to `int` or `unsigned int`.

This differs from format-string injection, where an attacker controls the format program. A constant but incorrect format can still read unintended memory, write through `%n`, or corrupt call-state interpretation.

## Conditions that establish the issue

Recover the actual variadic API, trusted or untrusted format, every conversion specification, promoted caller arguments, ABI locations, and consumer behavior. Prove a reachable mismatch causes the callee to fetch an incompatible value or nonexistent argument and that the result reaches a memory access, output, or write.

Account for length modifiers, positional arguments, `*` width/precision arguments, and platform-specific wide-string conventions. Custom loggers need their own grammar.

## Evidence that is not sufficient

A variadic call, format string, register residue, or decompiler omission is not sufficient. The caller may supply matching promoted values, wrappers may transform the format, and unused register contents are not arguments.

An untrusted string supplied under a constant `%s` format is data, not format-string injection, though termination and confidentiality still matter.

## Investigation sequence

Parse the effective format and list arguments in consumption order with required promoted types. Reconstruct the caller's supplied values under the selected ABI, including floating-point metadata and stack alignment. Compare each consumed width and role.

Follow `%s`, `%n`, pointer, and wide-character conversions to their actual memory operations. For output disclosure, identify the observable sink and bytes reached.

## Constructed System V AMD64 example

```c
uint32_t identifier = 0x41414141;
printf("record=%s\n", identifier);
```

The integer argument is supplied where `%s` requires a pointer to a null-terminated character sequence. Under ordinary System V AMD64, the format is in `RDI` and the promoted `uint32_t` value is supplied in `ESI`; the formatter interprets the corresponding argument as an address and scans it. Mapping and termination determine fault versus read; a correct `%u` conversion would consume the integer value instead.

## Primitive and impact limits

The direct result can be invalid read, unintended output disclosure, invalid write through `%n`, or wrong scalar interpretation. Code execution requires an additional controllable write or dispatch chain.

## Related knowledge and primary sources

`reference-native-strings-copy-format` defines format conversions, while `reference-native-prototype-argument-evidence` covers promotions and ABI recovery. This profile repeats caller-versus-consumer comparison locally.

Reviewed 2026-10-09 against C formatted I/O in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), C++ [default argument promotions](https://eel.is/c++draft/expr.call), the [System V AMD64 ABI](https://gitlab.com/x86-psABIs/x86-64-ABI), and [MITRE CWE-686](https://cwe.mitre.org/data/definitions/686.html). The example is constructed.
