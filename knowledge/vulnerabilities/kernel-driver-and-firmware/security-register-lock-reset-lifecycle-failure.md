---
id: vulnerability-kernel-security-register-lock-reset-lifecycle-failure
title: Security register, lock bit or fuse-derived state fails across lifecycle transitions
kind: vulnerability
topics: [hardware, firmware, security-register, lock-bit, fuse, reset, power-state]
platforms: [embedded, firmware]
architectures: [any]
---

# Security register, lock bit or fuse-derived state fails across lifecycle transitions

## Definition and violated invariant

This vulnerability occurs when a security-sensitive register or region starts permissive, remains writable after policy should lock it, derives the wrong state from fuses/straps, can be overridden by debug/test mode, or reopens across reset, sleep, resume, power-domain or recovery transitions. The invariant is that effective protection must match the boot trust model continuously before less-trusted actors can access the asset.

A fuse records state; combinational logic, reset defaults and firmware still determine how that state controls a particular register or interface. A set lock bit is evidence only for the assets and transitions it actually governs.

## Conditions that establish the issue

Identify protected register or asset, writers and readers, reset/default value, fuse/strap derivation, lock semantics, write-once behavior, debug/test overrides, power domains and every transition. Prove an unauthorized actor can reach a permissive or writable interval and perform a protected read/write before correct state is restored.

For resume and recovery, establish which domain retained state and which reset. Include ordering between access enable, policy initialization and lock assertion.

## Evidence that is not sufficient

A lock bit, fuse, reset path, writable register, debug mode or zero default is not sufficient. Firmware may configure and lock the asset before untrusted execution, hardware may enforce access elsewhere or the state may be intentionally service-authorized. A stale decompiler name does not define RTL semantics.

Do not infer permanence from write-once behavior without identifying the reset or power event that clears it.

## Investigation sequence

Build a state table across power-on, warm/cold reset, sleep/resume, firmware update, recovery, debug and fault states. For each, record the register value, controlling domain, permitted writers and protected effect. Trace fuse sampling and synchronization into the live access-control signal.

In firmware, locate configuration and lock order and every early return. In RTL, follow reset muxes, lock gating and override signals to the final write/read enable. Determine when lower-trust software or physical interfaces become active relative to that state.

## Constructed lifecycle

A hypothetical access-control register resets to allow nonsecure reads. Trusted firmware later writes restrictive policy and sets a lock bit, but resume resets the register's power domain without re-running initialization before nonsecure cores resume. The post-resume window violates policy if those cores can read the protected asset.

## Primitive and impact limits

Report the transition, open interval, actor and exact register, memory or debug capability exposed. Impact ranges from configuration change or secret readout to boot-policy bypass. Persistent code execution requires the reopened authority to install or execute controlled code.

## Related knowledge and primary sources

Debug and boot-chain profiles cover common consumers. This profile owns continuous effective protection across lifecycle transitions.

Reviewed 2026-10-09 against [MITRE CWE-1232](https://cwe.mitre.org/data/definitions/1232.html), [MITRE CWE-1233](https://cwe.mitre.org/data/definitions/1233.html), [MITRE CWE-1234](https://cwe.mitre.org/data/definitions/1234.html) and [MITRE CWE-1221](https://cwe.mitre.org/data/definitions/1221.html). The lifecycle is hypothetical; hardware reset and power-domain behavior require target documentation or RTL evidence.
