---
id: vulnerability-injection-dynamic-library-plugin-module-name
title: Dynamic library, plugin, module, class, or script-name injection
kind: vulnerability
topics: [injection, libraries, plugins, modules, classes, scripts, dynamic-loading]
platforms: [windows, linux, macos, ios, android, freebsd]
architectures: [any]
---

# Dynamic library, plugin, module, class, or script-name injection

## Definition and violated invariant

Dynamic-loading injection occurs when attacker-controlled data selects a library, plugin, module, class, package, script, symbol, or entry point outside the caller's intended closed set. The selected identity, resolution context, origin, integrity and callable interface must be bound to the authorized component before loading or invocation.

Name injection differs from search-path hijacking: direct control of the requested logical name can be unsafe even when every search directory is trusted, while a fixed trusted name can be hijacked through unsafe resolution. Native loaders, managed reflection, package importers, plugin registries, and script runtimes use different naming and initialization contracts.

## Conditions that establish the issue

Recover the attacker-controlled name or identifier, normalization, aliases, extension or prefix addition, architecture, loader/import/reflection API, search and resolver context, package or assembly identity, signature/integrity policy, initialization side effects, exported symbol or class selection, interface validation, and execution identity. Prove the controlled name resolves to an unauthorized component or callable target and reaches a security-relevant load or invocation.

Account for code that runs during load, module initialization, class initialization, constructors, registration, or import before an explicit entry point. Establish actual resolution and load success rather than inferring from a requested name.

## Evidence that is not sufficient

A dynamic-loader import, plugin directory, class name, reflection API, module string, writable file, or successful library open is not sufficient. The name may be fixed or allowlisted, the resolver may bind a trusted identity, signature policy may reject the candidate, or no relevant initializer or exported operation may run.

Loading a data-only package or resolving a class object is not automatically code execution; recover the mechanism's initialization and invocation contract.

## Investigation sequence

Trace the requested logical name from input through normalization, aliases, manifest or registry mapping, search order, candidate probing, architecture selection, integrity checks, and final object identity. Record every candidate and the reason it was selected or rejected. Follow load-time callbacks and the exact symbol, class, method, or script entry invoked.

At binary level, recover loader call prototypes and flags, string encoding, returned handles, error checks, symbol lookup, indirect calls, and unload/lifetime behavior. In managed code, inspect assembly/module contexts, type resolution and static initialization separately.

## Constructed native-plugin example

```c
string library_name = request["renderer"];
module_handle module = load_library(library_name);
render_fn render = resolve_symbol(module, "render_document");
render(job);
```

If `renderer` can select any resolvable module, the requester controls both load-time initialization and the implementation behind `render_document`. The finding requires the target loader's actual resolution, a successful unauthorized module load, compatible symbol resolution, and the reachable call. A closed mapping from public renderer IDs to verified module identities changes the conclusion.

## Constructed indirect-call shape

```asm
; Illustrative Windows x64-like shape after a successful loader call.
mov     rcx, rax                ; module handle
lea     rdx, [render_name]
call    resolve_symbol
test    rax, rax
jz      .fail
mov     rcx, rbx                ; job pointer
call    rax                     ; implementation selected through loaded module
```

This shape establishes indirect invocation through a resolved symbol only after the helper contracts and returned module identity are known. It does not prove the module name was attacker-controlled, that load-time initialization occurred under a particular OS loader, or that the callee is unauthorized.

## Primitive and impact limits

The direct primitive is attacker selection of a loadable component or callable implementation. Consequences can include code execution, alternate policy implementation, data access, persistence, or denial of service under the loading process's authority. Platform signature rules, sandboxing, loader namespace, architecture compatibility, and available trusted modules constrain impact.

## Related knowledge and primary sources

Loader-resolution, process, managed-runtime, and code-provenance references provide deeper identity and execution evidence. This profile keeps logical-name control separate from search-path control.

Reviewed 2026-10-09 against Microsoft [`LoadLibraryEx`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw) and [dynamic-link search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order), POSIX [`dlopen`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dlopen.html), Java [`Class.forName`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Class.html#forName(java.lang.String)), and Python [`importlib`](https://docs.python.org/3/library/importlib.html). The API names, source, and assembly are constructed abstractions.
