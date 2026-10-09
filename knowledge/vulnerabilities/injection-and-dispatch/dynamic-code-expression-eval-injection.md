---
id: vulnerability-injection-dynamic-code-expression-eval
title: Code, expression, or eval injection in scripting and embedded runtimes
kind: vulnerability
topics: [injection, eval, scripting, expressions, runtimes, dynamic-code]
platforms: [cross-platform]
architectures: [any]
---

# Code, expression, or eval injection in scripting and embedded runtimes

## Definition and violated invariant

Dynamic-code injection occurs when attacker-controlled data is parsed as source code or as an expression language whose reachable operations exceed the intended data-only policy. The accepted grammar, names, objects, functions, side effects, resource limits, and authority must match the caller's intended expression capability.

The boundary includes direct `eval` or `exec`, embedded script engines, rule and formula evaluators, debugger expressions, configuration expressions, reflection-driven invocation, and generated source later compiled or interpreted. A restricted expression grammar can still expose dangerous object traversal or callable capabilities; an API name alone does not determine the available authority.

## Conditions that establish the issue

Recover input construction, decoding and template stages, selected language and mode, compilation and execution APIs, global/local scope, built-ins, registered host objects and functions, import or module access, reflection, filesystem/network/process capabilities, resource controls, and execution identity. Prove attacker-controlled syntax reaches the parser and selects an unintended operation or capability.

For a purported sandbox, establish the actual reachable object graph and engine restrictions at the call site. A string filter is relevant only under the exact grammar and transformations that follow it.

## Evidence that is not sufficient

An `eval` symbol, script engine, expression parser, dynamic language, template, or user-authored formula is not sufficient. The call may be unreachable, input may be fixed, the grammar may be data-only, or the execution environment may expose only the intended bounded operations.

Parsing success is not code execution, and an exception does not prove that earlier callbacks or side effects were absent. Trace execution and effects.

## Investigation sequence

Identify the exact source text or bytecode supplied to the engine and mark attacker-controlled spans. Recover parse mode, namespace construction, host bindings, lookup fallbacks, callbacks, compilation cache, exception path, timeout or work limits, and subsequent use of the result. Enumerate reachable capabilities from the objects actually exposed rather than from language defaults alone.

At binary boundaries, recover the runtime API prototype, source length and encoding, context or realm, flags, and returned value or exception. Follow indirect dispatch through registered native callbacks and confirm their argument and authority contracts.

## Constructed expression example

```python
expression = request["calculation"]
result = eval(expression, application_globals, record_locals)
store_result(result)
```

If `application_globals` exposes functions or objects with filesystem, process, network, reflection, or import capability, the submitted expression can select those capabilities rather than merely calculate over `record_locals`. The finding requires actual reachable names and a successful effect; the presence of `eval` does not identify which operations the supplied namespaces permit.

## Primitive and impact limits

The direct primitive is attacker influence over executable syntax or an expression operation under the engine's exposed capability set. Consequences range from policy bypass or data access to resource exhaustion, host callback invocation, native extension reachability, or code execution. Host compromise depends on sandbox boundaries, native interfaces, process authority, and containment.

## Related knowledge and primary sources

Runtime dispatch, foreign-code, and generated-code references provide deeper implementation evidence. This profile keeps grammar reachability and exposed-capability proof local.

Reviewed 2026-10-09 against Python's [`eval` and `exec` documentation](https://docs.python.org/3/library/functions.html#eval), ECMAScript [`eval`](https://tc39.es/ecma262/multipage/global-object.html#sec-eval-x), and Lua's [`load`](https://www.lua.org/manual/5.4/manual.html#pdf-load) for distinct dynamic-execution contracts. The example is constructed and does not generalize one runtime's sandbox behavior to another.
