---
id: vulnerability-external-package-source-namespace-substitution
title: Package source, namespace or dependency substitution
kind: vulnerability
topics: [supply-chain, dependency-confusion, package-manager, repository, namespace, build]
platforms: [cross-platform]
architectures: [any]
---

# Package source, namespace or dependency substitution

## Definition and violated invariant

This vulnerability occurs when package resolution can select an attacker-controlled artifact instead of the intended dependency because name, scope, repository/source, version, lock state, platform variant, or trust policy is not bound strongly enough. The invariant is that every dependency identity resolves to authorized bytes from the intended namespace and source for the exact build or install consumer.

Dependency confusion is a resolution and activation chain. A matching public package name or multiple configured sources alone does not prove the target selects or executes it.

## Conditions that establish the issue

Recover the manifest and transitive graph, package-manager and configuration, source precedence or candidate-selection rules, scoped/private namespace policy, version constraints, lockfile and integrity fields, cache, platform/architecture selection, credentials, and install/build hooks. Prove an attacker can publish or substitute a candidate that outranks or replaces the intended package and that the consumer fetches and activates it.

Account for source mapping and repository snapshots. A lockfile can bind a version yet leave source or bytes ambiguous in some ecosystems; in others it can bind integrity and eliminate the proposed candidate.

## Evidence that is not sufficient

An internal-looking name, public registry entry, wildcard version, missing lockfile, or package script is not sufficient. The name may be scoped or reserved, source mapping may exclude the public repository, the resolver may prefer a private index, integrity may be pinned, or scripts may be disabled.

Do not generalize one ecosystem's "first index," highest-version, or fallback behavior to another. Recover the actual resolver rules and command/configuration used by the affected build.

## Investigation sequence

Map each dependency name to namespace owner, allowed sources, candidates, selected version, integrity, cache entry, and final installed bytes. Include environment-specific configuration, credentials, proxies, mirrors, lock updates, and generated manifests. Follow lifecycle hooks, code generation, compiler plugins, native extensions, and runtime loading to the first effect.

For CI impact, identify the build identity, secrets and publication rights available to the selected package. A developer installation and a release build can have different sources and authority.

## Constructed resolution example

```text
manifest:       corp-parser >= 2
private source: corp-parser 2.4
public source:  corp-parser 9.0 controlled by attacker
resolver rule:  choose the highest satisfying version across all configured sources
```

Under only those stated rules, version 9.0 is selected. The example is not portable to resolvers that prioritize sources, enforce namespace mapping, or bind the dependency in a lockfile. Activation and resulting authority still require the package to be fetched and its code or hook to run.

## Primary sources and scope

Reviewed 2026-10-09 against pip's official [`pip install` source-selection and dependency-confusion warning](https://pip.pypa.io/en/stable/cli/pip_install/), NuGet [package source mapping](https://learn.microsoft.com/en-us/nuget/consume-packages/package-source-mapping), npm [package scopes](https://docs.npmjs.com/about-scopes), and [The Update Framework specification](https://theupdateframework.github.io/specification/latest/) for repository metadata principles. Each ecosystem's resolver and trust model must be applied separately.
