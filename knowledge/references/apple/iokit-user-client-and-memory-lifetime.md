---
id: reference-apple-iokit-user-client-memory
title: IOKit user-client dispatch, argument extents and shared-memory lifetime
kind: reference
topics: [iokit, user-client, driverkit, dispatch, shared-memory, descriptors, asynchronous-io]
platforms: [macos, ios]
architectures: [x86, x64, arm, arm64]
---
# IOKit request and memory evidence

## A user-client selector chooses a dispatch contract, not a universal prototype

IOConnectCallScalarMethod takes a connection, selector, scalar input count and
output count. DriverKit's user-client argument model separately describes scalar
arrays, structure objects/descriptors and asynchronous completion. [1][2]

Identify the actual kernel IOKit or DriverKit implementation and method table.
Recover scalar counts separately from structure byte extents and output capacity.
One API declaration does not validate every selector's arguments. An open
connection also does not establish authorization for all selected methods.

## Shared input needs stable content as well as a valid mapped extent

For analysis, bind memory descriptor, mapping owner, offset/length, access
direction and actual operation. Retaining or wiring pages does not by itself
make their contents immutable or validate an embedded pointer/count.

Recover what was copied or revalidated before use and who can still write the
same backing memory. Shared mappings can be intentional; a defect requires a
reachable violated requirement, not merely a mapping API. Do not use user virtual
addresses as kernel or device addresses without the translation contract.

## IOMemoryDescriptor preparation and object release are different lifetimes

Apple's archived IOKit data model balances IOMemoryDescriptor prepare with complete
for page wiring/unwiring; release does not substitute for complete. DMA-command
preparation/completion has a separate transaction role. [3]

Track retained object, mapping, outstanding I/O and completion independently,
including close/cancel/failure. Request submission is not completion evidence.
These named lifecycle concepts do not fix every driver's implementation or modern
API sequence; private structure offsets and hardware-specific DMA rules need
their own source evidence.

## Sources and scope

Reviewed 2026-10-08. [Scalar method declaration](https://developer.apple.com/documentation/iokit/1514793-ioconnectcallscalarmethod)
[1]; [DriverKit method arguments](https://developer.apple.com/documentation/driverkit/iouserclientmethodarguments)
[2], field roles; [IOKit Managing Data](https://developer.apple.com/library/archive/documentation/DeviceDrivers/Conceptual/IOKitFundamentals/DataMgmt/DataMgmt.html)
[3], prepare/complete and DMA distinctions. Archived DART-generation behavior and
numeric selector recipes are not adopted. Workflow: playbook-apple-memory-dispatch.
