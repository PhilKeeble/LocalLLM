---
id: vulnerability-failure-uninitialized-security-sensitive-state
title: Uninitialized state reaches a security-sensitive operation
kind: vulnerability
topics: [uninitialized-memory, initialization, authorization, pointer, discriminator]
platforms: [cross-platform]
architectures: [any]
---

# Uninitialized state reaches a security-sensitive operation

## Definition and violated invariant

This vulnerability occurs when a pointer, length, flag, discriminator, object field, credential, or authorization result is consumed before every feasible reaching path gives it a valid value for that use. The invariant is defined-state dominance: the use must be dominated by initialization covering the same storage, generation, and path, or by a language/runtime rule that supplies a valid default.

Uninitialized state can cause disclosure, invalid memory access, wrong dispatch, or policy bypass. The impact depends on the consumer; uninitialized bytes are not automatically attacker-controlled or secret.

## Conditions that establish the issue

Identify the exact storage and byte/field extent, allocation or frame generation, language initialization rule, all definitions and partial writes, control-flow joins, error paths, and first security-sensitive use. Prove a feasible path reaches the use without a complete valid definition and determine what values can arise from prior stack/heap contents, padding, allocator behavior, or runtime defaults.

For aggregates, track fields and padding separately. A structure-wide zeroing call proves only the bytes it actually covers and can still encode an invalid discriminator or sentinel for the later API.

## Evidence that is not sufficient

A decompiler variable lacking an initializer, stack allocation, missing visible zeroing call, or warning is not sufficient. Initialization may occur through a caller, constructor, out parameter, aggregate copy, implicit runtime rule, or instruction the decompiler failed to associate with the variable. Dead or overwritten uninitialized values do not establish a reachable effect.

Do not assume zero is a safe default. Null pointers, zero lengths, false flags, or enum value zero can mean invalid, deny, allow, default, or a real object depending on the contract.

## Investigation sequence

Recover storage identity from machine accesses, not variable names. Build reaching definitions per byte or field through normal, exceptional, retry, and partial-success edges. Check constructor and allocator semantics and whether a result code establishes an out parameter. Follow the first undefined value into address calculation, copy length, branch, dispatch, serialization, or authorization.

When stack-slot reuse is possible, distinguish two nonoverlapping variables from one partially initialized object. Dynamic observations can demonstrate one realized value but cannot prove the value is stable across builds or calls.

## Constructed C and Windows x64 example

```c
int allowed;
if (lookup_policy(user, &allowed) < 0)
    log_failure(user);
if (allowed)
    perform_sensitive_action();
```

```asm
lea  rdx, [rsp+2Ch]       ; &allowed
mov  rcx, rbx             ; user
call lookup_policy
test eax, eax
jns  policy_done
mov  rcx, rbx
call log_failure          ; no defining store to allowed on this path
policy_done:
cmp  dword ptr [rsp+2Ch], 0
jne  perform_sensitive_action
```

The constructed path uses the Windows x64 integer-argument registers `RCX` and `RDX`. It is vulnerable only if failure leaves `allowed` undefined and execution continues to the branch. A callee contract that always initializes the out parameter, or a hidden store on the failure edge, disproves this instance.

## Primary sources and scope

Reviewed 2026-10-09 against C11 draft N1570 sections 6.2.6 and 6.7.9 in the WG14 [committee document](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), the C++ working draft [default-initialization rules](https://eel.is/c++draft/dcl.init), and MITRE [CWE-457](https://cwe.mitre.org/data/definitions/457.html) as taxonomy. Apply the selected language and ABI; managed runtimes can define defaults that native automatic storage does not have.
