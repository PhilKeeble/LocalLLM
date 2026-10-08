---
id: playbook-re-incremental-parser-state
title: Recover incremental parser state across reads, errors and reconnects
kind: playbook
topics: [reverse-engineering, parsers, incremental-parsing, state-machines, vulnerability-analysis, malware-analysis]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Recover incremental parser state

## Separate transport reads, parser progress and application messages

Locate input submission, parser return, callbacks, message-complete indication
and consuming operation. Record actual byte counts rather than requested counts.
Identify whether the parser handles one message, a sequence or a fragment of an
outer protocol. Use reference-parser-incremental-input-buffer-state.

For malware analysis, a packet or extracted buffer is not necessarily a whole
command. Recover reassembly and decoding before assigning command meanings.
For vulnerability analysis, identify who can influence input content, partitioning,
arrival timing and connection termination without assuming all are controllable.

## Recover the state that survives an input call

Record parser phase, pending field width/length, cursor, buffered-byte count,
remaining payload, escape/Unicode state, nesting and accumulated output where
present. Explain each from loads, stores and branches; do not invent fields solely
because a textbook parser would need them. Separate per-message, per-connection
and global state.

Constructed review scenario: a multibyte length arrives in two reads. Determine
whether the code retains the first bytes and waits, misreads uninitialized bytes,
or resets the prefix before the next call. The same logical byte sequence should
not be assumed to follow the same code path under different read partitions.

## Track buffer movement and retained aliases

For every append, resize, compact, drain or replacement, recover which pointers,
offsets and lengths remain valid. Track unconsumed suffixes separately from
allocated capacity. Check the arithmetic before growth and before advancing the
cursor; allocation bounds do not prove logical-field bounds.

Constructed risk: a callback saves a pointer into a receive buffer, then compaction
moves later data over it before dispatch. The allocation may remain live while
the pointer names different bytes. Follow actual last use and ownership; route
native lifetime questions to reference-native-ownership-release-dangling.

## Identify completion, no-progress and error transitions

Classify need-more-input, complete, paused, invalid, EOF, would-block and timeout
using the actual API contract. Follow all outputs alongside the status. Determine
whether an error preserves partial fields and whether callbacks have already
performed effects. A loop needs progress, a state change that can lead to progress,
an external wait or termination; repeatedly retrying unchanged input may spin.

For resynchronization, identify the grammar rule making the new boundary reliable,
the discarded range and retained state. Do not turn an arbitrary magic-byte match
into evidence of a valid next record. Use reference-parser-stream-recovery-limits.

## Trace resource and session limits across message boundaries

Separate per-read capacity, per-field maximum, accumulated message size, nested
output size, concurrent-connection totals and time limits. Recover when each
counter resets. Backpressure means slowing or suspending input; it does not prove
bounded retained application state or eventual completion.

At disconnect/reconnect or object-pool reuse, trace parser reset, authentication
state, queued work and generation binding. Late completions must be evaluated
against their original operation/owner. Legitimate protocol resumption needs
explicit identity and state evidence, not an assumption that every reset is correct.

## Report a concrete state transition, not only a suspicious loop

For a vulnerability candidate, state the input/state before the transition,
instruction or callback changing it, violated bound/lifetime/policy and reachable
consequence. For malware analysis, report proven message assembly and dispatch,
including unresolved fragments and the distinction between capability and execution.

Reviewed 2026-10-02. The two referenced parser documents provide scoped primary
API/protocol evidence. These are static/evidence-review steps, not a requirement
to execute samples or run a retrieval test. Preserve uncertainty where captures
or control flow do not establish the complete transition.
