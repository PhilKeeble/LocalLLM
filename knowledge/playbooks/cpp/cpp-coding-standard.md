---
id: cpp-coding-standard
title: C++ implementation and review playbook
kind: playbook
topics: [cpp, coding, raii, exceptions, memory-safety, binary-parser]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# C++ implementation and review
Local workflow: preserve the requested language version, public API and existing project constraints.

## Ownership and RAII
Assign every acquired resource an owner immediately. Prefer automatic objects, std::string, std::vector and std::unique_ptr; wrap foreign handles with RAII. Avoid owning raw allocation pairs in ordinary application code. A string_view does not extend storage lifetime; spans and views also need bounds and invalidation checks. Cleanup must work on success, early return and exception propagation. Destructors must not let exceptions escape.

## Fallible calls and exception boundaries
For each fallible call, check its status, recover, translate the failure at a boundary, or deliberately propagate to a documented handler. Do not wrap every individual call in try/catch. Catch where recovery/reporting is useful; never swallow failure or return success after it. Promise noexcept only when its contract holds. Check input, output and explicit close/commit failures where relevant; ordinary iostream failures do not automatically throw. Guard aggregate arithmetic and counters against overflow. Command-line failures return nonzero; this playbook's malformed-input diagnostic prefix is input-error: (local convention, not language law).

## Untrusted input and binary parser review
Prove offset <= size, then length <= size - offset. Before multiplying an array count, prove count <= remaining / element_size with nonzero element_size. Check narrowing, endianness, alignment and lifetime; do not cast hostile bytes to trusted native structures.
For integer text parsing prefer std::from_chars where available: check its error and final pointer against the full string extent. A NUL terminator check alone can miss embedded NUL followed by junk. Distinguish truncation, invalid structure, unsupported format and I/O failure.

## Memory-safe API choices
Never introduce gets, strcpy, strcat, sprintf, vsprintf or unbounded scanf %s in new application code. Use owned strings and bounded parsing; never pass external text as a printf format. Bounded APIs still require capacity, truncation and termination checks; strncpy is not a general safe replacement. memcpy requires valid source/destination extents and non-overlap; use memmove when overlap is permitted.

## Verification
Compile with project warnings. Test valid, empty, malformed, boundary and failure cases, including embedded NUL, exact-end ranges and oversized counts as applicable. Check cleanup and state after failure, arithmetic overflow and output failure. Use supported sanitizers/fuzzing when warranted. Report what actually ran and any remaining limits.

Background: [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). API restrictions and diagnostics above are local policy.
