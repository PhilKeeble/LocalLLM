---
id: reference-native-floating-validation
title: Floating-point NaN, infinity, rounding and unsafe numeric validation
kind: reference
topics: [floating-point, nan, infinity, rounding, precision, numeric-validation]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Floating-point validation

## Scope and representation first

Use when binary floating values influence a size, index, quota, deadline,
geometry bound or policy comparison. Identify format, operation precision,
rounding mode, exception handling and compiler math options. The following
NaN examples assume ordinary IEEE-style unordered comparisons with execution
continuing; enabled traps or optimized finite-only assumptions can change the
executed path. [1,2]

Keep raw bits and decoded value together. A printed decimal string can conceal
rounding, signed zero or NaN payload differences. Distinguish integer comparisons
on raw bits from floating comparisons on decoded values.

## NaN defeats some rejection-style range checks

NaN is unordered: ordinary equality with itself is false, and ordered less/
greater comparisons are false. [1] Constructed example: rejecting only when
`x < 0 || x > limit` can let NaN through. Accepting only a finite value within
the intended range expresses a different condition. GNU libc isfinite rejects
both NaN and positive/negative infinity; isnan alone does not reject infinity. [3]

Investigation: determine whether a parser accepts special numeric spellings,
whether raw binary input can encode them, or arithmetic can generate them.
Then inspect the emitted unordered/ordered branch behavior and downstream use.
An apparent missing NaN check is not a finding if an earlier proven invariant
excludes NaN, or the domain intentionally supports it without unsafe consequences.

## Float-to-integer conversion needs a representability proof

C++ conversion from floating point to an integer type other than bool discards
the fractional part. If the truncated value is not representable in the destination
integer type, behavior
is undefined; conversion is not a portable saturation or modulo operation. [4]
Rejecting NaN alone is insufficient: infinity and out-of-range finite values
also need handling before conversion. Conversion to bool instead tests zero
versus nonzero under its separate language rule; do not apply an integer-size
representability check to that Boolean conversion. [6]

Constructed investigation: a length is checked against an integer maximum
converted to floating type. If that maximum rounds upward, `x <= converted_max`
may admit a nonrepresentable integer result. Establish the comparison constant's
actual bits, destination width and conversion instruction. Validate the final
allocation/use count as well; a safe conversion does not prove an acceptable
resource limit or that a later expression uses the same rounded value.

## Precision loss and inconsistent rounding

IEEE single precision uses 24 significand bits and double uses 53. [5]
Constructed binary32 example: 16777216 is exact, while 16777217 is not; under
round-to-nearest ties-to-even, conversion rounds the latter to 16777216.
Different integer identifiers or counters can therefore collapse to one floating
value. This is distinct from overflow to infinity.

For a numeric-boundary finding, compare parsing precision, intermediate
arithmetic, stored precision and final conversion. Floor, ceiling and truncation
are not interchangeable for negative/fractional values. A producer and consumer
using different rounding can disagree about a count or boundary. Show the exact
input, formats and operation sequence; do not rely on rounded debugger display.

## Compiler assumptions and evidence limits

GCC -ffinite-math-only permits optimizations assuming no NaN/infinity, and
-ffast-math enables it along with other relaxed assumptions. [2] A source-level
isfinite or self-comparison is not proof of an emitted check when such options
apply. Inspect the shipped code; a diagnostic rebuild with strict options can
behave differently.

Consider finite boundary neighbors, zero, negative zero, subnormal values, NaN and
infinities where the input domain permits. Record floating exception state and
whether traps prevent the hypothesized sink. A surprising numeric result becomes
a vulnerability claim only with an evidenced violated invariant and relevant
input/control path, not merely a nondecimal representation.

## Result comparison is not always ordinary floating equality

Under the ordinary IEEE-style comparison assumptions above, two NaN results do
not compare equal using ordinary numeric equality. [1] A result oracle therefore
needs to say whether it compares numeric values, classifications, raw bits or
some domain-specific relation. Treating every NaN as equivalent can conceal a
representation distinction; treating every NaN pair as a mismatch can falsely
flag a permitted result. Keep the chosen rule tied to the actual contract.

Approximate equality also needs an error model and units; it is not appropriate
by default for an integer identifier or an exact allocation bound. A rounded display
match is not machine-value equality. Use reference-validation-oracles-comparison-relations
for tolerance and representation limits, and
playbook-validation-differential-metamorphic-analysis for comparing implementations.

## Sources and verification scope

Reviewed 2026-10-02. GNU libc/GCC documentation and current C++ draft; arithmetic
examples constructed, not executed against a specimen. Non-IEEE targets need
their own representation and comparison contract.

1. [GNU libc infinity and NaN](https://sourceware.org/glibc/manual/latest/html_node/Infinity-and-NaN.html).
2. [GCC math optimization options](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html): finite-math-only and fast-math.
3. [Floating-point classes](https://sourceware.org/glibc/manual/latest/html_node/Floating-Point-Classes.html).
4. [C++ floating/integral conversions](https://eel.is/c++draft/conv.fpint).
5. [IEEE floating-point parameters](https://sourceware.org/glibc/manual/latest/html_node/IEEE-Floating-Point.html): IEEE significand precision.
6. [C++ Boolean conversions](https://eel.is/c++draft/conv.bool): zero versus nonzero conversion, distinct from truncating conversion to other integer types.
