---
id: vulnerability-integer-extension-negative-sentinel-confusion
title: Sign extension, zero extension, and negative-sentinel confusion
kind: vulnerability
topics: [integers, sign-extension, zero-extension, sentinels, error-handling]
platforms: [cross-platform]
architectures: [any]
---

# Sign extension, zero extension, and negative-sentinel confusion

## Definition and violated invariant

Extension confusion occurs when a narrow bit pattern is widened with the wrong signed interpretation or when a documented negative sentinel is converted into a large count, index, timeout, or identifier. Sign extension repeats the narrow sign bit; zero extension inserts zero high bits. Neither operation establishes what the producer meant.

The invariant is that status/sentinel classification occurs in the producer's domain before conversion, and ordinary values are widened according to the selected contract.

## Conditions that establish the issue

Recover producer return or field type, documented sentinel values, branch width and signedness, extension instruction, destination type, and consumer. Prove a feasible sentinel or high-bit-set ordinary value is misclassified and reaches a security-relevant operation.

Distinguish `-1` meaning error, infinite, not found, scan-to-terminator, or all entries. The same bit pattern has different semantics at different APIs.

## Evidence that is not sufficient

`MOVSX`, `MOVZX`, a value of all ones, or conversion to `size_t` is not sufficient. The widened interpretation may be required, a prior status branch may remove the sentinel, or all-ones may be a valid mask.

Do not treat upper register bits as proof of a declared narrow type when the ABI leaves them unspecified.

## Investigation sequence

Start at the producer and list every success, partial, and error result. Track the raw bits through storage, extension, comparisons, arithmetic, and the final parameter. Identify whether the error check occurs before or after conversion and whether it tests the same width.

At call boundaries, confirm result register rules and any wrapper translation. Inspect both sign- and zero-extended interpretations of high-bit-set boundary values, then retain only values feasible under the producer contract.

## Constructed source and assembly example

This hypothetical receive routine returns `-1` on error, but the caller converts it to an unsigned copy count without checking:

```c
int received = receive_bytes(source, capacity);
size_t count = (size_t)received;
memcpy(destination, source, count);
```

On a 64-bit target, conversion of signed `-1` to `size_t` produces the maximum value. Architecture-neutral binary dataflow can appear as `call receive_bytes; sign_extend copy_count, return_value; call memcpy`; a signed negative-result branch before extension would reject this sentinel. Recover saved destination and source arguments under the actual ABI rather than assuming they survive the first call in volatile registers.

## Primitive and impact limits

The direct primitive is a semantic change during widening or sentinel handling. It can create an oversized operation, infinite wait, invalid object selection, or fail-open state, depending on the consumer.

An API may reject the large result before use. Memory corruption, authorization bypass, or disclosure requires the complete downstream chain.

## Related knowledge and primary sources

`architecture-machine-representation` defines extension behavior, while `reference-native-resource-lifetimes-api-results` covers result validity. This profile repeats the producer-domain requirement needed independently.

Reviewed 2026-10-09 against [MITRE CWE-195](https://cwe.mitre.org/data/definitions/195.html), [MITRE CWE-681](https://cwe.mitre.org/data/definitions/681.html), C conversions in [WG14 N1570](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), and C++ [integral conversions](https://eel.is/c++draft/conv.integral). The source and assembly are constructed.
