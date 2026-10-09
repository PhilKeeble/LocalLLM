---
id: vulnerability-kernel-hardware-debug-interface-authority-lifecycle-exposure
title: Hardware debug, test or readout interface exposed under the wrong authority
kind: vulnerability
topics: [hardware, firmware, debug-interface, jtag, swd, scan-chain, lifecycle]
platforms: [embedded, firmware]
architectures: [any]
---

# Hardware debug, test or readout interface exposed under the wrong authority

## Definition and violated invariant

This vulnerability occurs when JTAG, SWD, a scan chain, manufacturing/recovery debug mode or another hardware readout/control path exposes registers, memory, halt/reset or instruction execution to an actor not authorized in the device's current lifecycle. The invariant is that debug capability, authentication and accessible assets must match production, service, recovery and manufacturing policy across every reset and mode transition.

Hidden or unpopulated board pins are a physical obstacle, not on-chip authorization. A debug interface can remain secure when exposed if its authentication and asset-level policy are correctly enforced.

## Conditions that establish the issue

Identify physical/logical interface and transport, device lifecycle and boot state, debug authentication, credentials or challenge state, lock/fuse inputs, reset and recovery behavior, selected access level and actual operations available. Prove the stated attacker can reach the interface and obtain memory, register, halt, reset or execution capability outside policy.

Check modes that override earlier locks, halt-on-reset and debug-module reset state. A production lock that reopens during recovery or a debug reset can still violate the lifecycle invariant.

## Evidence that is not sufficient

Test pads, JTAG strings, an enabled debug clock, a debug module, manufacturing code or a lock bit is not sufficient. Pins may be disconnected, authentication may gate useful commands, asset policy may restrict reads and device lifecycle may intentionally authorize service access.

Do not claim full memory or code-execution capability from boundary-scan access alone; enumerate the actual instructions, address domains and permissions exposed.

## Investigation sequence

Build a lifecycle matrix for power-on, reset, boot stages, production, service, recovery and failure states. For each, record interface reachability, authentication state, access level and protected assets. Trace hardware straps, fuses, security registers and firmware decisions into the final debug enable.

In firmware or RTL, locate debug authentication, reset values, lock updates and override muxes. Follow failure counters and reset sources. Correlate an observed command with its resulting memory/register operation rather than inferring capability from protocol discovery.

## Constructed lifecycle

A hypothetical device locks debug after secure boot, but asserting a recovery strap resets the debug module to an unauthenticated active state before recovery authentication runs. If an attacker can hold reset/recovery and halt the core before the lock is restored, the temporary window exposes authority contrary to production policy.

The finding requires reachable timing and an actual debug operation during the window. A detected port or permissive reset bit without demonstrated path is only a candidate.

## Primitive and impact limits

Report physical access, timing, credentials, lifecycle state and exact halt/read/write/execute/reset capability. Impact can include secret readout, firmware modification or control of processor execution, but only within the exposed address and policy domains.

## Related knowledge and primary sources

Security-register lifecycle and boot-policy profiles cover adjacent controls. This profile keeps interface reachability, authentication and asset capability together.

Reviewed 2026-10-09 against [RISC-V Debug Specification 1.0](https://docs.riscv.org/reference/debug/index.html), [MITRE CWE-1191](https://cwe.mitre.org/data/definitions/1191.html), [MITRE CWE-1244](https://cwe.mitre.org/data/definitions/1244.html) and [MITRE CWE-1234](https://cwe.mitre.org/data/definitions/1234.html). The lifecycle is hypothetical; implementation and board evidence determine reachability.
