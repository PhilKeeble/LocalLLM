---
id: reference-microarchitecture-side-channel-evidence
title: Microarchitectural side-channel scope, shared resources and measurement limits
kind: reference
topics: [microarchitecture, side-channels, speculation, timing, caches, threat-models]
platforms: [linux, windows, macos, freebsd, android, embedded]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, powerpc]
---
# Side-channel interpretation limits

## Architectural correctness does not describe every microarchitectural effect

Intel's speculative-execution analysis distinguishes architectural program state
from microarchitectural effects, including caches, translation caches and shared
resource contention. Discarded speculative results can still affect those internal
resources. [1]

Recover processor/microarchitecture, code path, protected information and possible
observation boundary. A correctly rejected architectural access does not alone
settle side-channel exposure. Conversely, a branch or cache access is not proof
that an observer recovered information. Intel's examples explain a mechanism;
applicability and mitigation behavior require the actual hardware and configuration.

## Shared-resource and scheduling assumptions belong in the threat model

Intel distinguishes stateful channels, whose state changes can be observed later,
from stateless contention channels requiring concurrent activity. It also separates
data-dependent non-transient behavior from transient-execution mechanisms. [2]

Specify who can observe what, which resources are shared and whether concurrency
or persistent state is required. Same-machine placement does not prove the
necessary sharing or observer access. Do not assume every channel needs shared
pages, simultaneous threads or identical prerequisites. Preserve hardware scope;
one platform's channel or mitigation does not certify all processors.

## Timing variation is an observation, not automatically secret disclosure

A timing claim needs the measured event, units/clock, input classes, environment
and uncertainty. Distinguish variation associated with a public input or workload
from information about a protected value. Scheduling, caching, frequency changes,
I/O and collection overhead are competing explanations to assess for that claim.

Static code can identify a potential secret-dependent path; it cannot alone
establish an observer's resolution or reliable information recovery. Retain
sample scope and alternative explanations in any report. A faster/slower group
without a protected-value relation is not sufficient evidence of a side channel
across a claimed security boundary.

## Mitigation presence does not prove complete coverage of the claimed channel

Intel's guidance relates microarchitectural controls and workload configuration
to the system threat model. [2] Recover hardware support, deployed firmware/OS
state, protected transitions and application policy rather than treating a named
barrier or configuration flag as a universal proof.

Report the precise mechanism addressed and what remains unknown. A constant-time
comparison does not establish all surrounding accesses or speculative behavior
have the same property. Related: reference-crypto-timing-comparison-evidence.
Workflow: playbook-specialist-side-channel-review. No attack sequence is supplied.

## Sources and scope

Reviewed 2026-10-08. Intel primary explanations, not cross-vendor hardware contracts.
Other architectures are applicability candidates requiring their own evidence.

1. [Speculative-execution analysis](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/analysis-speculative-execution-side-channels.html): Speculative Execution, architectural/microarchitectural distinction.
2. [Workload security guidance](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/best-practices/securing-workloads-against-side-channel-methods.html): transient/non-transient, stateful/stateless channels and threat-model-dependent controls. Rolling primary page; no deployment-default or measurement result imported.
