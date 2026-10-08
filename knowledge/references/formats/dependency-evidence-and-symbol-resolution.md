---
id: format-dependency-evidence-symbol-resolution
title: Static libraries, dynamic dependencies, plugins and symbol-resolution evidence
kind: reference
topics: [dependencies, static-linking, dynamic-linking, plugins, symbol-interposition, evidence]
platforms: [windows, linux, android, freebsd, macos, ios]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Dependency and resolution evidence

## Different dependency views answer different questions
Reviewed 2026-10-02. Separate build inputs, recorded dynamic dependencies,
runtime-loaded modules and actually called implementations. A static archive can
contribute selected code without leaving a runtime DLL/DT_NEEDED dependency.
A plugin selected from configuration can be absent from the initial dependency
table. A module can load without its investigated export being called.

For an investigation, retain a graph edge with requester, requested name,
load/lookup mechanism, selection conditions, resolved object identity and call
evidence. An inventory tool's name list is a discovery aid, not that graph.
Unknown runtime loading does not prove no dependency; a matching library string
does not establish that its associated code survived linking or is reachable.

## Static archive selection and linker transformations
GNU ld's archive search is position-sensitive by default: unresolved references
at that point drive member extraction. Group rescanning and whole-archive options
alter selection; --as-needed can suppress dynamic dependency entries for libraries
that do not satisfy the relevant references at their position. [1]

Constructed case: a build command mentions a vulnerable library release, but the
affected object/function was not retained. Establish the actual machine-code
implementation before declaring the binary affected. Conversely, no runtime
library dependency does not exclude statically linked vulnerable code. Inlining,
dead stripping, folding and local patches complicate version fingerprints;
preserve matched bytes/semantics and uncertainty rather than assuming package
version strings describe every embedded implementation.

## Extracting an archive member does not retain every section
GNU ld --whole-archive includes every member object in the link. On supported
targets, --gc-sections separately retains input sections through roots and
relocation references; it can remove unused sections. [1] Archive extraction
and section garbage collection are different decisions.

Constructed ELF link with section GC enabled: extracted codec.o contains
separate encode and decode sections. Only encode is rooted/referenced, with
no export, retention flag or script rule keeping decode. Extraction alone
does not establish decode survives in the output. Inspect final bytes/symbols,
link maps or discarded-section evidence before attributing decode's behavior.
Conversely, if both functions share a retained input section, section-level
GC need not remove the unused function. Retention still does not prove a
feasible runtime path. For signature/version uncertainty, use
reference-native-library-signatures-templates.

## Direct dependencies are not the complete loaded closure
ELF DT_NEEDED, PE import/delay-import metadata and Mach-O load commands identify
different recorded edges. See `format-elf-dynamic-linking`,
`format-pe-directories-loader-metadata` and `format-macho-mapping-dyld` for those
formats. Recursively inspect selected dependency objects, preserving their own
search context; do not resolve every child relative to the root executable.

Runtime loaders, plugin registries, scripting hosts and explicit symbol lookups
add edges conditionally. Dependencies can also fail to load. A static dependency
listing from the analyst machine is not proof of the deployed selection: retain
target architecture, loader, namespace, environment, package context and file
identity. Do not silently substitute a host library for a missing target artifact.

## Linux/glibc lookup scope is not a sandbox
Linux dlopen's RTLD_GLOBAL makes symbols available to subsequent loads;
RTLD_LOCAL limits that exposure but can be promoted through later loading.
glibc dlmopen can create a separate link-map namespace. [2] These symbol-scope
mechanisms are not process-memory isolation for untrusted native code.

For interposition, trace the requesting relocation/lookup, symbol/version,
visibility, handle/namespace and actual target. Loading a library file does not
guarantee every same-named reference resolves inside it. RTLD_DEEPBIND and other
options can change precedence, while compiler binding decisions can remove a
lookup entirely. Apply Linux/glibc details only in that scope; Android linker
namespaces and other Unix runtimes require their own contracts.

## Plugin lifetime and initialization edges
On Linux, constructors can run before dlopen returns. dlclose decrements a
loader reference; successful return does not guarantee that the object was
actually removed from the address space. [2] Conversely, callers must not assume
a saved function pointer or callback remains valid after releasing the ownership
that kept its code loaded.

Constructed case: a plugin is loaded only to query its version. Its constructor
is still an execution edge even if the main plugin entry is never called. Track
registered callbacks, outstanding work and module ownership through unload or
reload. Reuse of a handle/address does not prove the same code generation.
Consult `reference-concurrency-cancellation-completion-shutdown` for draining
work separately from requesting cancellation.

## Safe dependency inspection is not ldd execution
Linux ldd documentation warns against using it on untrusted executables: some
versions/cases may run a supplied interpreter or the program itself. Static
inspection of dynamic metadata is a safer way to obtain direct dependency names,
but does not resolve the full runtime tree. [3]

Use a format-aware static reader in a constrained analysis environment; its
parser is still processing untrusted input. Do not load a specimen into the
analyst's process just to enumerate exports. Read-only parsing, target-loader
execution and source-code lookup are different validation methods and should be
reported separately. Controlled execution requires its own authorization and
isolation; a dependency question alone does not establish that it is necessary.

## Primary sources and related platform contracts
Reviewed 2026-10-02. GNU linker behavior is not a universal rule for every linker;
Linux API details below use man-pages 6.19. Scenarios are constructed.

1. [GNU ld options](https://sourceware.org/binutils/docs/ld/Options.html): archive selection, groups, whole-archive, gc-sections and as-needed; section-retention distinction rechecked 2026-10-02.
2. [Linux dlopen/dlmopen/dlclose](https://man7.org/linux/man-pages/man3/dlopen.3.html): namespaces, symbol scope, initialization and lifetime.
3. [Linux ldd](https://man7.org/linux/man-pages/man1/ldd.1.html): untrusted-input warning and direct-dependency limitation.

Windows selection: `reference-windows-dll-plugin-resolution-activation`.
ELF Linux/glibc search: `format-elf-dynamic-linking`.
Apple image/binding/path context: `format-macho-mapping-dyld`.
