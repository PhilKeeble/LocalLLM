---
id: reference-validation-ubsan-check-semantics
title: Selected runtime checks, defined arithmetic warnings and trap versus recovery
kind: reference
topics: [ubsan, undefined-behavior, integer-overflow, alignment, instrumentation, traps]
platforms: [windows, linux, macos, android, freebsd]
architectures: [x86, x64, arm, arm64]
---
# Runtime diagnostic checks are not a complete undefined-behavior oracle

## Check groups do not enable every diagnostic

Clang's -fsanitize=undefined group excludes checks including unsigned-integer-overflow,
implicit-conversion, local-bounds and vptr. Record effective fine-grained options,
not just the UBSan label. Integer-conversion diagnostics and arithmetic-overflow
diagnostics answer different questions.

Unsigned wrap can be defined language behavior yet trigger an explicitly enabled
check. Establish operand types, widths and the violated application invariant;
do not label every UBSan integer warning source-level undefined behavior.

## Trap, fatal report and recovering report are different outcomes

Most Clang UBSan checks can report and continue; -fno-sanitize-recover=CHECK changes
termination, while supported -fsanitize-trap=CHECK emits a trap without needing
the reporting runtime.
Trap options alone do not enable checks. The vptr check does not support trap mode.

An unexplained trap is not proof of a specific source bug. Recover its condition
and instruction path. A continuing process does not establish that no diagnostic
occurred, and suppressed reporting does not repair the operation.

## A diagnostic rebuild is not the original machine code

For reversing, connect the reported expression to emitted operands and guards in
the shipped binary. A guessed decompiler type cannot establish the original
source-level contract. Use reference-native-compiler-transformations.

## Source and scope

Reviewed 2026-10-02 against [Clang UBSan](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html),
Usage and Available checks. Match compiler, target and options; group membership
is an implementation contract, not a complete language-UB checklist.
