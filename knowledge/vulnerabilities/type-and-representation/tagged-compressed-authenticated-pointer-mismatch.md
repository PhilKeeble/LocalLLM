---
id: vulnerability-type-tagged-compressed-authenticated-pointer-mismatch
title: Tagged, compressed, or authenticated pointer mismatch
kind: vulnerability
topics: [pointers, tagged-pointers, pointer-compression, pointer-authentication, runtimes, abi]
platforms: [cross-platform]
architectures: [any]
---

# Tagged, compressed, or authenticated pointer mismatch

## Definition and violated invariant

A pointer-representation mismatch occurs when code interprets, reconstructs, copies, signs, authenticates, strips, or uses a pointer-like value under a schema different from the one that produced it. The tag class, payload width, base or cage, extension rule, address space, authentication key, discriminator, storage-address diversity, and eventual pointer role must remain consistent.

Pointer-shaped integers, high-bit patterns, tag tests, base additions, and authentication instructions are normal runtime and ABI mechanisms. The issue requires a reachable disagreement that changes the value or validity consumed as a pointer.

## Conditions that establish the issue

Recover the producer representation and every transformation to the dereference or indirect call. For a tagged value, identify tag bits and each payload class. For a compressed pointer, establish encoded width, extension, base, scale, allowed region, and null or immediate encodings. For an authenticated pointer, establish the actual target ABI, pointer role, key, discriminator, address diversity, signing operation, and authentication operation.

Prove a feasible value is decoded under the wrong class, base, width, or authentication context and reaches a memory or control-flow use. Keep analysis-only stripping separate from execution-time authentication.

## Evidence that is not sufficient

Masking high or low bits, a 32-bit load on a 64-bit process, an unusual pointer value, a pointer-authentication fault, or a runtime helper is not sufficient. The operation may be the correct decoder for that representation, and authentication failure may reflect corruption without attacker control.

A raw address obtained by stripping authentication does not prove that the original pointer would authenticate. A reconstructed address falling in a mapped region does not establish correct object identity, lifetime, bounds, or authority.

## Investigation sequence

Annotate each representation as a tuple: class or tag, encoded bits, base and scale, address space, and authentication schema when applicable. Follow the exact instruction widths through loads, extensions, arithmetic, masks, signs, authentication, and final use. Compare stores and later loads because representation conversions may be implicit at those boundaries.

For a failure, test the correct interpretation and plausible wrong interpretations against the observed bytes and faulting instruction. Then establish which input or corruption can create the mismatched value and what effective address or target results.

## Constructed x86-64 compressed-tagged example

Assume `RCX` holds the field address and a runtime defines a 32-bit field whose low bit is `1` for a heap pointer; the remaining bits are an unsigned byte offset from a heap base held in `R15`. Values with low bit `0` are immediate integers.

```asm
mov  eax, dword ptr [rcx]     ; zero-extend the encoded value
add  rax, r15                 ; incorrectly treats every class and tag bit as an offset
mov  rdx, qword ptr [rax]     ; dereference the reconstructed address
```

The sequence is inconsistent with the stated scheme because it neither distinguishes immediates nor removes the pointer tag before reconstruction. To establish a vulnerability, show a feasible encoded value reaches this path and that the resulting address is accessed; a different runtime may deliberately use biased bases or representations where an apparently similar addition is correct.

## Primitive and impact limits

The direct result can be wrong-address access, type confusion, invalid pointer use, loss of authentication, or unintended indirect dispatch. Code execution requires additional control over a usable target and satisfaction or bypass of active bounds, lifetime, memory-permission, and control-flow defenses.

## Related knowledge and primary sources

`architecture-machine-representation`, `reference-apple-arm64e-pointer-auth-evidence`, `reference-objc-dispatch-type-evidence`, and runtime representation references define the surrounding mechanisms. This profile repeats the full representation tuple and eventual-use requirement locally.

Reviewed 2026-10-09 against V8's [pointer-compression design](https://v8.dev/blog/pointer-compression), Clang's [pointer-authentication model](https://clang.llvm.org/docs/PointerAuthentication.html), and Apple objc4 [tagged-pointer and isa implementation](https://github.com/apple-oss-distributions/objc4/blob/main/runtime/objc-object.h). The assembly and encoding scheme are constructed and are not a claim about V8 or Objective-C layout.
