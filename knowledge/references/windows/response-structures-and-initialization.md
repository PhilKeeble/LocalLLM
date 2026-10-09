---
id: reference-windows-response-structures-initialization
title: Native response structures, initialization, padding and disclosure
kind: reference
topics: [windows, structures, initialization, padding, information-disclosure, ipc]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---

# Native response structures, initialization and disclosure

## Applicability and canonical source

The representation and data-flow rules here apply to native responses across platforms; the existing Windows path and source ID are retained for citation stability. API-specific output-length and transport contracts remain platform-specific. This is the canonical shared initialization reference, not a claim that Windows IOCTL, Linux read and Mach message interfaces behave identically.

## Outbound byte ranges need initialization and recipient authorization

When a native structure or buffer crosses a process, privilege, device, network, or trust boundary, every returned byte must have a defined value. Assigning all named fields does not necessarily initialize compiler-inserted padding, union storage, reserved fields, alignment gaps, or bytes after a variable-length member. Different architecture, packing, compiler, or version can change layout.

Determine the exact byte count written to the boundary and compare it with fields definitely initialized on that path. Include error/partial paths, structure version/size fields, nested structures, and arrays. Returning `sizeof(struct)` is safe only if the whole object representation is initialized and is the intended wire contract.

## Field initialization is not complete object-representation initialization

Prefer explicit serialization into a byte buffer with every emitted byte assigned by the wire contract. C++ value-initialization is not a blanket promise to zero every byte of every class: whether zero-initialization precedes construction depends on the selected constructor. Padding and inactive union storage must be assessed for the actual type, language version and emitted operations, including subsequent assignments/copies. Do not infer the final outbound representation solely from an initializer's spelling.

Zeroing a raw outbound byte buffer can establish its initial contents, but later copies can reintroduce unspecified or sensitive bytes. Inspect the final returned range. Set reserved fields to their documented values and copy only the response length required by the protocol.

Do not `memset` arbitrary non-trivial C++ objects, objects with virtual state, or types whose all-zero representation is invalid. Construct those objects normally and serialize defined fields into a separate byte buffer.

## Pattern-filled storage is only candidate unwritten-byte evidence

If available diagnostic evidence began with a known fill pattern in raw outbound storage, matching bytes before transfer can identify candidate unwritten ranges. They are not proof: legitimate writes can produce the same bytes. Corroborate with the reaching writes, path conditions and final transferred range. Absence of the pattern does not prove initialization on every path.

Keep diagnostic initialization separate from production behavior: changed layout, initial contents or instrumentation can change the observed result. Establish external disclosure from bytes crossing the actual boundary to an unauthorized recipient, not merely from a pattern remaining in internal storage. This inference does not require building a diagnostic target or modifying a specimen.

## Error paths, reuse and returned lengths

Constructed investigation: a 64-byte response is reused across requests. The success path writes 64 bytes; an error path updates only the first eight but still sends 64. Trace bytes 8..63 back to their previous writes. Stale data is not necessarily indeterminate at the language level, yet it may disclose a previous client's information. Show the final transmitted count, actual bytes, recipient and trust boundary before claiming external disclosure.

Track defined ranges after partial reads, constructor failure, version-specific branches and optional fields. Initial allocation, object construction, field assignment and outbound serialization are separate events. An initialized length field does not prove that its claimed payload was filled, and a fully initialized buffer may still contain information the recipient is not allowed to receive. Distinguish initialization defects from authorization defects.

## Construction, unions and definite writes

For each emitted byte range, enumerate feasible paths reaching the send/copy and the last defining write on each path. A constructor call does not establish that every scalar member or padding byte was written; distinguish default, value and zero initialization for the selected type and constructor. For a union or variant payload, trace the active alternative and which storage is actually serialized. Do not assume the largest alternative's full extent was filled when a smaller alternative is active.

Inspect nested arrays, early exits, failed conversions, shortened payloads and subsequent copies from other objects. Source-language uninitialized-value rules vary by type and edition; at the binary boundary, establish the bytes actually read and transmitted. A deterministic zero-filled tail can refute a proposed stale-byte disclosure on that path, but not an unrelated leak of initialized sensitive fields. Record both counterevidence and untested paths.

## Transport counts are not interchangeable with delivered bytes

A native response's initialized range, claimed length, actual transfer and recipient are separate evidence. For Windows DeviceIoControl, FALSE may mean pending work or a partial-result condition; an arbitrary error does not prove buffered output was copied back. Direct-buffer writes can already have happened before completion. The method, status and count contracts have their primary home in reference-windows-driver-ioctl-buffer-access, not a shared rule that all failed transports return their buffers.

Inference: an excessive completion count is a defect candidate, while an external information-disclosure claim additionally needs a feasible transfer of bytes the recipient was not entitled to receive. Conversely, an error code does not undo writes already made into caller-visible storage.

## Sources

Initialization and diagnostic-pattern qualifications reviewed 2026-10-02. These C++ representation principles also apply outside Windows; platform transport and response-length contracts still require their own verification.

- [C++ draft initialization](https://eel.is/c++draft/dcl.init): distinction between zero-, default- and value-initialization.
- [C++ draft object/value representation](https://eel.is/c++draft/basic.types): padding is distinct from value bits.

- [SEI DCL55-CPP: Avoid information leakage when passing a structure across a trust boundary](https://wiki.sei.cmu.edu/confluence/display/cplusplus/DCL55-CPP.+Avoid+information+leakage+when+passing+a+structure+across+a+trust+boundary)
- [SEI EXP53-CPP: Do not read uninitialized memory](https://wiki.sei.cmu.edu/confluence/display/cplusplus/EXP53-CPP.+Do+not+read+uninitialized+memory)
