---
id: vulnerability-filesystem-search-path-executable-library-plugin-hijacking
title: Executable, library, or plugin search-path hijacking
kind: vulnerability
topics: [filesystem, search-path, dll, shared-libraries, plugins, process-creation]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Executable, library, or plugin search-path hijacking

## Definition and violated invariant

Search-path hijacking occurs when a fixed or partially qualified executable, library, dependency, plugin, script or helper name resolves to an attacker-controlled object before the intended trusted object. Every resolution edge must bind the requested name to an authorized file under the actual loader, process, activation, environment and namespace context.

Top-level selection and dependency selection are separate. A fully qualified parent module can still have name-based dependencies; an already loaded module, platform-known library, activation context, package graph or cache can resolve before ordinary directory search. Search rules differ across Windows application types and configurations, Linux loaders, macOS dyld, Android and custom plugin systems.

## Conditions that establish the issue

Recover the requesting component, exact name, whether it contains a path separator, loader/process API and flags, applicable search strategy, current/application/load directories, PATH or loader variables, manifests/activation/package context, already loaded objects, dependency graph, secure-execution state, candidate order, directory/file mutation rights, architecture, integrity/signature policy, selected file identity, initialization and invoked symbol. Prove an attacker-controlled candidate is selected and reaches a security-relevant load or execution effect.

Analyze each dependency edge from its own requester. A safe root executable directory does not establish that every child dependency resolves there.

## Evidence that is not sufficient

An unqualified name, writable directory, PATH entry, DLL import, missing file, planted candidate, loader call, or successful module load is not sufficient. An earlier trusted match may win, policy may reject the file, architecture may be incompatible, or the loaded module's relevant code may not execute.

Safe-search configuration intent is not effective state unless setup succeeded before the load and no per-call or fallback path changed it.

## Investigation sequence

Build a resolution record for each executable or dependency: requester, requested bytes, API/flags, process and activation state, ordered candidates, rejection reasons, selected identity and permissions. Trace setup calls and results, environment and working-directory changes, fallback loaders, delay loading, plugin registries and dependency recursion. Follow initialization and the actual resolved function or entry call.

At binary level, recover whether the name is full or relative, loader flags, setup return checks, imported versus runtime resolution and indirect calls. Compare the historical selected bytes, not a later file with the same path.

## Constructed Windows DLL example

```c
HMODULE module = LoadLibraryW(L"codec.dll");
decode_fn decode = (decode_fn)GetProcAddress(module, "decode_frame");
decode(frame);
```

The unqualified name requires Windows loader resolution under the process's effective search and activation state. This is a vulnerability only if a directory reached before the intended `codec.dll` is attacker-writable, the attacker candidate is compatible and accepted, and its initialization or resolved function executes. The call alone cannot establish the candidate order or selected file.

## Primitive and impact limits

The direct primitive is substitution of an executable component or dependency selected by name. Consequences commonly include code execution under the loading process, persistence, policy substitution, or denial of service. Search configuration, protected directories, signatures, architecture, already loaded objects, sandboxing and process authority bound impact.

## Related knowledge and primary sources

`reference-windows-dll-plugin-resolution-activation`, `reference-linux-loader-selection-context`, `format-elf-dynamic-linking`, and Mach-O loader references provide platform resolution details. This profile repeats selected-object and executed-code requirements locally.

Reviewed 2026-10-09 against Microsoft [Dynamic-link library search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order), [`LoadLibraryW`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryw), and [`LoadLibraryExW`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw), Linux [`ld.so`](https://man7.org/linux/man-pages/man8/ld.so.8.html), POSIX [`dlopen`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dlopen.html), and Apple's [`dyld` manual source](https://raw.githubusercontent.com/apple-oss-distributions/dyld/main/doc/man/man1/dyld.1). The source is constructed and does not assert one universal search order.
