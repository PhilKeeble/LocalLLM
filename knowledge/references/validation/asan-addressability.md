---
id: reference-validation-asan-addressability
title: AddressSanitizer shadow memory, allocation boundaries and report interpretation
kind: reference
topics: [asan, addresssanitizer, shadow-memory, use-after-free, bounds, instrumentation]
platforms: [windows, linux, macos, android, freebsd]
architectures: [x86, x64, arm, arm64]
---
# ASan addressability evidence

## Shadow memory describes access validity, not application payload

AddressSanitizer combines compiler instrumentation with a runtime. Its design
uses shadow metadata to mark inaccessible regions, including allocation redzones
and freed blocks held temporarily in quarantine. Poisoning changes that metadata;
it need not overwrite the corresponding application bytes. [1,2]

Investigative consequence: distinguish a shadow-byte dump from target content.
A recognizable string remaining in a freed block does not establish a valid
lifetime. Quarantine also changes reuse behavior; an instrumented allocation
sequence is not proof of the shipped allocator's exact layout or reuse order.
The historical design source is not a universal shadow-address formula.

## ASan reports an access against the boundaries it knows

ASan can detect heap/stack/global out-of-bounds accesses, use-after-free and invalid
release. Stack use-after-return and use-after-scope have separate controls.
Container overflow detection depends on library annotations; partial instrumentation
or poisoning can produce misleading container reports. [1]

Investigative consequence: recover the operation, width, address and object
contract. A write to the wrong field inside an addressable object can violate an
authorization invariant without crossing an ASan boundary. A clean report cannot
validate semantic lengths, permissions or all subobjects of a custom arena.

## Preserve the report and instrumentation scope

ASan reports can include access and allocation/free stacks; symbolization uses
matching debug information. Excluded functions, ignorelists and runtime settings
affect detection/reporting. [1] Keep raw addresses and binary identity alongside
symbolized names. A report from a rebuilt parser is evidence about that build;
map its operation to the original binary before transferring the conclusion.

First-detected-error chronology is covered by
reference-validation-detection-point-corruption. Windows-specific runtime and
debugger caveats are in reference-validation-windows-diagnostics.

## Sources and scope

Reviewed 2026-10-02. Toolchain/target support and enabled checks require matching;
these are not universal guarantees for every ASan implementation.

1. [Clang ASan](https://clang.llvm.org/docs/AddressSanitizer.html): instrumentation, reports, optional checks, container annotations and exclusions.
2. [ASan authors' algorithm description](https://github.com/google/sanitizers/wiki/AddressSanitizerAlgorithm): shadow, redzones and quarantine; historical design, not current offsets.
