---
id: reference-linux-io-uring-request-lifetime
title: io_uring submissions, completions, cancellation and buffer ownership
kind: reference
topics: [linux, io-uring, asynchronous-io, ownership, buffers, cancellation, completion]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Asynchronous ring request identity and lifetime

## A submission entry and a completed operation are different events

Linux io_uring has submission entries (SQEs) and completion entries (CQEs).
Completions can arrive out of submission order; user_data is returned to support
request correlation. [1]

For investigation, identify ring, request generation, opcode, flags, actual
resource and supplied buffers. Preparing an SQE does not establish submission
or effect. A recycled user_data value can join unrelated requests if application
lifetime is ignored. Preserve the consumer's correlation method and missing
events; do not infer ordered effects merely from adjacent submissions or equal
buffer addresses. Particular linking/ordering features need their own contract.

## Operation data buffers can outlive submission metadata

The io_uring manual distinguishes metadata consumed at submission from data
buffers used while an operation is in flight. Read/write data buffers must remain
valid until their relevant completion. [1]

Investigate the opcode's actual ownership and consumption rules. An SQE consumed
by the kernel is not proof every pointed-to allocation can be freed or changed.
Conversely, do not assume every auxiliary structure must survive until final
completion if its contract copies it earlier. Record buffer extent, producer,
mutation, release and supported final-consumer event. Special registration,
provided-buffer and zero-copy modes require their own release/notification rules.

## A CQE result and flags need the request's completion contract

io_uring CQEs supply user_data, res and request-specific flags. For supported
multishot operations, IORING_CQE_F_MORE indicates more completions are expected
from that request. [1]

For investigation, interpret res with the opcode's result convention and actual
completed extent. One CQE is not universally one final resource-release event;
multishot or notification modes can have additional obligations. A short I/O
result does not fill the remainder of a destination buffer. Preserve terminal
state and buffer-selection identity before attributing returned bytes or freeing
request state. Feature support and active mode must be established on the target.

## Cancel completion and the target request's completion are distinct

The liburing cancellation contract reports the cancellation request separately.
An unmatched request can already have completed; an operation too advanced to
cancel can still complete later. The documented EALREADY case requires waiting
for the targeted request's completion. [2]

For investigation, bind cancellation selector, target request generation, cancel
result and target completion. A cancellation attempt does not establish that
all access to data buffers ended. An ENOENT result cannot by itself distinguish
an invalid selector from a request that completed earlier. Cleanup must follow
the actual terminal ownership condition, not merely a function named cancel.
Do not generalize one cancellation variant's result to all ring operations.

## Ring/resource registration must be included in authority and teardown evidence

For analysis, determine whether an entry selects an ordinary descriptor, a
registered resource or another supported indirection. Record the resource's
generation, owner, binding and allowed operation from the actual interface.

Closing a familiar descriptor number cannot alone prove every registered or
in-flight reference has been removed. Likewise, a completion cannot authenticate
the identity of a resource registered after a number was reused. Trace registration,
replacement, outstanding work and terminal release under the supported contract.
This is an ownership question, not a universal claim about every opcode or ring
mode; use reference-linux-descriptors-open-file-descriptions for ordinary references.

## Sources and scope

Reviewed 2026-10-08. Upstream liburing manual pages as rendered by man7:
submission/completion, in-flight buffers and multishot indication; cancellation
results and notes. Feature names specify scope, not assumed kernel availability.

1. [io_uring(7)](https://man7.org/linux/man-pages/man7/io_uring.7.html): queue events, correlation, metadata/data lifetime and flags.
2. [io_uring_prep_cancel(3)](https://man7.org/linux/man-pages/man3/io_uring_prep_cancel.3.html): target versus cancellation result and delayed completion.

Workflow: playbook-linux-async-lifetime. No ring structure offsets, submission
recipe or unsupported opcode semantics are assumed.
