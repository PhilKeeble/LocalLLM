---
id: vulnerability-integer-floating-enum-boolean-state-conversion
title: Floating-point, enumeration, or Boolean conversion changing security state
kind: vulnerability
topics: [floating-point, enums, booleans, conversions, state-validation]
platforms: [cross-platform]
architectures: [any]
---

# Floating-point, enumeration, or Boolean conversion changing security state

## Definition and violated invariant

This vulnerability occurs when conversion or validation of a floating value, enumeration, or Boolean accepts a representation outside the security decision's intended domain and maps it to an unintended size, selector, or state. Storage representability and semantic validity are separate: an enum's underlying type can represent values that the protocol does not define, and an integer Boolean ABI may accept nonzero values beyond canonical one.

Floating NaN is unordered, so rejection checks such as `x < minimum || x > maximum` can accept NaN. Conversion of NaN, infinity, or an out-of-range floating value to an integer has language-specific behavior and must be established before relying on the result.

## Conditions that establish the issue

Recover raw representation, source type, conversion, accepted semantic set, comparison behavior, ABI storage width, and final consumer. Prove a feasible noncanonical or exceptional value passes validation and selects or sizes a security-relevant operation differently from the intended policy.

For enums, identify every accepted value rather than assuming an in-range underlying integer names an enumerator. For Boolean fields, determine whether the boundary uses zero/nonzero truth or requires a canonical encoding.

## Evidence that is not sufficient

An enum cast, floating comparison, `SETcc`, or nonzero Boolean is not sufficient. The domain may deliberately support extension values or NaN, a default branch may reject unknowns, and zero/nonzero may be the documented Boolean contract.

Decompiler enum labels and Boolean types do not validate the stored value or prove the original declaration.

## Investigation sequence

Trace decoding and conversion into the decision, preserving raw bits and semantic value. Enumerate explicit cases and default behavior. For floating input, include NaN, infinities, signed zero, and representability boundaries only when the input format permits them.

At binary level, recover ordered versus unordered branches and the width actually loaded for enum or Boolean storage. Follow the selected state into the privileged action, array, allocation, or dispatch.

## Constructed source and assembly example

```c
enum action : uint32_t { view = 0, edit = 1 };

void dispatch(uint32_t wire_value)
{
    action selected = static_cast<action>(wire_value);
    if (selected == view)
        view_record();
    else
        edit_record();
}
```

Every nonzero value, including undefined protocol values, reaches `edit_record`. A matching fragment is `test ecx,ecx; jne edit_path`. The issue requires policy to permit only explicit values and `edit_record` to carry greater authority; an else branch that rejects unknowns would differ.

## Primitive and impact limits

The direct primitive is selection or sizing under an unintended semantic value. It may cause incorrect authorization, out-of-range indexing, allocation error, or fail-open state.

Privilege impact requires the selected path to perform an operation unavailable to the caller. An unknown value that is logged or rejected has no such effect.

## Related knowledge and primary sources

`reference-native-floating-validation` defines NaN and conversion boundaries, while `abi-data-models-api-types` covers enum and Boolean storage. This profile repeats semantic-set validation locally.

Reviewed 2026-10-09 against C++ [enumerations](https://eel.is/c++draft/dcl.enum), [Boolean conversions](https://eel.is/c++draft/conv.bool), [floating-to-integer conversions](https://eel.is/c++draft/conv.fpint), and [MITRE CWE-704](https://cwe.mitre.org/data/definitions/704.html). The source and instruction fragment are constructed.
