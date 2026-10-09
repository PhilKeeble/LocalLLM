---
id: vulnerability-memory-stack-growth-stack-clash
title: Unsafe stack growth and stack-clash path
kind: vulnerability
topics: [memory-safety, stack, stack-clash, guard-page, alloca, vla]
platforms: [cross-platform]
architectures: [any]
---

# Unsafe stack growth and stack-clash path

## Definition and violated invariant

Unsafe stack growth occurs when attacker-influenced fixed or dynamic frame growth, variable-length allocation, recursion, or nested execution exceeds the supported stack policy. A stack clash is the narrower case where a large adjustment skips a guard region and subsequent stack access reaches another mapped region instead of faulting safely.

The target ABI, compiler-generated prologue, probe sequence, operating-system growth/guard policy, thread stack mapping, and later access all form the invariant. A large allocation or missing familiar helper alone does not establish a clash.

## Conditions that establish the issue

Recover the maximum stack-pointer movement on a feasible path, including alignment and repeated allocations. Establish the target's guard arrangement and required probe spacing, then prove the emitted sequence can skip that guard and touch usable memory beyond it. For exhaustion, prove the input can reach an unhandled failure or unacceptable recursion depth.

Separate static frame probing from dynamic adjustments and calls that add their own frames. Probes must occur before ordinary use of the final region and cover every page interval required by the target policy.

## Evidence that is not sufficient

Use of `alloca`, a VLA, recursion, a large frame, `sub SP`, or absence of `__chkstk` is not sufficient. The frame may be bounded below a relevant threshold, another inline probe loop may be present, the operating system may reject the adjustment, or the platform may use a different mechanism.

A guard fault usually demonstrates containment or exhaustion, not a successful clash into adjacent memory. Likewise, presence of a stack-check helper does not validate arrays inside the frame or bound recursive aggregate use.

## Investigation sequence

Trace every value contributing to stack growth, its width, alignment rounding, upper bound, and repetition. Reconstruct the prologue and dynamic paths from instructions and unwind metadata where applicable. Mark each page touch and its order relative to stack-pointer updates.

Compare the largest gap with the actual thread-stack mapping and guard policy. Identify the first ordinary read or write after the skipped region and whether it aliases another mapping. Inspect exception, signal, and failure handling before assigning availability or corruption impact.

## Constructed source example

This hypothetical function places an attacker-sized temporary on the native stack and touches only the resulting region through a copy:

```c
void process_message(const uint8_t *input, size_t length)
{
    uint8_t *temporary = dynamic_stack_allocate(length);
    memcpy(temporary, input, length);
    consume(temporary, length);
}
```

The pseudofunction deliberately leaves compiler and platform semantics unspecified. The source establishes attacker-influenced stack demand, but a vulnerability finding still needs a reachable length, emitted adjustment/probes, stack policy, failure behavior, and valid source extent.

## Constructed machine representation

This pseudodisassembly shows the pattern requiring target-specific review:

```asm
size = align_up(attacker_length, stack_alignment)
stack_pointer = stack_pointer - size   ; one large adjustment
store_byte [stack_pointer], 0          ; only final region is touched
call consume
```

The single final touch does not probe intervening pages. It becomes a stack-clash path only if `size` can skip the actual guard and the final or later accesses land in another usable mapping; a safe fault is a different outcome.

## Primitive and impact limits

The direct result may be controlled stack exhaustion, process or privileged-context termination, or collision with another mapping. Record which outcome is supported. An allocation failure or guard exception that is handled without unsafe continuation may have no security impact.

Memory corruption and privilege escalation require proof of the collided mapping, controllable accesses, and relevant privilege boundary. Do not equate a large stack request with overwrite of a saved return address; that is a separate stack-buffer condition.

## Related knowledge and primary sources

`reference-native-stack-growth-and-probing` defines probe and guard distinctions, while `abi-windows-x64` describes Microsoft's special `__chkstk` convention. This profile repeats the skipped-guard and subsequent-mapping requirements needed in isolation.

Reviewed 2026-10-09 against Microsoft [x64 prolog and epilog](https://learn.microsoft.com/en-us/cpp/build/prolog-and-epilog), Microsoft [x64 stack usage](https://learn.microsoft.com/en-us/cpp/build/stack-usage), GCC [`-fstack-clash-protection`](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-fstack-clash-protection), and [MITRE CWE-121](https://cwe.mitre.org/data/definitions/121.html). The source abstraction and pseudodisassembly are constructed; operating-system guard behavior remains target specific.
