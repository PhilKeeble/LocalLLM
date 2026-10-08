---
id: cpp-coding-standard
title: C++ ownership, failure and input-validation review
kind: playbook
topics: [cpp, coding, raii, exceptions, memory-safety, binary-parser]
platforms: [windows, linux, macos]
architectures: [x86, x64, arm64]
---
# C++ ownership, failure and input-validation review

## Recover contracts, not compliance with a coding style

Use this workflow for C++ source or reconstructed native code. Preserve target
language/library version, ABI, optimization and exception model where known.
Decompiler types and familiar library names are hypotheses until supported by
instructions, call arguments, metadata or matching implementation evidence.
Raw pointers and C-style APIs are review leads, not defects by themselves.

## Ownership, RAII and escaped views

RAII (resource acquisition is initialization) ties resource ownership to an
object's lifetime. Recover acquisition, owner construction, borrowing, transfer,
destruction and the actual release operation; a wrapper's name is not proof that
it owns or releases the right resource. Follow early returns and exceptional
edges as well as success. Native cleanup recovery:
reference-native-cpp-lifecycle-unwind and playbook-re-recover-cpp-lifecycle.

std::string_view and std::span refer to other storage; copying a view does not
extend the backing object's lifetime. [1,2] Trace retained callbacks, container
mutations and release before a later use. An unchanged pointer value does not
prove the same live object or a valid range. Exact invalidation rules belong in
reference-native-container-invalidation.

## Exception cleanup and termination are different outcomes

During ordinary C++ unwinding toward a handler, completed automatic objects are
destroyed in reverse construction order. Constructor failure requires examining
which subobjects completed initialization, not assuming the complete object's
destructor runs. [3] If destruction during unwinding exits by throwing, or an
exception escapes a non-throwing exception boundary, std::terminate is invoked.
Do not assume ordinary complete unwinding before termination. [4]

Recover handler ranges, constructed-state flags and release calls before claiming
a leak, double release or skipped authorization. A noexcept declaration constrains
exception escape; it does not establish successful work or rollback. A caught
failure can leave mutations or external effects that precede the throw.

## Fallible API results must govern the later use

For each allocation, conversion, I/O or commit, identify its actual success
predicate and valid outputs on failure. Trace the returned value and error state
through branches to the consumer. A missing local catch is not a flaw if the
documented boundary handles propagation; a catch that logs does not establish
that the operation failed closed. Status, exception and partial-result contracts
remain API-specific: reference-native-resource-lifetimes-results.

Determine whether a fallback restores a permitted state or publishes partially
updated state as success. Keep clean end-of-input, malformed data, truncated
records and I/O failure distinct where the protocol makes them distinct.

## Integer text parsing: successful prefix is not a valid whole record

For the C++17 integer std::from_chars interface, recover the valid [first,last)
input range, destination type, base and enclosing record grammar. The result's
ec reports conversion error; ptr identifies the first unconsumed character.
An out-of-range result leaves the destination unchanged. [5]

If the grammar requires a whole integer record, success requires both no error
and the appropriate end position. Separators may instead be intentionally parsed
by a following stage. Track embedded NUL within the original range rather than
silently reducing the record with a separate C-string scan. A conversion call
alone proves neither full consumption nor rejection of stale/default output.

## Binary ranges and count arithmetic need compatible domains

For nonnegative offset, length and size in the same units, first establish
offset <= size, then length <= size - offset. For nonnegative count and remaining
with element_size > 0 and compatible units, checking count <= remaining / element_size
avoids overflowing a count-times-size check.
These range inequalities do not establish pointer provenance, alignment, object
lifetime or initialized contents. Recover signedness and narrowing before applying
them. Facts: reference-native-integer-size-buffer-arithmetic.

Follow the checked value to the actual allocation, copy or index. A later reload,
unit conversion or different object can invalidate the connection. Wire data
cast to a native structure still needs representation, bounds and lifetime proof.

## String, copy and format sinks require exact arguments

For copy/format operations, recover source extent, destination capacity, count
units, overlap and terminator requirements. memcpy requires nonoverlapping valid
ranges; memmove's overlap support does not enlarge either range. Bounded names
do not guarantee appropriate termination or acceptable truncation. Distinguish
external text used as a format string from the same text passed as a data argument.
Contracts: reference-native-strings-copy-format.

## Report the violated invariant and the limits of the evidence

A supported finding identifies controlled input, a feasible guard-to-use path,
the exact lifetime/range/state violation and consequence. Keep static deductions,
captured events and diagnostic-build effects separate; a clean observed path
does not cover unobserved failure paths. No particular build or test tool is a
prerequisite for this review.

For malware analysis, trace reconstructed values and calls into their effects.
Ordinary ownership patterns, standard-library helpers and correct error handling
neither prove nor disprove malicious behavior. Use
playbook-vr-evidence-and-chaining for claim scope and unresolved relationships.

## Sources and limits

Reviewed 2026-10-02. Draft sections below support established lifetime and
conversion distinctions, not adoption of every newer draft feature by an older
target. Target-specific ABI/implementation facts remain in the named references.

1. [C++ string-view rules](https://eel.is/c++draft/string.view.template): referred storage and invalidation.
2. [C++ span overview](https://eel.is/c++draft/span.overview): non-owning contiguous views; std::span is a C++20 library facility.
3. [C++ stack unwinding](https://eel.is/c++draft/except.ctor): automatic objects and incomplete construction.
4. [C++ termination](https://eel.is/c++draft/except.terminate): exception escape and limits on unwinding.
5. [C++ from_chars](https://eel.is/c++draft/charconv.from.chars): range, error, unchanged destination and end pointer; integer-interface rules here do not require newer constexpr support.
