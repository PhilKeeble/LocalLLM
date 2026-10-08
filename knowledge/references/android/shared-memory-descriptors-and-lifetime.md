---
id: reference-android-shared-memory-lifetime
title: Android shared-memory descriptors, mutable aliases and mapping lifetime
kind: reference
topics: [android, shared-memory, descriptors, mappings, mutability, ownership, lifetime]
platforms: [android]
architectures: [arm, arm64, x86, x64]
---
# Android shared-storage evidence

## A received descriptor and a local mapping are different resources

Android SharedMemory can be passed through a parcel and mapped with a protection,
offset and length. Its name is for debugging rather than object authentication.
[1]

Recover backing identity, descriptor ownership, extent, local view and sender's
remaining access. Equal descriptor numbers in different processes do not prove
the same object. A received descriptor does not validate a nested offset/count
or authorize every use; keep object and request binding explicit.

## setProtect does not remove access from mappings already created

SharedMemory.setProtect can reduce protection for future mappings; existing
mappings retain their previous protection. [1]

A recipient's read-only view therefore does not prove immutable backing content
if another writer still has a writable mapping. Recover aliases, snapshots and
validation-to-use ordering for the actual bytes consumed. This is the named
SharedMemory API contract, not a blanket rule for every sealed-memory mechanism.

## Closing a SharedMemory descriptor does not unmap all views

SharedMemory.close closes that instance's descriptor while existing mappings
remain valid. unmap invalidates the mapped buffer and its aliases; the backing
resource persists while descriptor/mapping references remain. [1]

Track descriptor, mapping, wrapper aliases and asynchronous users independently.
Closing one owner is not proof all readers lost access. Keeping a ByteBuffer
wrapper reachable cannot make an explicitly unmapped view valid. Recover final
use and cleanup on failure/cancellation before alleging premature release.

## Source and scope

Reviewed 2026-10-08. [SharedMemory API](https://developer.android.com/reference/android/os/SharedMemory)
[1], create/map/parcel, setProtect, close and unmap descriptions. API support must
be established for the target. No private ashmem/memfd layout or assumed default
protection is imported. Workflow: playbook-android-native-evidence.
