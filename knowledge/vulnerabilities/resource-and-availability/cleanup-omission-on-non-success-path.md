---
id: vulnerability-resource-cleanup-omission-on-non-success-path
title: Resource cleanup omitted on malformed input, timeout or cancellation
kind: vulnerability
topics: [resource-exhaustion, cleanup, error-handling, cancellation, timeout]
platforms: [cross-platform]
architectures: [any]
---

# Resource cleanup omitted on malformed input, timeout or cancellation

## Definition and violated invariant

This vulnerability occurs when a malformed-input, partial-success, error, timeout, exception or cancellation path bypasses the release or rollback required for an acquired resource. The violated invariant is that every acquisition must reach exactly one terminal ownership transfer or release on every feasible path.

The retained resource can be memory, a descriptor, lock, process, transaction, reservation, mapping, pinned page or privileged capability. Double release is a separate lifetime defect.

## Conditions that establish the issue

Identify the acquisition, current owner, all exits, required release, bypass path, retained lifetime, attacker reachability and consequential limit. Prove no later owner or enclosing scope performs cleanup and that repetition or duration can exhaust a protected resource or retain security-sensitive state.

For partial success, enumerate each acquired component and rollback order. For cancellation or exceptions, apply the runtime's actual unwinding and cleanup contract rather than source indentation.

## Evidence that is not sufficient

An early return, error label, missing visible `close`, exception or canceled task is not sufficient. RAII, `finally`, deferred cleanup, transaction scope, process teardown or ownership transfer may release the resource. A cleanup function call is also not proof if it covers only a subset or can fail.

One bounded process-lifetime resource may be a quality defect without a security-relevant exhaustion path. State the repeatability and protected consequence.

## Investigation sequence

Build an acquisition ledger and annotate ownership after every successful step. Walk normal, parse-error, allocation-failure, short-operation, timeout, cancellation, exception and partial-commit edges. Match each resource to one release or explicit transfer and inspect cleanup failures.

At binary level, identify acquire calls and success predicates, then follow every return and unwind landing pad. Recover compiler-generated destructors and runtime cleanup tables before declaring an omission. For asynchronous work, determine which context owns cleanup after cancellation is requested.

## Constructed example

This hypothetical function leaks a descriptor when parsing fails:

```c
int load(const char *path) {
    int fd = open(path, O_RDONLY);
    if (fd < 0) return -1;
    if (!parse(fd)) return -1;
    close(fd);
    return 0;
}
```

The early return omits `close(fd)` if `parse` fails. A vulnerability requires attacker-reachable repetition and a consequential descriptor limit; an outer owner that closes `fd` would refute the local conclusion.

## Primitive and impact limits

Report resource units retained per trigger, lifetime, limit, cleanup elsewhere and affected scope. The direct effect is retention or incomplete rollback. Denial of service, stale authority or lockout depends on the resource; code execution requires a separate unsafe failure behavior.

## Related knowledge and primary sources

Lifetime leak and partial-commit profiles cover related ownership and state consequences. This profile keeps non-success control flow and resource release together.

Reviewed 2026-10-09 against POSIX [thread cancellation cleanup handlers](https://pubs.opengroup.org/onlinepubs/9799919799/functions/V2_chap02.html), [MITRE CWE-772](https://cwe.mitre.org/data/definitions/772.html) and [MITRE CWE-404](https://cwe.mitre.org/data/definitions/404.html). The source is constructed; language and runtime unwinding rules must be established for the target.
