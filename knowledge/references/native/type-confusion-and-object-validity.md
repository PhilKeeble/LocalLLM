---
id: reference-native-type-confusion-object-validity
title: Native type confusion, discriminators, aliasing and valid object representations
kind: reference
topics: [type-confusion, casting, discriminators, aliasing, object-lifetime, representations]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Type confusion and object validity

## Type confusion is a producer-consumer disagreement

Investigative definition: an operation interprets an object using a type/layout
or semantic variant that the object's actual construction/state does not satisfy.
To establish a finding, link object creation, discriminator updates, validation
and the incompatible access/dispatch on one feasible path. A decompiler cast
alone is not evidence that the source contained an unsafe cast.

Constructed example: a message tag selects a short inline-data variant, while
a later handler interprets the same storage as a pointer-bearing variant. Prove
that this combination passes the actual tag/length/state checks and identify
which field becomes a length, pointer or call target. Matching record sizes
do not establish matching field meanings.

## C++ static_cast downcasts do not perform runtime type tests

A permitted static_cast downcast requires a non-null source pointer to designate
the corresponding base subobject of an actual derived object; it does not perform
a runtime type test. A null source yields a null destination pointer. Violating
the non-null object condition is undefined behavior. [1]

## C++ dynamic_cast failure differs for pointers and references

For applicable dynamic_cast runtime checks, failure to pointer type produces
null; failure to reference type throws std::bad_cast. The operand must itself
meet lifetime/type requirements; dynamic_cast is not validation of arbitrary
attacker-supplied addresses. [2]

Investigation: locate the actual cast helper or inlined tag test and how failure
is handled. A thunk adjusting a base pointer can be legitimate inheritance,
not corruption. Compare the adjusted address with the expected subobject and
dispatch table under the target C++ ABI; a guessed vtable type is not proof.

## Discriminators must describe the consumed payload

Recover all writers of a tag, size, vptr, version or state field, not only the
creation path. Track whether validation and use refer to the same snapshot.
An independently mutable tag/payload pair can cease to agree between checks.
An unknown/default tag must have an explicit behavior, not an inferred success.

Constructed investigation: the dispatcher validates version 1, then calls a
helper that re-reads a shared version field to select a version-2 layout. Test
the mutation window and layout-specific accesses. If the request is copied and
all reads use the immutable copy, that can refute this particular disagreement;
the copy must be complete and its nested pointers separately accounted for.
For wire tags, schema alternatives and decoded-object defaults, use
playbook-re-serialization-schema-boundary; encoded tags are not native vptrs.

## Size and alignment do not establish a live object of a type

C++ object lifetime and permissible reuse are separate from storage existence.
Some specified allocation/copy operations can implicitly create suitable objects;
do not claim every raw allocation necessarily requires an explicit constructor.
Equally, a reinterpretation or suitably aligned address alone does not establish
that the intended object exists and is usable. [3]

For binary analysis, distinguish a raw serialized record parsed bytewise from
a C++ object used through typed member access. Record the actual operations and
compiler assumptions. Avoid importing a C effective-type rule unchanged into
C++, or using source UB terminology as a substitute for demonstrating the
shipped machine behavior and external reachability.

## C++ byte inspection is not arbitrary typed-pointer access

C++ type-accessibility rules permit inspecting object representation through
char, unsigned char or std::byte and specified compatible types. This is not
permission to access an arbitrary object through any unrelated typed pointer. [4]

## Raw bytes in bool storage differ from integer-to-bool conversion

An access to an invalid value representation can be undefined; for example,
bytes copied into bool storage need not constitute a valid bool representation.
An integer-to-bool conversion is different from a raw byte overwrite. [5]

## bit_cast does not validate the semantic domain of wire data

bit_cast has size/trivial-copy constraints and representation rules; it is not
a validator that makes every input bit pattern a valid target value. [6]
Investigate bytes copied into pointers, enums, Boolean fields and discriminated
unions before trusting later typed accesses. For wire data, decode and validate
the semantic domain independently of whether its byte count matches sizeof(T).

## Sources and verification scope

Reviewed 2026-10-02 against current C++ working-draft clauses. Lifetime and
indeterminate-value wording evolves across editions; use the actual target
compiler/language contract. Examples are constructed, not observed exploits.

1. [static_cast](https://eel.is/c++draft/expr.static.cast): base-to-derived requirements.
2. [dynamic_cast](https://eel.is/c++draft/expr.dynamic.cast): runtime checks and failures.
3. [Lifetime](https://eel.is/c++draft/basic.life) and [C allocation](https://eel.is/c++draft/c.malloc): storage/object distinction and implicit creation.
4. [Type accessibility](https://eel.is/c++draft/basic.lval).
5. [Lvalue conversion](https://eel.is/c++draft/conv.lval): invalid value representations.
6. [bit_cast](https://eel.is/c++draft/bit.cast).
