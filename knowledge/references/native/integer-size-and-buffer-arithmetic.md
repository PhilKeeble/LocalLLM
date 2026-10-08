---
id: reference-native-integer-size-buffer-arithmetic
title: Integer conversions and buffer-size arithmetic
kind: reference
topics: [integers, signedness, narrowing, overflow, buffer-sizing, memory-safety]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---

# Integer conversions and buffer-size arithmetic

## Trace values, types, and units

For every security-relevant count preserve its source type/width/signedness and
unit at each operation. Review validation, cast, promotion, multiplication,
addition, alignment, allocation, API parameter conversion, loop/index, and
copy/use. Credit a comparison for a later use only after relating the checked
value to the converted value, intended domain and consumed unit. Representability
is required when the conversion must preserve the original value; intentional
truncation needs its own semantic contract and consistent downstream use. A correct
allocation does not validate a later copy count from another source.

## Widening a result does not widen the preceding operation

In C++, ordinary integer arithmetic uses the promoted/common operand types. Assigning
the result to a wider type does not recover bits lost when multiplication or
addition already overflowed in a narrower type. Signed overflow is undefined
behavior in C++; N-bit unsigned arithmetic is modulo 2^N. Converting a
negative signed value to unsigned can produce a large value; narrowing can
truncate high bits. [1][2] Investigative inference: locate the extension or cast
relative to the arithmetic, not only the final API argument's width. Recover
machine semantics separately if the decompiler's source types are uncertain.

## Evidence needed for a size-flow finding

1. Identify which signed values are valid, including any documented sentinels,
   before interpreting conversion to unsigned.
2. Recover the accepted range in the original domain and unit.
3. Determine whether each conversion preserves the required value or intentionally
   changes it, and which value the consumer actually uses.
4. Trace the widths and overflow conditions of `count * element_size`, headers,
   alignment and terminators; preserve any earlier bounds that rule overflow out.
5. For nonnegative counts in one representable domain and unit, validate
   `offset <= total` then `length <= total - offset`, rather than an
   overflow-prone `offset + length <= total`.
6. Relate the allocation size and consuming range to the validated value. A use of
   the original field needs evidence that it satisfies the same required bound.
7. Account for every boundary whose representation, width or unit changes; an
   adequate earlier proof can protect a later operation without a repeated check.

An absent overflow-check instruction alone is not a finding. Establish a feasible
input and path on which the required relation fails and an invalid operation
follows; a proved input limit or a different consumed value can refute the candidate.

Decompiler types are hypotheses. Confirm security-relevant operand widths and
signed/unsigned branches in instructions or metadata. On Windows, do not assume
`long`, `size_t`, `DWORD`, `ULONG_PTR`, `int`, and managed `long` have matching
widths.

## Checked formulas and subtraction prerequisites

For nonnegative unsigned values in one width with maximum M: addition a+b is
representable when `b <= M-a`; multiplication a*b when b is zero or
`a <= M/b`. For a buffer range, first prove `offset <= total`, then
`length <= total-offset`. Without the first condition, unsigned subtraction can
wrap into a large apparent remainder. These are mathematical checks; recover
the actual promoted operand types before applying them to C/C++ expressions. [1]

## Power-of-two alignment needs a checked addition

For representable nonnegative unsigned n and power-of-two A > 0 in one width
with maximum M, rounding n upward as
`(n + A-1) & ~(A-1)` requires proving `n <= M-(A-1)` before the addition.
The mask formula does not implement general non-power-of-two alignment. Include
header bytes, payload, alignment slack and terminators in the final capacity;
checking individual terms does not prove their sum fits. A valid aligned size
still needs the intended resource limit; representability is not affordability.

## Constructed allocation and use mismatch

Hypothetical unsigned 32-bit count n=0x40000001 and four-byte elements:
32-bit `n*4` yields 4 modulo 2^32. Assigning that result to a 64-bit allocation
argument still requests 4 bytes. A consuming loop using the original n can
attempt many more bytes. Establish that both paths are feasible, that no earlier
bound excludes n, and that the allocation actually succeeds before claiming
the concrete overflow. Wide arithmetic before multiplication would instead
produce 0x100000004, which still needs resource and destination bounds checks.

## Narrowed lengths matter when validation, allocation and use disagree

Constructed example: a 32-bit length 65537 converted to unsigned 16-bit becomes 1.
If allocation uses 1 but copying uses the original length, the mismatch matters.
If all consumers intentionally use the validated narrowed value and its semantic
contract permits that representation, truncation alone is not a vulnerability.
Streaming decompression adds separate declared, available and actually produced
counts; use `reference-parser-decompression-size-memory-limits` for those domains.

## Promotions and mixed signedness change comparisons

For ordinary C++ integer binary arithmetic/comparisons, first apply integral
promotions. With mixed signed/unsigned types: unsigned wins if its rank is at
least the signed rank; otherwise signed wins if it can represent every value
of the unsigned type; otherwise use the unsigned counterpart of the signed type.
Thus negative signed operands can become large unsigned values. [2]

Investigation: for a boundary check, record width, comparison signedness and
which operand was extended. Reason about zero, one, maximal accepted value, next
value and negative inputs where representable. Rejecting negative values is
necessary only when that domain forbids them; sentinels require their documented
meaning. A decompiler's signed type alone does not establish the machine branch.

## C++ shift-count validity differs from CPU count masking

C++ shift counts must be nonnegative and less than the promoted left operand's
width. A CPU instruction that masks its shift count does not make an out-of-range
C++ expression defined. Current C++ signed right shift rounds toward negative
infinity; older language editions have different rules. Evaluate the emitted
instruction independently from source-language assumptions. [3]

## Boundary inputs must survive the representation path

For a recovered limit B, nearby values B-1, B and B+1 probe different sides only
when encoded and decoded as intended. Constructed example: 65536 is outside an
unsigned 16-bit field's range. Truncating it to that field produces zero, not a
test of the consumer receiving 65536. A wider wire field followed by a narrowing
conversion is a different path and can expose an allocation/use disagreement.

Retain the intended value, encoded bytes, decoded value and consuming width.
For malware configuration recovery, the same distinction prevents interpreting
a wrapped count as an intentional command or payload size. Use
playbook-validation-input-selection-mutation for concept-led input selection.

## Sources and verification scope

Reviewed 2026-10-02: current C++ working-draft conversion/arithmetic/shift clauses
and constructed mathematical examples. Not a claim that all historical C/C++
editions share every conversion rule. No target execution was performed.

1. [C++ fundamental integer arithmetic](https://eel.is/c++draft/basic.fundamental) and [integral conversions](https://eel.is/c++draft/conv.integral).
2. [Usual arithmetic conversions](https://eel.is/c++draft/expr.arith.conv).
3. [Shift operators](https://eel.is/c++draft/expr.shift).

## Additional reading

- [C++ type conversions and type safety](https://learn.microsoft.com/en-us/cpp/cpp/type-conversions-and-type-safety-modern-cpp?view=msvc-170)
- [SEI INT30-C: Ensure unsigned integer operations do not wrap](https://wiki.sei.cmu.edu/confluence/display/c/INT30-C.+Ensure+that+unsigned+integer+operations+do+not+wrap)
- [SEI INT31-C: Ensure integer conversions do not result in lost or misinterpreted data](https://wiki.sei.cmu.edu/confluence/display/c/INT31-C.+Ensure+that+integer+conversions+do+not+result+in+lost+or+misinterpreted+data)
