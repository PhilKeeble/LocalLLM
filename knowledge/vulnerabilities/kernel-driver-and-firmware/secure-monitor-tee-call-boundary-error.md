---
id: vulnerability-kernel-secure-monitor-tee-call-boundary-error
title: Secure-monitor, TEE or enclave call-boundary error
kind: vulnerability
topics: [firmware, secure-monitor, tee, enclave, shared-memory, calling-convention]
platforms: [cross-platform, embedded]
architectures: [arm, arm64, x86, x64, riscv32, riscv64]
---

# Secure-monitor, TEE or enclave call-boundary error

## Definition and violated invariant

This vulnerability occurs when a higher-trust monitor, TEE or enclave misdecodes function dispatch, registers, caller identity, shared-memory ranges or nested pointers, permits unsafe reentrancy, or restores incomplete/wrong context across a call boundary. The invariant is that the selected service, caller authority, captured inputs, protected state and return context must remain bound throughout the transition.

Calling conventions define register roles and preservation, not authorization. Shared memory controlled by a rich or normal world remains untrusted and mutable while mapped into a trusted environment.

## Conditions that establish the issue

Identify initiating execution world and caller identity, trap/call instruction, function ID and width, register convention, dispatcher, session/service, shared-memory ownership and extent, nested inputs, reentrancy state, saved context and return path. Prove lower-trust influence reaches a protected read/write, service, secret or restored state beyond policy.

For asynchronous or interrupted calls, include which context owns shared buffers and session state until final completion. For identity, use the trusted platform-provided caller token, not an untrusted field inside the request.

## Evidence that is not sufficient

An SMC/ECALL/enclave transition, shared buffer, secure-world pointer or privileged function is not sufficient. The dispatcher may reject the ID, copy and validate complete input, bind a trusted caller identity and restore all required state. A register value shown at entry does not prove it survives ABI conversion or reaches a consumer.

Do not generalize Arm SMCCC register layouts to another TEE, architecture or vendor ABI.

## Investigation sequence

Trace `caller world -> architectural transition -> function decoder -> service/session -> protected effect -> saved-state restore`. Annotate register widths, sign/zero extension, return convention and every shared range. Determine which bytes are copied and which remain externally mutable.

At binary level, map dispatch comparisons, table bounds, context-save areas and exception returns. Follow nested calls and callbacks for reentrancy. Check that errors restore world, interrupt, vector/floating-point and session state according to the selected ABI.

## Constructed flow

A hypothetical monitor accepts a normal-world shared-memory pointer and length in registers, validates the range, then passes the original pointer to a reentrant trusted service. A nested call lets normal-world code change a length field that the service later refetches. The security conclusion requires an actual reentry path and protected effect outside the first validation.

## Primitive and impact limits

Direct effects include secure-world memory access, confused-deputy service use, cross-session disclosure, state corruption or denial of service. Secure-world code execution requires control of memory or saved control state and the relevant mitigations; entry into a trusted service alone is not elevation.

## Related knowledge and primary sources

Double-fetch, authorization and saved-state profiles cover individual mechanisms. This profile keeps the higher-trust call boundary and world identity together.

Reviewed 2026-10-09 against Arm's [SMC Calling Convention](https://developer.arm.com/documentation/den0028/latest/), GlobalPlatform's [TEE Client API](https://globalplatform.org/specs-library/tee-client-api-specification/) and Intel's [SGX developer reference](https://www.intel.com/content/www/us/en/developer/tools/software-guard-extensions/sdk.html). The flow is hypothetical; each target ABI and threat model must be recovered independently.
