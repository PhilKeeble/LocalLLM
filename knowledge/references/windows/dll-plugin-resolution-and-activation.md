---
id: reference-windows-dll-plugin-resolution-activation
title: Windows DLL/plugin search, dependencies and side-by-side activation evidence
kind: reference
topics: [dll-loading, plugins, search-path, manifests, activation-contexts, dependencies]
platforms: [windows]
architectures: [x86, x64, arm64]
---
# Windows library resolution

## Scope and resolution record
Reviewed 2026-10-02. A LoadLibrary/LoadLibraryEx call site does not determine
its selected DLL without the supplied name, flags and process state. Record
OS build, packaged/unpackaged status, calling image, activation context,
already loaded modules, search configuration and actual result. Retain the
selected object's path and identity, not only the requested basename.

Constructed case: an unqualified plugin name appears unsafe, but the lookup
resolves an already loaded trusted image before reaching a writable directory.
That call is not demonstrated path hijacking. Conversely, an absolute top-level
DLL path does not by itself constrain every dependent DLL. A search-path claim
must identify the particular edge where untrusted bytes can be selected.

## Default search is not one cross-version list
Windows resolves dynamic-link library (DLL) redirection, API sets, side-by-side
(SxS) redirection, already loaded
modules and KnownDLLs before ordinary directory searching in the documented
standard strategies. Packaged applications use their package dependency graph;
unpackaged search differs, including a graph step on Windows 11 build 22000 and
later. Safe DLL search mode moves the current directory later; it does not
universally remove it. [1]

Do not copy a familiar application/System32/current/PATH list onto every target.
Identify the applicable strategy and successful earlier matches. App Paths is
not the DLL PATH search list. A full path still needs applicable redirection
review, and dependencies are searched by module name under their effective
rules even when the parent DLL was named by full path. [1][2]

## Explicit directory controls and effective state
SetDefaultDllDirectories establishes process search categories used when
LoadLibraryEx supplies no LOAD_LIBRARY_SEARCH flags. DEFAULT_DIRS combines
application, System32 and explicitly added user directories, not arbitrary
current-directory/PATH searching. Added directories participate through USER_DIRS;
their order is unspecified when several are added. [3][4]

Constructed case: a restrictive setup call fails and execution continues into a
plugin load. The intended flags are not evidence of the effective policy. Check
return values, setup-before-use ordering and later per-call overrides. Capture
AddDllDirectory cookies and RemoveDllDirectory lifetimes; do not invent insertion
order as a reliable priority. Older Windows availability depends on the documented
OS/update support, so failed dynamic API discovery also needs its fallback traced.

## Per-load dependency directory is not the application directory
LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR requires a fully qualified DLL path and adds
that DLL's directory for dependency resolution. It is distinct from
LOAD_LIBRARY_SEARCH_APPLICATION_DIR. LOAD_WITH_ALTERED_SEARCH_PATH is another
strategy and cannot be combined with LOAD_LIBRARY_SEARCH flags. [2]

Constructed case: host in C:\Host loads C:\Plugins\p.dll, which needs helper.dll.
Do not substitute C:\Host for C:\Plugins when interpreting DLL_LOAD_DIR. Prove
the actual selected helper and whether the relevant directory/file can be
modified by the investigated principal. A secure parent file plus a writable
dependency location can differ from an entirely trusted dependency closure.
Compatibility, signature policy and an earlier resolved match can defeat the
candidate; record those checks instead of assuming selection from writability.

## Manifest and activation-context routing
Windows activation contexts hold manifest-derived binding information for DLLs,
COM and other side-by-side objects. ActivateActCtx pushes a context on the
current thread's activation stack; its cookie pairs with reverse-order
DeactivateActCtx. [5][6] Merely creating a context is not evidence that it was
active during the load.

For a SxS-dependent operation, recover the applicable manifest assembly identity,
version and effective activation context at the call. Trace failure and cleanup,
especially thread reuse or work handed to another thread. A manifest file on disk
does not prove that its desired redirection occurred. Do not equate SxS version
selection with object authorization or assume the same COM class name always
activates identical code under different contexts.

## Data/resource mapping versus executable loading
LoadLibraryEx data-file/image-resource modes differ from ordinary DLL execution
and initialization. If the module was already loaded as an executable DLL, the
documented behavior can instead return its existing handle and increment its
reference count. [2] Inspect flags, preexisting state and the returned mapping;
do not infer a new execution just from the API name.

Constructed case: a resource preview maps an image to read a dialog template.
This is not proof that a plugin entry was called, though resource parsing remains
an input surface. Conversely, using ordinary DLL loading solely to inspect
exports can run initialization. Perform static metadata inspection without
loading untrusted DLLs into the analyst or production process.

## Plugin trust and failure-path evidence
A plugin's registration/configuration source, resolved file, entry-point name
and interface contract are separate inputs. Follow lookup failure, alternate
directory, legacy loader and delay-import hooks; a fallback may have different
constraints from the successful primary path. See
`format-pe-directories-loader-metadata` for delay resolution.

Record accepted architecture/interface, loader result, actual function pointer,
initialization and callback lifetime. A loaded module is not proof that its
exported sensitive operation was reached. Signature success does not replace
product-specific plugin authorization. Unloading while callbacks survive is a
lifetime question, not automatically a search-order issue.

## Primary sources and applicability
Reviewed 2026-10-02. Microsoft contracts below distinguish app type, OS support
and load flags. Examples are constructed; no target loader was invoked.

1. [DLL search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order).
2. [LoadLibraryExW](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw).
3. [SetDefaultDllDirectories](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-setdefaultdlldirectories).
4. [AddDllDirectory](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-adddlldirectory).
5. [Activation contexts](https://learn.microsoft.com/en-us/windows/win32/sbscs/activation-contexts).
6. [ActivateActCtx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-activateactctx).
