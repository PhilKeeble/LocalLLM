---
id: abi-itanium-cpp-dispatch-layout
title: Itanium-style C++ vtable address points, inheritance adjustments and member pointers
kind: reference
topics: [cpp, vtables, rtti, inheritance, thunks, member-pointers]
platforms: [linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64]
---
# Interpret Itanium-style C++ object machinery

## Address point is not necessarily the table beginning
Reviewed 2026-10-02. A virtual table supplies dispatch entries and associated
metadata; vptr means the object's virtual-table pointer. For the ordinary Itanium
C++ ABI, the vptr selects an address point; metadata may precede it. Function-entry
representation is processor-specific. [1] This is not the Microsoft ABI or a relative-vtable
extension. Platform tags are possible users, not confirmation of a specimen's ABI.

Constructed ordinary x64 layout with eight-byte entries: object vptr=0x5000,
candidate signed offset-to-top at 0x4ff0, RTTI pointer at 0x4ff8 and callable
entry at 0x5000. Calling the word at 0x4ff8 as code confuses metadata with dispatch.
These candidate offsets require the stated ABI and entry-width evidence; do not
copy them to another target merely because its executable is ELF or Mach-O.
Record the address point, component role, entry width and relocation separately.

## Secondary subobjects and signed offsets
Itanium offset-to-top maps the vptr-bearing subobject to its object top; secondary
tables can have negative values, while construction tables can differ. Vbase
offsets locate virtual bases; vcall offsets support virtual-call adjustments. [1]

Constructed completed-object candidate: receiver B=0x1020 and offset-to-top=-32
give top=0x1000. A thunk subtracting 32 before accessing receiver+0x38 then
accesses 0x1038, not 0x1058. Normalize the receiver before merging field maps.
Do not assume every negative table word is a code-relative displacement, or
that every base subobject has a distinct allocation. Conversely, plausible
arithmetic does not establish that 0x1000 is still allocated or properly typed.
Keep construction-phase and completed-object interpretations distinct.

## Thunks can adapt both receiver and result
Itanium virtual entries may target adjustment thunks; covariant-return thunks
can adjust the returned pointer as well as the incoming receiver. [1]

Constructed trace: input subobject 0x1020 becomes implementation receiver 0x1000;
the body returns a non-null complete-object pointer 0x2000; a result adjustment
of +0x18 exposes subobject 0x2018. Treating the thunk and body as identical
interfaces loses two coordinate changes. Recover adjustment instructions and
their branch conditions independently. Do not infer what a null-result path
does from this non-null example. A short jump stub is not necessarily dead code,
and two table entries reaching one body need not accept identical receivers.

## RTTI supplies type evidence, not object validation
RTTI means runtime type information. Ordinary Itanium tables include a typeinfo
component, with different secondary tables of a class referring to that class's
type information. [1]

Investigative consequence: two vptrs with matching RTTI can support a shared
complete-object hypothesis; they do not alone establish allocation identity,
subobject offset or current lifetime. A copied or stale dispatch pointer can
still refer to genuine metadata. Record the RTTI bytes and their mapping to
the table before naming a recovered type. Missing metadata in an unknown
compiler configuration leaves type recovery incomplete; do not substitute a
Microsoft Complete Object Locator parser. Runtime cast preconditions live in
reference-native-type-confusion-object-validity, not in a table-name heuristic.

## Member-function pointers are not ordinary function pointers
The Itanium standard member-function-pointer representation has pointer and
receiver-adjustment fields; virtual encoding is one plus a table byte offset.
This rule excludes the alternate 32-bit Arm representation. [1]

Constructed standard-representation x64 case: ptr=17, adj=32 and receiver=0x1000
select the vptr of adjusted receiver 0x1020, then the entry at byte offset 16
from its address point. With eight-byte function entries this is slot index 2.
The value 17 is not a direct code address. Do not apply that decoding to a
Microsoft member pointer or infer validity merely from its low bit. Preserve
both fields, the verified encoding and the selected object lifetime when
following a stored callback. Use abi-microsoft-cpp-dispatch-rtti for that family.

## Sources and boundaries
1. [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html), rolling specification reviewed 2026-10-02: sections 2.3.2, 2.5.1-2.5.3 and 2.6. Target ABI variants require separate confirmation.

Examples are constructed coordinate checks, not compiler reproductions.
Lifecycle rules and destructor variants: reference-native-cpp-lifecycle-unwind.
Investigation workflow: playbook-re-recover-cpp-lifecycle.
