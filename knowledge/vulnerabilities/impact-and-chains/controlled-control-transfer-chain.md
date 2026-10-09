---
id: vulnerability-impact-controlled-control-transfer-chain
title: Controlled control-transfer and code-reuse execution chains
kind: vulnerability
topics: [rce, control-flow, return-address, function-pointer, vtable, rop, jop, coop, srop]
platforms: [cross-platform]
architectures: [x86, x64, arm, arm64]
---

# Controlled control-transfer and code-reuse execution chains

## Controlled instruction pointer or saved return address

A controlled instruction-pointer primitive exists when attacker-influenced state supplies the target of an executed branch, call, return, exception return, or equivalent transfer. For a saved return address, prove the root write reaches the saved control datum for the active frame, controlled bytes survive any encoding or integrity check, and execution reaches the consuming return. A crash at `ret`, an overwritten stack slot, or control over data adjacent to a return address does not establish a chosen target.

Record target constraints, controllable bytes, stack/register state, repetitions, timing, and whether the transfer is direct or speculative. On x86-64, `ret` conventionally pops its target from the architectural stack; a hardware shadow stack can independently validate returns. The source defect and the control-transfer primitive are separate findings.

## Controlled indirect callback, function pointer, vtable or dispatch entry

An indirect-target primitive exists when less-trusted influence changes the callable target selected at a reachable indirect call or jump. Establish object and table identity, entry index, pointer width/encoding, any receiver adjustment or thunk, expected signature, argument state, and effective control-flow policy. A writable pointer or corrupted vptr is insufficient until the actual call consumes it.

Virtual dispatch, callbacks, import tables, jump tables, delegates, exception handlers, and runtime stubs have different validation and lifetime contracts. A type-confused call can fail before useful work because its ABI does not match; conversely, a constrained target set can still include a security-relevant operation. State the admitted targets rather than calling every indirect corruption arbitrary control.

## Partial or relative overwrite

A partial overwrite controls only selected bytes or changes a target by a constrained delta. Prove byte order, address width, preserved high bits, carry behavior, alignment, mapped destination, and uncertainty from address randomization. For adjacent data corruption, identify the exact security-bearing field and its later use; changing a length, flag, role, or object pointer can be security-relevant without immediate instruction-pointer control.

Constructed little-endian example: overwriting the low two bytes of `0x00007ff612341000` with `0x2780` yields `0x00007ff612342780`. This says nothing about whether that address contains a valid target, whether the high bytes remain stable, or whether a control-flow policy admits it.

## Code-reuse chain

A ROP, JOP, COP, COOP, SROP, or related chain reuses existing code or a kernel/runtime context mechanism. Establish the initial transfer, controllable stack or dispatcher state, usable instruction sequences or virtual calls, calling convention, memory reads/writes required to stage the chain, and the final effect. For SROP, prove the target kernel and ABI accept the constructed signal frame and that execution reaches the relevant return mechanism.

Classify defenses from the affected process and build: forward-edge CFI, indirect-branch tracking, pointer authentication, return shadow stacks, code signing, and address randomization constrain different edges. Merely finding gadgets or a dispatcher loop does not prove a chain; show that all state transitions are simultaneously satisfiable under the active policy.

## Alternate saved-context control transfer

Exception handlers, unwind records, signal frames, `setjmp`/`longjmp` buffers, coroutine continuations, fibers, and saved execution contexts can restore control state without an ordinary function return. Identify who creates and authenticates the state, its ABI fields, mutation authority, restoration path, and any target validation. A structure that contains a code address is not sufficient; prove the active runtime consumes attacker-influenced state.

Do not decode one platform's context layout using another ABI or assume pointer mangling is absent. Unwind metadata can describe cleanup and stack reconstruction without itself being writable runtime state.

## Constructed x86-64 representation

```asm
mov  rax, qword ptr [rcx+18h] ; load callback from an object field
mov  rdx, qword ptr [rcx+20h] ; load callback argument
call rax                      ; indirect transfer consumes both values
```

This gives useful control only if the object at `RCX` is the corrupted generation, the callback field and argument are attacker-influenced as claimed, the call is reachable, and the target passes effective control-flow checks. The instruction sequence is hypothetical and does not identify a source type or vulnerability by itself.

## Impact limits and primary sources

Control of one transfer establishes neither persistence nor remote code execution. Report the demonstrated continuation and authority; code execution additionally needs a viable target or chain, suitable arguments/state, and a reachable source of influence. Reviewed 2026-10-09 against Intel's [software developer manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html), Microsoft's [Control Flow Guard](https://learn.microsoft.com/en-us/windows/win32/secbp/control-flow-guard), Intel [Control-flow Enforcement Technology](https://www.intel.com/content/www/us/en/developer/articles/technical/technical-look-control-flow-enforcement-technology.html), Arm [pointer authentication](https://developer.arm.com/documentation/102433/latest/), the [Itanium C++ ABI virtual-table rules](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#vtable), Shacham's [return-oriented programming paper](https://hovav.net/ucsd/dist/geometry.pdf), and Bosman and Bos's [SROP paper](https://www.cs.vu.nl/~herbertb/papers/srop_sp14.pdf). Apply the target ABI and mitigation configuration.
