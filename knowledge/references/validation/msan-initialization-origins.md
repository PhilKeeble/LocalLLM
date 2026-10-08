---
id: reference-validation-msan-initialization-origins
title: MemorySanitizer initializedness, origin tracking and uninstrumented boundaries
kind: reference
topics: [msan, memorysanitizer, uninitialized-memory, origins, information-disclosure]
platforms: [linux, freebsd, netbsd]
architectures: [x64, arm64]
---
# MSan initializedness evidence

## Readable memory can contain an uninitialized value

Clang MemorySanitizer tracks uninitialized-value use, including branch conditions,
pointer use and selected call boundaries. It is not an addressability check.
Interpret an uninitialized-value report separately from out-of-bounds or freed
memory. Determine which producer failed to define bytes consumed by the operation.

## Origin tracking is additional evidence, not the current stack

MSan -fsanitize-memory-track-origins=1 records allocation origins; mode 2 additionally tracks
intermediate stores. Keep origin and use stacks separate. An allocation site
identifies where uninitialized storage originated, not necessarily the missing
initialization branch or the component responsible for consuming it.

## Missing instrumentation can invalidate initializedness propagation

MSan requires instrumentation across dependencies; supplied libc interceptors
cover common boundaries, not every external library or assembly write.
Uninstrumented code can cause false reports. Ignorelisted functions can cause
loaded values to be considered initialized. Preserve these exclusions before
interpreting silence or a warning.

For a disclosure investigation, establish the actual outgoing bytes and recipient.
An uninitialized-value warning alone proves neither secret content nor delivery.

## Source and scope

Reviewed 2026-10-02 against [Clang MSan](https://clang.llvm.org/docs/MemorySanitizer.html):
Introduction, Origin Tracking, Ignorelist and Handling external code. Match the
specific toolchain/OS/architecture; tags are not a complete support matrix.
