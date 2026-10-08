---
id: format-elf-dynamic-linking
title: ELF relocations, dynamic symbols, initialization and Linux loader resolution
kind: reference
topics: [elf, relocations, got, plt, dynamic-linking, symbol-versioning, ifunc, loader]
platforms: [linux, android, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# ELF dynamic-linking evidence

## ELF dynamic entries and startup paths

PT_DYNAMIC locates tagged entries. Distinguish d_ptr addresses from d_val
integers/string-table offsets; DT_NEEDED is a dependency name offset, not a
pointer to loaded code. Bound tables, strings and entry sizes. DT_INIT and
DT_INIT_ARRAY identify initialization functions, and DT_FINI/DT_FINI_ARRAY
termination functions. Array sizes are byte counts, not element counts. [1]

Investigation: include initialization and runtime loading when tracing entry
paths. An import name establishes a potential dependency, not execution of a
specific operation. Termination hooks are not guaranteed after every kind of
process exit. Function-pointer representation depends on the psABI. [1]

## ELF REL, RELA and RELR relocations

REL obtains an implicit addend from the relocation site; RELA carries an
explicit r_addend. r_offset is section-relative in ET_REL but a virtual address
in ET_EXEC/ET_DYN. r_info selects symbol and processor-specific operation;
use the correct psABI formula and field width. RELR compactly encodes locations
for relative adjustment, not arbitrary named-symbol relocations. [2]

Investigation: preserve the site, original bytes, relocation type, addend,
resolved symbol and load bias. An encoded addend is not necessarily a live
pointer. Reconstruct relocation effects before treating a disk/runtime pointer
difference as tampering or corrupted control flow.

## ELF GOT/PLT: indirect calls and lazy symbol resolution

The ELF global offset table (GOT) and procedure linkage table (PLT) support
ABI-specific address references and calls between objects. ABI means the binary
interface contract; a psABI is its processor-specific supplement.
Relocation type and binding mode determine when a slot is resolved. A slot
may initially lead into linker resolution code rather than the final function.
Lazy binding defers resolution until use; eager binding resolves it during loading.
DT_BIND_NOW or applicable binding flags request eager relocation. Exact stub
instructions and GOT layout are architecture-specific. [1]

For an indirect call, trace the actual slot, its relocation and the observed
resolved target. Follow that target's module identity. Neither a PLT label nor
a library basename proves which implementation executed. Static and live
addresses must use the mapping rules in `format-elf-structure-addresses`.

## ELF constructor and destructor ordering

For ELF's generic initialization contract, DT_PREINIT_ARRAY belongs to an
executable and precedes shared-object initialization; it is ignored in shared
objects. Within one object, DT_INIT precedes forward-order DT_INIT_ARRAY.
DT_FINI_ARRAY runs in reverse order before DT_FINI. Dependency initialization
precedes the dependent object's initialization; cycles do not supply a defined
total order. [1]

Constructed case: a validation flag is set by one constructor but read by another.
Establish the actual dependency/order and loader implementation before asserting
the flag must already be set. A symbol named main is not the first possible
application-controlled code. These rules do not guarantee cleanup after abrupt
termination or cover every language runtime's separate registration mechanism.

## ELF TLS template is not a process-global variable

TLS here means thread-local storage, not the network security protocol.
Each thread has its own instance. PT_TLS identifies the initialization template
and total per-thread storage requirements. SHF_TLS distinguishes TLS sections;
STT_TLS values in an executable
or shared object denote TLS offsets, not ordinary process virtual addresses.
Module identity and the selected thread's TLS state are needed to obtain the
live address. [5][6]

Constructed case: st_value=0x18 does not mean load_bias+0x18 points to the current
thread's variable. The initialized template can differ from a thread's current
copy. Record thread, module, access sequence and offset; a thread pointer or
TLS helper call is not automatically an application object. Likewise, thread-local
storage is not inherently request-local state when a worker handles many clients.

## ELF thread-local storage access models and transformed sequences

The traditional ELF models distinguish general/global-dynamic module+offset
resolution, local-dynamic module-base resolution plus a known local offset,
initial-exec runtime-fixed thread-pointer offset, and local-exec link-time-known
thread-pointer offset. Register, relocation and helper conventions are psABI-
specific. Drepper's version 0.21 describes these models, not every newer TLS
descriptor encoding or loader allocation policy. [6]

GCC's -ftls-model choice can be optimized to another model. [7] Thus a missing
__tls_get_addr call does not rule out TLS after compiler/linker transformations.
Identify the final instruction/relocation sequence, not only a build option.
For TLSDESC or late-loaded static TLS, obtain the target's psABI/loader contract;
do not generalize a historical model restriction into universal dlopen failure.

## GNU symbol-version tables and local indexes

GNU-style SHT_GNU_versym entries correspond to dynamic-symbol entries; version
definitions and requirements use SHT_GNU_verdef and SHT_GNU_verneed. Version
numbers in these tables identify strings within the object, not a globally
ordered library release number. The same numeric index in two files need not
mean the same version. [8]

In glibc 2.42 dl-version.c, version indexes are masked with 0x7fff and a high
bit is tracked separately as hidden metadata. [9] Do not confuse that bit with
ELF st_other visibility or use an unmasked value as an array index. Preserve
symbol spelling, required/defined version string, dependency and selected scope.
Version metadata is ABI association evidence, not authentication or proof that
a specific implementation executed.

## Linux glibc loader search-path evidence

The following search behavior is Linux/glibc ld.so-specific, not a universal
ELF/Android/FreeBSD rule. A dependency containing a slash is a pathname. For a
name without a slash, the documented sequence includes applicable DT_RPATH
when no DT_RUNPATH exists, LD_LIBRARY_PATH outside secure execution,
DT_RUNPATH, cache and default paths, subject to loader options. RUNPATH applies
to direct dependencies; RPATH has different descendant scope. $ORIGIN expands
relative to the containing program/shared object. [3]

Secure-execution mode suppresses or restricts several environment controls.
Record AT_SECURE, credentials, loader build, namespace, effective environment,
resolved path and directory permissions. A writable directory string is only a
lead: establish that the relevant lookup can actually select an attacker-owned
object under the target execution conditions. [3]

## Linux symbol lookup, versions and GNU IFUNC

On Linux, dlsym looks up a symbol by name; its handle/scope affects which
definition is found. Lookup scope is the set and order of candidate objects;
RTLD_DEFAULT and RTLD_NEXT are not interchangeable. dlvsym adds an explicit
version string. Preserve symbol version as well as spelling and owning module.
GNU IFUNC resolution can select an implementation through a resolver, so the
resolver and eventual callable target can differ. [4]

For dlsym, a NULL value alone does not establish a lookup error: clear dlerror,
perform lookup, then save/check dlerror. An IFUNC resolver may legitimately
produce NULL without a lookup error; that still does not make NULL callable.
Review the consumer's failure path and indirect call. [4]

## GNU IFUNC resolver timing and repeated invocation

GNU STT_GNU_IFUNC identifies a resolver, whose returned address supplies the
implementation. In glibc, non-lazy references can resolve during startup or
dlopen relocation before constructors; a lazy PLT reference can defer resolution
until a call. A resolver can run more than once, including concurrent lazy
resolution. [10] Do not model its body as the ordinary exported function body
or assume every resolver runs exactly once after global initialization.

The inspected rolling glibc manual labels some expanded resolver-environment
guarantees as since 2.44. Those labels must not be applied to earlier target
libraries. Match the actual release before assuming TLS, other objects' data,
stack protection or library calls are usable. Resolver identity, invocation
context and returned implementation are three separate pieces of evidence.

## Constructed loader investigation

Hypothesis: a privileged program loads a helper named by a configuration field.
First locate the load operation and show field control. Then determine whether
the name is a path, the effective search namespace, secure-execution behavior,
and the selected file's identity/permissions. Finally trace exported symbol
lookup and the call. A dependency-list entry alone leaves these edges unproved.

Compare the same target build and environment when reproducing resolution.
Android bionic, musl, FreeBSD rtld and custom loaders need their own contracts;
the Linux/glibc paragraph must not be used to clear their search paths.

## Sources and review

Reviewed 2026-10-02. Generic format sections use ELF 4.3 DRAFT. Linux API/search
sections use man-pages 6.19; no target loader was executed in this review.

1. [ELF dynamic linking](https://gabi.xinuos.com/elf/08-dynamic.html): tagged entries, GOT/PLT, binding and initialization.
2. [ELF relocation](https://gabi.xinuos.com/elf/06-reloc.html): REL/RELA sites/addends and RELR encoding.
3. [Linux ld.so](https://man7.org/linux/man-pages/man8/ld.so.8.html): lookup order, dynamic tokens and secure execution.
4. [Linux dlsym/dlvsym](https://man7.org/linux/man-pages/man3/dlsym.3.html): lookup scope, versioned lookup, NULL and IFUNC caveats.

## Primary TLS and versioning sources

Reviewed 2026-10-02. Historical TLS exposition supplies model distinctions, not
current platform-wide restrictions; glibc source observations are release-pinned.

5. [ELF symbols](https://gabi.xinuos.com/elf/05-symtab.html): STT_TLS offsets.
6. [Drepper, ELF Handling For Thread-Local Storage](https://www.akkadia.org/drepper/tls.pdf), version 0.21, August 22, 2013: sections 2-4, 5; template, runtime identity, access models and relaxation.
7. [GCC code-generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html): -ftls-model and optimization qualification.
8. [LSB 5.0 symbol versioning](https://refspecs.linuxfoundation.org/LSB_5.0.0/LSB-Core-generic/LSB-Core-generic/symversion.html): table association and object-local indexes.
9. [glibc 2.42 dl-version.c](https://raw.githubusercontent.com/bminor/glibc/glibc-2.42/elf/dl-version.c): masked indexes and version requirements.
10. [GNU C Library indirect functions](https://www.sourceware.org/glibc/manual/latest/html_node/Indirect-Functions.html): rolling manual inspected 2026-10-02; resolver timing/repetition and explicitly versioned guarantees.
