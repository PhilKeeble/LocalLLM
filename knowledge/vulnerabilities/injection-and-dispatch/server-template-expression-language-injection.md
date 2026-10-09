---
id: vulnerability-injection-server-template-expression-language
title: Server-side template or expression-language injection
kind: vulnerability
topics: [injection, templates, expression-language, server-side, runtimes]
platforms: [cross-platform]
architectures: [any]
---

# Server-side template or expression-language injection

## Definition and violated invariant

Server-side template or expression-language injection occurs when attacker-controlled text is compiled or evaluated as template or expression syntax and can select data, properties, methods, functions, includes, imports, or host capabilities beyond the intended literal content. Untrusted content must remain a template value under the selected engine rather than become the template or expression program.

Output escaping and evaluation authority are separate. Autoescaping can encode rendered values for an output context while a submitted template still invokes allowed methods or reads objects during rendering. Template syntax, sandbox behavior, loaders, globals, filters, functions, and object traversal are engine-specific.

## Conditions that establish the issue

Recover the exact engine and mode, template source origin, compile/load/render APIs, delimiter and expression grammar, context objects, globals, functions, filters, method invocation, property resolution, include/import loaders, filesystem/network/process capabilities, sandbox configuration, output autoescape context, and execution identity. Prove attacker text reaches template compilation or expression evaluation and invokes an unintended operation or reads an unintended object.

Distinguish an attacker value rendered by a fixed trusted template from an attacker-supplied template. Follow nested templates, database-stored content, localization resources, and re-rendering stages that can turn a value into source later.

## Evidence that is not sufficient

Template delimiters in input, a template engine dependency, reflected output, an error, autoescaping, or a sandbox label is not sufficient. The text may be a value only, delimiters may be inert in that position, or the context may expose only intended data and operations.

Rendered HTML/script injection and server-side template execution are different findings even when one leads to the other. Establish where evaluation occurs.

## Investigation sequence

Trace submitted bytes through storage, decoding, concatenation, template selection, compilation, inheritance/include resolution, rendering, and output encoding. Record whether each attacker-controlled span is template source, expression source, variable name, lookup key, value, or final output. Enumerate reachable objects and callable methods from the actual context.

At binary or managed-code level, recover engine entry points, source string and length, resolver or loader callbacks, context construction, sandbox flags, exception paths, and native host callbacks. Confirm the observed result or side effect rather than relying on a familiar delimiter alone.

## Constructed template-source example

```python
template_source = request["report_template"]
template = environment.from_string(template_source)
output = template.render(account=current_account, helpers=report_helpers)
```

Here the request supplies the program parsed by the template engine, while `account` and `helpers` define part of its reachable object graph. A vulnerability requires that the selected engine lets submitted syntax read or invoke something outside the intended report capability. The same text passed as a value to a fixed template would be a different boundary.

## Primitive and impact limits

The direct primitive is control over server-side template or expression evaluation under the exposed context. Consequences can include data disclosure, unauthorized method calls, file or network access, resource exhaustion, or code execution. The engine's actual sandbox, loaders, host objects, native extensions, and process authority bound impact.

## Related knowledge and primary sources

Dynamic-code, runtime dispatch, and output-context profiles cover adjacent boundaries. This profile retains the crucial distinction between template source, template values, and rendered output.

Reviewed 2026-10-09 against Jinja's [template designer](https://jinja.palletsprojects.com/en/stable/templates/) and [sandbox](https://jinja.palletsprojects.com/en/stable/sandbox/) documentation, and the Jakarta [Expression Language specification](https://jakarta.ee/specifications/expression-language/6.0/jakarta-expression-language-spec-6.0). The code is constructed; engine and integration behavior must be established for the target.
