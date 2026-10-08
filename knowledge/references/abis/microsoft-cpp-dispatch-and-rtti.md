---
id: abi-microsoft-cpp-dispatch-rtti
title: Microsoft C++ vfptr, vbptr, RTTI coordinates and construction adjustments
kind: reference
topics: [cpp, vtables, rtti, inheritance, thunks, member-pointers]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Separate Microsoft C++ dispatch from object-location metadata

## vfptr dispatch and vbptr virtual-base lookup are different operations
Reviewed 2026-10-02. Here vfptr means a virtual-function-table pointer and vbptr
a virtual-base-table pointer. Clang 21.1.0's Microsoft ABI implementation uses a vbptr
to load an i32-offset table; virtual-base adjustment adds the selected offset
to the address of the vbptr field. [1] This is pinned implementation evidence,
not a layout guarantee for every MSVC version or ARM64EC binary.

Constructed receiver=0x1000, vbptr field offset=0x10 and selected signed table
value=0x30: the virtual base is 0x1040, not 0x1030. The vbtable entry is not a
callable function pointer. Trace the consumer: vfptr-derived values used as
indirect call targets and vbptr-derived displacements have different roles.
Do not identify them from read-only placement alone. Neither coordinate
calculation proves object validity; verify allocation, phase and the selected
entry's index range before treating the recovered subobject as usable.

## x64 RTTI mixes pointers and image-relative fields
Clang 21.1.0's Microsoft ABI places a pointer to an RTTI Complete Object Locator
before the vftable address point when RTTI data is present. In its 64-bit mode, selected
locator references are 32-bit image-relative values, including self, type and
hierarchy; the table's locator reference is a pointer. [1]

Constructed x64 loaded locator=0x140003000 and self RVA=0x3000 yield image
base=0x140000000. Type-descriptor RVA=0x5000 then resolves to 0x140005000,
not locator+0x5000. Keep pointer-sized table entries separate from 32-bit RTTI
fields. Verify the locator signature, field widths and containing image first;
a plausible recovered base is not sufficient proof of a valid RTTI graph.
For offline files, convert RVAs through PE mappings rather than dereferencing
runtime addresses; use pe-headers-sections for range and coordinate checks.

## Object locator offsets are not Itanium offset-to-top
Clang 21.1.0's Microsoft locator records the vfptr's offset within the most-derived
class and a separate construction displacement offset. [1] Do not parse it as
the Itanium table header's signed offset-to-top.

Constructed completed-object case with no construction adjustment: vfptr-bearing
subobject=0x1020 and locator offset=32 imply candidate top=0x1000 by subtraction.
Adding 32 would give 0x1040. This example does not define construction-phase
recovery: a nonzero construction displacement requires its own consumer trace.
Record whether the number came from a locator, a vbtable or an instruction;
similar-looking constants are not interchangeable base adjustments. Preserve
separate layouts when observations belong to different construction phases.

## vtordisp depends on construction and compiler configuration
Microsoft /vd controls construction displacement fields for virtual inheritance.
/vd0 suppresses them, /vd1 enables the default behavior, and /vd2 broadens their
use. A vtordisp helps calls from constructors/destructors use the appropriate
receiver adjustment. [2] Not every virtual base has such a field.

Investigative consequence: a small field read before a virtual-base receiver,
followed by subtraction from this, is a construction-adjustment candidate,
not automatically an application length or attacker-controlled offset. Prove
the writing constructor, field width, consuming thunk and build configuration.
If the value can be modified after validation or the receiver is stale, the
compiler-generated pattern does not make the use safe. /vd documentation is
not permission to assign a fixed hidden field to every recovered object.

## Member pointer shape depends on the inheritance model
Clang 21.1.0's Microsoft member-function-pointer representation starts with a
function-or-thunk pointer and adds adjustment fields according to inheritance
model. Its null function-member test uses the first field. [1]

Investigative consequence: copying only one machine pointer from an observed
multi-field member callback can discard required adjustment state. Conversely,
assuming every member pointer occupies a two-word Itanium pair can consume an
adjacent field as an invented receiver delta. Establish the producer's layout,
consumer's decoding and transferred byte count. A first-field null test does
not prove all other bytes initialized, nor do nonzero trailing bytes alone
prove a callable target. No universal Microsoft member-pointer size is given.

## Missing RTTI does not settle whether dispatch exists
MSVC /GR enables runtime type information by default; /GR- disables it. [3]
The absence of an expected type name therefore cannot by itself establish
absence of C++ objects. Investigative inference: trace actual stores of table
addresses, indirect calls and receiver adjustments independently of successful
RTTI naming. Do not fabricate a hierarchy to fill a missing descriptor.

Use reference-native-cpp-lifecycle-unwind for phase and cleanup reasoning;
abi-windows-x64 for argument registers; abi-itanium-cpp-dispatch-layout for the
separate Itanium family. These homes are not interchangeable layout templates.

## Sources and inspected implementation
1. [Clang 21.1.0 MicrosoftCXXABI.cpp](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-21.1.0/clang/lib/CodeGen/MicrosoftCXXABI.cpp): getImageRelativeConstant, getCompleteObjectLocatorType, getMSCompleteObjectLocator, getVTableAddressPoint, ConvertMemberPointerType, GetVBaseOffsetFromVBPtr, AdjustVirtualBase and EmitMemberPointerIsNotNull. Implementation reviewed 2026-10-02; examples are constructed, not MSVC execution tests.
2. [Microsoft /vd](https://learn.microsoft.com/en-us/cpp/build/reference/vd-disable-construction-displacements?view=msvc-170): construction displacement options and virtual-inheritance scope; reviewed 2026-10-02.
3. [Microsoft /GR](https://learn.microsoft.com/en-us/cpp/build/reference/gr-enable-run-time-type-information?view=msvc-170): RTTI option; reviewed 2026-10-02.
