---
id: vulnerability-memory-truncation-invalidates-later-bound
title: Truncated copy or conversion invalidating a later bound
kind: vulnerability
topics: [memory-safety, truncation, formatting, encoding, length]
platforms: [cross-platform]
architectures: [any]
---

# Truncated copy or conversion invalidating a later bound

## Definition and violated invariant

This vulnerability occurs when a copy, formatter, or encoder stores only a bounded prefix but later code treats the required, requested, or pre-conversion length as the initialized output length or assumes an omitted terminator exists. The later consumer must use a length that is within the bytes or code units actually produced and within the destination object.

Truncation alone is not necessarily memory unsafe: it may be an explicit result state. The defect arises when the program fails to preserve that state and a later read, write, parse, send, or comparison relies on a stronger length or completeness assumption.

## Conditions that establish the issue

Recover the producer's precise success, failure, truncation, return-value, and termination contract. Identify the capacity unit and distinguish required output from stored output. Prove a feasible truncated result reaches a consumer using a count beyond the initialized range, scanning for a missing terminator, or making a security decision on a semantically incomplete value.

For encoding conversion, track input bytes or code units, output units, substitution policy, and actual returned count. Expansion ratios are encoding and input dependent; an input character count is not automatically an output-byte capacity.

## Evidence that is not sufficient

A bounded function, a return value equal to capacity, or a visibly shortened string is not sufficient. The caller may reject truncation, the API may always terminate successful nonzero-capacity output, or the next consumer may intentionally use only the stored prefix.

Do not transfer return semantics between similarly named runtimes. Resolve the actual import, wrapper, flags, and error conventions, especially for formatting and platform conversion APIs.

## Investigation sequence

At the producer call, label input extent, output capacity, return value, actual initialized count, and termination state. Follow every branch that classifies the result and every later use of both the return value and destination. Look for signed error values converted to unsigned counts and for time-of-check changes between sizing and conversion calls.

In assembly, recover which register or stack slot preserves the return value and whether the consumer receives that value, the capacity, or a recomputed length. Relate conditional branches to the documented truncation predicate rather than inferring success from a nonnegative result alone.

## Constructed source example

For C99-style `snprintf`, a nonnegative return is the number of characters that would have been written excluding the terminator; when it is at least the nonzero capacity, the stored output is truncated:

```c
void emit_path(const char *base, const char *name)
{
    char output[32];
    int required = snprintf(output, sizeof output, "%s/%s", base, name);
    if (required < 0)
        return;
    send_bytes(output, (size_t)required);
}
```

If `required >= 32`, `send_bytes` receives a count larger than the object even though `snprintf` bounded its own write. The direct result is an over-read only if that send path reads the full supplied count; rejecting `required >= sizeof output` would refute it.

## Constructed call-site representation

This architecture-neutral pseudodisassembly focuses on dataflow because variadic call registers differ by ABI:

```asm
call snprintf
test return_value, return_value
js   format_failed
zero_extend length_arg, return_value
address     data_arg, output_buffer
call send_bytes
```

The relevant omission is a branch for `return_value >= capacity` before using the required length as a readable count. Confirm the resolved formatter follows the stated return contract and the later callee consumes exactly that count; a wrapper may translate either behavior.

## Primitive and impact limits

The direct primitive may be an out-of-bounds read, unterminated scan, later out-of-bounds write, or semantic use of a truncated identifier or path. Record which result occurs rather than treating every truncation as memory corruption.

Disclosure requires the excessive read to reach an observable sink. Authorization bypass or file confusion requires evidence that validation and use interpret different complete or truncated values. Code execution needs a further control-bearing corruption chain.

## Related knowledge and primary sources

`reference-native-strings-copy-format` defines formatting and termination contracts, and `reference-native-text-encoding-size-units` defines conversion units. This profile repeats the required-versus-stored distinction required to assess the issue independently.

Reviewed 2026-10-09 against C `snprintf` in [WG14 N1570 section 7.21.6.5](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), [GNU libc formatted-output semantics](https://sourceware.org/glibc/manual/latest/html_node/Formatted-Output-Functions.html), Microsoft [WideCharToMultiByte](https://learn.microsoft.com/en-us/windows/win32/api/stringapiset/nf-stringapiset-widechartomultibyte), and [MITRE CWE-170](https://cwe.mitre.org/data/definitions/170.html). The example and pseudodisassembly are constructed.
