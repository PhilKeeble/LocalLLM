---
id: vulnerability-impact-execution-sink-and-code-loading-chain
title: Data-only, interpreter, deserialization and code-loading execution chains
kind: vulnerability
topics: [rce, data-only, injection, deserialization, code-loading, jit, executable-memory]
platforms: [cross-platform]
architectures: [any]
---

# Data-only, interpreter, deserialization and code-loading execution chains

## Data-only policy or control corruption

A data-only chain changes security-bearing state without immediately redirecting machine control flow. Prove the root write or semantic corruption reaches the exact policy, identity, length, object binding, state-machine value, or operation parameter later consumed under a sensitive authority. The primitive is the unauthorized effect, even when all branches target legitimate code.

An adjacent flag, role string, count, or object identifier is not sufficient until its consumer and effective policy are recovered. Control-flow integrity can leave data-only attacks in scope because it constrains transfers rather than the correctness of ordinary data.

## Command, expression or template engine execution

An injection-to-execution chain requires less-trusted data to cross a structural boundary and become syntax for the selected shell, expression language, template engine, query engine, or evaluator. Recover decoding, quoting, concatenation, parser mode, evaluation API, variable bindings, and the final operation. A dangerous API name or metacharacter is insufficient when input remains a data argument or the path is unreachable.

State the first achieved primitive: command execution, expression access, template-side object traversal, file operation, or another engine capability. Process execution additionally depends on the engine's exposed functions and the consumer's authority.

## Deserialization callback or gadget execution

A deserialization chain requires attacker influence over the consumed bytes or type metadata, an effective serializer/type-resolution policy admitting the relevant types, and a reachable sequence of construction callbacks, setters, converters, or methods that produces a security-sensitive side effect. The presence of a serializer or known gadget class alone is not a chain.

Validation after reconstruction cannot prevent side effects that already ran, but a callback is not inherently dangerous. Reconstruct order, controlled members, loaded code identity, exception handling, and the process authority, and stop at the strongest demonstrated operation.

## Untrusted library, plugin, module, bytecode or update activation

An activation chain exists when a less-trusted actor controls the exact bytes selected as executable library, plugin, module, script, bytecode, native cache, or update and the consumer loads or executes them without the required origin, integrity, identity, or authorization binding. File presence or a writable search directory is insufficient without selection and activation.

Trace name/path resolution, namespace and architecture, signatures or hashes, redirects and caches, replacement races, loader configuration, compatibility checks, and the executing process. Valid signatures prove only what the verification policy and signed scope establish; they do not automatically authorize a component for every consumer or role.

## Writable-to-executable or generated-code transition

A W^X/JIT chain requires controlled bytes to become instructions in a mapping that the processor can execute, or controlled inputs to make a code generator emit unintended instructions. Recover mapping identity, write source, cache coherency requirements, permission transitions, code-signing/JIT entitlement, entry target, and actual transfer. A writable mapping and a separate executable mapping are relevant aliases only if they cover the same physical backing and the attacker can bridge them.

Generated code and private executable memory are normal in many runtimes. A JIT API, `mprotect`, `VirtualProtect`, or executable allocation is not a vulnerability without unauthorized byte influence and execution under the stated policy.

## Constructed loader chain

```c
void *module = dlopen(plugin_name, RTLD_NOW);
void (*run)(void) = (void (*)(void))dlsym(module, "run");
run();
```

This hypothetical code is vulnerable only if a less-trusted actor controls resolution of `plugin_name` to unapproved bytes, loading succeeds, `run` resolves, and the call is reachable. A fixed absolute path can still be unsafe if the selected object is replaceable; a relative name can be safe under a trusted, fixed search configuration. Apply the platform loader contract.

## Impact limits and primary sources

Report the exact execution engine or activated code and the authority it receives. Remote code execution additionally requires a remote input path through all intervening authentication, framing, configuration, and state gates. Reviewed 2026-10-09 against POSIX [`exec`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/exec.html) and [`dlopen`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/dlopen.html), Microsoft [`LoadLibraryEx`](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibraryexw) and [`VirtualProtect`](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualprotect), Apple [hardened runtime](https://developer.apple.com/documentation/security/hardened-runtime), WebAssembly [validation](https://webassembly.github.io/spec/core/valid/index.html), and the serializer-specific primary sources in the linked vulnerability profiles. Loader, engine, and signing rules are platform-specific.
