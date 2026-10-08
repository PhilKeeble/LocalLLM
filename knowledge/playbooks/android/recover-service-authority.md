---
id: playbook-android-service-authority
title: Recover Android component, Binder, provider and HAL authority
kind: playbook
topics: [android, binder, components, providers, hal, authorization, investigation]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android request-authority investigation

## Recover the installed entry and reachable endpoint

Identify package/split, component or service instance, process and registration.
Establish effective exposure and lookup/transport policy for the actual caller.
A manifest class or service name alone does not prove a reachable operation.
Use reference-android-package-entry-evidence, reference-android-component-uri-authority
and reference-android-native-hal-boundary.

## Bind caller identity to the handling context

Distinguish Binder UID from claimed package/PID/WorkSource fields. Recover local
versus remote execution, clear/restore scopes and identity captured for queued
work. A later worker's local identity does not recover the original caller.
Use reference-android-binder-dispatch-authority and reference-android-binder-identity-async.
Preserve the target's API/backend scope rather than assuming all callbacks have
an incoming transaction.

## Trace permission and object selection into the effect

Recover per-method checks, provider read/write permission, actual URI grant,
selected path/query/handle and brokered resource. Keep user/profile and policy
generation with the request. Successful decoding or Binder access does not
authorize every object. Use reference-android-component-uri-authority and
reference-android-sandbox-policy; UID and SELinux decisions remain separate.

## Recover concurrency, completion and failure effects

Follow reentrant calls, thread-pool execution, asynchronous submission, service
death and retries. Identify accepted work and retained state before assuming an
error undoes the effect. Shared buffers and JNI callbacks need the lifetime
workflow playbook-android-native-evidence.

## Report the supported authority relation

For a candidate defect, name controlled input, reachable request, required policy,
first unsupported relation and effect. For malware, establish behavior and its
controlling principal; exported components and hardware interfaces are ordinary
platform mechanisms too. Unknown device policy/vendor implementation remains
explicit rather than generalized from AOSP source.

Reviewed 2026-10-08 against the linked primary-backed references. Conceptual
evidence workflow only; no service probing, target execution or command recipe.
