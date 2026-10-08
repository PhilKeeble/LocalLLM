---
id: format-debug-information-build-matching
title: PDB, DWARF, build IDs and dSYM matching evidence
kind: reference
topics: [debug-symbols, pdb, dwarf, build-id, dsym, symbolication, evidence]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Debug information and build matching

## Scope and identity record
Reviewed 2026-10-02. Debug metadata associates machine locations with names,
types, source and variable descriptions; it is evidence from a producer, not
a replacement for the executed instructions. Preserve executable hash, loaded
module base/ranges, architecture/slice, OS build, debug-file hash, matching IDs
and debugger load diagnostics. A matching basename, product version or timestamp
alone is insufficient association for the formats below.

Matching metadata IDs does not authenticate origin or prove runtime bytes are
unchanged. Keep specimen provenance and code-byte comparison separate. Never
silently force mismatched symbols into an investigation and then treat inferred
field offsets or source lines as facts about the target.

## Windows CodeView and PDB association
Modern RSDS CodeView records carry a 16-byte signature/GUID, age and PDB filename;
older NB10 uses a different layout including a 32-bit signature. Decode the
record kind before applying offsets. [1] PDB GUID and age are used together
for executable matching; incremental linking can retain GUID while changing
age. [2] DIA's loadAndValidateDataFromPdb checks supplied signature information
and age; age is not necessarily a wall-clock time. [3]

Constructed case: two PDBs share a GUID but have ages 3 and 4; an executable
requesting age 4 is not matched by filename plus GUID alone. The embedded path
is a discovery hint, not permission to trust or fetch an arbitrary external file.
Record whether symbols were rejected, partially loaded or explicitly forced.

## PDB streams and available evidence
LLVM's documented PDB representation uses an MSF multi-stream container; stream
blocks need not be contiguous. Stream 1 provides PDB identity/named-stream
information; TPI/IPI, DBI and symbol streams provide distinct type, module and
symbol information. [4] Do not parse a stream-relative offset as a raw file
offset without its block mapping.

For investigation, distinguish an export name, public symbol, private type,
source-line record and local-variable location. One available name does not
prove that full type or local-variable information is present. If types are
missing, retain that uncertainty instead of importing a same-named type from
another build. A malformed PDB is also untrusted parser input.

## ELF separate debug links and build IDs
GDB supports separate debug files associated by build ID or .gnu_debuglink.
The latter contains a filename, alignment padding and a CRC of the debug file;
the CRC uses the executable's byte order in the section. Build-ID lookup uses
the identifier, not necessarily a section with a particular name, and can
search .build-id/xx/rest.debug paths. [5]

Stripped and separate-debug artifacts can intentionally share an ID while
having different full-file hashes. Do not reject that expected difference as
tampering, or interpret the ID as a guarantee that a subsequently patched image
still agrees with its symbols. Preserve load bias separately from symbol identity.
Offline operation requires the needed debug artifacts to be locally available;
automatic server discovery is not evidence that they are already in the library.

## DWARF units, widths and variable locations
DWARF entries have tags/attributes and references describing entities and scope.
DWARF32 versus DWARF64 selects debug-section length/offset encodings, not target
pointer width; the unit's address_size is separate. Version and unit type govern
header interpretation. [6]

Location lists can select different variable locations for different PC ranges;
pieces can describe one value in several places. A location valid at an earlier
PC is not necessarily valid at the stop being examined. [6] Thus a debugger's
unavailable variable is not proof of an uninitialized machine read. Preserve
actual instruction definitions/uses and scope instead of treating a reconstructed
source variable as one permanent stack slot.

## Split DWARF association
In DWARF 5, skeleton and corresponding split compilation units share dwo_id;
DW_AT_dwo_name identifies the separate object path. Matching the filename alone
does not establish that the split unit belongs to the skeleton. [6] The program
may run while analysis lacks required split debug information.

Constructed investigation: symbols resolve function names but local types fail
because the referenced split unit is absent or mismatched. This is a debug
artifact problem, not proof that the executable's type layout is corrupt.
Record missing .dwo/.dwp or supplementary artifacts and the producer/consumer
versions; older split-DWARF extensions can differ from the DWARF 5 contract.

## Apple dSYM, UUID and architecture slice
Apple associates a built Mach-O image and its dSYM using a build UUID. Symbolication
requires the corresponding architecture slice and image load address/slide;
each loaded binary/framework needs its own matching information. Apple's
symbolication documentation describes matching image UUIDs and selecting the
corresponding architecture. [7][8]

Constructed case: an arm64 application and an x86_64 simulator build have the
same display version but are not interchangeable symbol sources. A dSYM directory
name does not establish a UUID match. Preserve the crash report's image UUIDs,
architecture and load ranges; do not subtract another image's slide. System
framework symbols must correspond to the reported OS build, not merely the app.

## Mismatch consequences and safe consumption
Incorrect symbol association can invent function boundaries, prototypes, field
offsets or cleanup paths and thereby create false vulnerability evidence.
Countercheck important types/addresses against bytes and ABI rules even when
debugger symbol loading succeeds. A source-line label can represent optimized
or inlined code rather than a distinct physical stack frame.

GDB can automatically execute associated command/extension files and warns
about untrusted inputs. Its auto-load controls and safe-path policy are separate
from symbol identity checks. [9] Do not disable those protections globally merely
to remove a warning. For an offline/untrusted specimen, explicitly control script
loading, network symbol discovery and the analysis environment; symbol parsing
itself is not a sandbox guarantee.

## Primary format sources
Reviewed 2026-10-02. PDB implementation observations use LLVM documentation and
the pinned 21.1.0 CodeView header; DWARF facts use Version 5, February 13, 2017.

1. [LLVM 21.1.0 CodeView debug-record layouts](https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-21.1.0/llvm/include/llvm/Object/CVDebugRecord.h).
2. [LLVM PDB info stream and matching](https://llvm.org/docs/PDB/PdbStream.html).
3. [Microsoft DIA loadAndValidateDataFromPdb](https://learn.microsoft.com/en-us/visualstudio/debugger/debug-interface-access/idiadatasource-loadandvalidatedatafrompdb?view=vs-2022).
4. [LLVM PDB container/streams](https://llvm.org/docs/PDB/index.html).
5. [GDB separate debug files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html).
6. [DWARF 5](https://dwarfstd.org/doc/DWARF5.pdf): §§2.3, 2.6, 3.1.2, 7.4–7.5; printed pp.24, 38–43, 67, 196–201.

## Primary symbolication and safety sources
Reviewed 2026-10-02. WWDC21 is used for symbol/address concepts, not current
App Store download procedures or changing debugger UI.

7. [Apple symbolication documentation](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report).
8. [Apple WWDC21: Symbolication beyond the basics](https://developer.apple.com/videos/play/wwdc2021/10211/).
9. [GDB auto-loading](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading.html)
   and [auto-load safe paths](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Auto_002dloading-safe-path.html).
