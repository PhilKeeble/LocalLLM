---
id: reference-android-binder-dispatch-authority
title: Android Binder and AIDL dispatch, parcels, caller identity and authorization
kind: reference
topics: [android, binder, aidl, ipc, parcels, authorization, caller-identity]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Binder request evidence

## Transaction decoding selects a method but does not authorize its effect

AIDL describes a client/service interface and generates Binder adapters. Binder
onTransact receives a transaction code, marshalled Parcel and optional reply. [1][2]

Recover the actual stub, interface version and method mapping; transaction
numbers are not universal across services. Trace decoded values, handles and
per-method validation into the effect. Successful parcel decoding or a matching
interface descriptor does not prove caller permission for the selected object.

## Remote and local calls have different execution boundaries

The app AIDL guide describes local calls executing on the calling thread and
remote calls on a receiver thread pool. A remote oneway call returns without
waiting for the method result; local oneway calls remain synchronous. [1]

Recover local/proxy selection, concurrency and reentrant call edges. Return from
submission does not establish completion, and one source method does not imply
single-threaded execution. Match detailed ordering to the actual interface/backend
rather than generalizing the Java guide to every native implementation.

## Binder UID belongs to the incoming transaction context

Binder.getCallingUid reports the incoming sender UID, or the current process UID
outside an incoming transaction. getCallingPid is unsuitable as a security
identifier because PIDs can be reused and may be unavailable for oneway calls. [2]

Bind the context to the exact request before mapping it to package/user policy.
A payload's claimed package or PID is different evidence. Possessing a Binder
reference establishes a route to requests, not authority for every method.
Identity transitions: reference-android-binder-identity-async.

## Sources and scope

Reviewed 2026-10-08. [AIDL guide](https://developer.android.com/develop/background-work/services/aidl)
[1], interface and local/remote/oneway discussion; [Binder API](https://developer.android.com/reference/android/os/Binder)
[2], onTransact and calling UID/PID. No service transaction table, private Parcel
layout, global serialization or automatic authorization assumed.
Workflow: playbook-android-service-authority.
