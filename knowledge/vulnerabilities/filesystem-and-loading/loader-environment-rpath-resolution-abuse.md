---
id: vulnerability-filesystem-loader-environment-rpath-resolution-abuse
title: Loader environment, rpath/runpath, and dependency-resolution abuse
kind: vulnerability
topics: [filesystem, loaders, environment, rpath, runpath, dependencies, libraries]
platforms: [linux, macos, ios, android, freebsd, windows]
architectures: [any]
---

# Loader environment, rpath/runpath, and dependency-resolution abuse

## Definition and violated invariant

Loader-resolution abuse occurs when environment variables, embedded search metadata, origin-relative tokens, run-path state, loader options, dependency names, or namespace configuration cause a process to bind a dependency to an unauthorized object. Each dependency must resolve under an approved loader context to the intended component identity before its initialization or symbols are used.

The rules are loader-specific. Linux/glibc distinguishes dependencies containing slashes from searched names and applies RPATH, environment, RUNPATH, cache, default directories and secure-execution qualifications under documented conditions. RUNPATH and RPATH have different dependency scope. Apple dyld path tokens and run-path stacks, Windows loader categories, Android namespaces and other loaders require their own contracts.

## Conditions that establish the issue

Recover executable and loader identity, credentials and secure-execution state, exact dependency record, requesting object, environment and loader options, RPATH/RUNPATH or equivalent metadata, origin/loader/executable path expansion, namespace, cache and defaults, candidate directories and permissions, architecture, integrity policy, selected object, initialization, relocation/binding and called symbol. Prove attacker-controlled state causes selection and execution or security-relevant use of an unauthorized dependency.

Analyze direct and transitive dependencies separately. A run path that applies to one requester's direct dependencies cannot be assumed to govern all descendants.

## Evidence that is not sufficient

An `LD_*` or `DYLD_*` string, RPATH/RUNPATH entry, `$ORIGIN`/`@rpath` token, writable directory, dependency basename, loaded object, or privileged executable is not sufficient. Secure execution may suppress variables, another candidate may resolve first, the path may be non-writable in context, or policy may reject the file.

Presence of a dependency does not prove its initializer or suspected symbol executed. Retain load and control-flow evidence separately.

## Investigation sequence

Build one resolution record per dependency edge with requester, encoded name, token expansion, effective environment, credentials, namespace, ordered sources/candidates, rejection reasons, selected identity and symbol binding. Trace privilege transitions, wrappers, service managers, containers and fallback launches that can change effective loader state. Preserve process generation and historical bytes.

At binary level, decode dynamic/load commands and flags, distinguish RPATH from RUNPATH, recover dependency requester, and follow relocations, initialization arrays and actual indirect calls. Do not use an analyst host's resolution as target evidence.

## Constructed Linux loader example

```text
application DT_NEEDED: libhelper.so
application DT_RUNPATH: $ORIGIN/../plugins
resolved application path: /opt/product/bin/application
```

Under a loader that applies this RUNPATH to the direct dependency, `$ORIGIN` expands from the containing application and yields `/opt/product/plugins`. A hijack requires that the relevant process can be made to select an attacker-controlled compatible `libhelper.so` there and that initialization or a bound symbol executes. The metadata alone does not prove writability, selection, or execution, and another loader may apply different rules.

## Primitive and impact limits

The direct primitive is substitution of a dependency through loader context rather than explicit application-level naming. Consequences commonly include initialization or symbol execution under the process identity, persistence, policy substitution, or denial of service. Secure-execution rules, directory authority, integrity policy, architecture, loader namespaces and sandboxing bound impact.

## Related knowledge and primary sources

`reference-linux-loader-selection-context`, `format-elf-dynamic-linking`, `reference-windows-dll-plugin-resolution-activation`, and `format-macho-mapping-dyld` provide platform-specific resolution contracts. This profile keeps effective loader state and per-edge selection local.

Reviewed 2026-10-09 against Linux/glibc [`ld.so`](https://man7.org/linux/man-pages/man8/ld.so.8.html), the System V ABI [dynamic linking](https://gabi.xinuos.com/elf/08-dynamic.html), Apple's [`dyld` manual source](https://raw.githubusercontent.com/apple-oss-distributions/dyld/main/doc/man/man1/dyld.1), and Microsoft [Dynamic-link library search order](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order). The example is constructed and scoped to the loader whose rules are established.
