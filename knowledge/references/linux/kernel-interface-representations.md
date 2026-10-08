---
id: reference-linux-kernel-interface-representations
title: Linux ioctl, user-copy, netlink, procfs and sysfs interpretation
kind: reference
topics: [linux, kernel-interfaces, ioctl, user-copy, compat, netlink, procfs, sysfs]
platforms: [linux, android]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# User/kernel request representations

## An ioctl argument needs its command and actual native or compat layout

Linux ioctl handlers can interpret an argument as a scalar or pointer according
to the command. Compat handling must preserve the user ABI; pointer/long widths
and alignment can differ from the native kernel layout. [1]

For investigation, bind device/object, command, caller ABI and selected handler
to the actual fields copied and consumed. A decompiler's native structure or a
command's apparent size is not independent validation of the request. Preserve
scalar/pointer distinction, extents, reserved fields and conversion result.
Access to a device descriptor is separate from authorization for its commands.
No raw ioctl numbers or subsystem-wide structure offsets are assumed here.

## Bulk user-copy results are uncopied byte counts

Linux copy_from_user/copy_to_user return the amount not copied; zero is success.
Single-value get_user/put_user have a different zero/negative-error convention.
User-access routines can sleep under their documented context requirements. [2]

Investigate the exact helper, extent, return and consumer. A positive bulk result
is not the number of bytes successfully copied. A checked pointer or one successful
copy does not freeze other user memory for later reads. Follow partial/error
paths, output initialization and repeated fetches without assuming every helper
has identical zero-fill behavior. Establish a violated input, lifetime or context
condition before reporting a defect; a user-copy call alone proves none.

## Netlink framing separates message extent, multipart state and family schema

Netlink nlmsg_len includes its header; streams can contain multiple messages.
Multipart termination uses NLMSG_DONE. NLMSG_ERROR carries an error structure
whose zero error value can acknowledge success. A family supplies additional
payload semantics. [3]

For investigation, preserve received extent, aligned traversal, message/family,
sequence and payload schema. A message-type name cannot replace bounds or nested-
attribute validation. A success acknowledgment is not automatically every claimed
downstream effect. Use the family's actual authorization and operation contract;
generic framing does not supply a universal permission rule for all netlink users.

## Netlink port IDs and missing notifications need scoped interpretation

Netlink nl_pid identifies a socket port, not necessarily a process PID. Kernel-
to-user messages can be lost when receive buffers are full; ENOBUFS can indicate
the need to resynchronize application state. [3]

For investigation, correlate sender/socket, namespace, sequence and operation
instead of authenticating a caller by a displayed port number. A notification
gap does not prove no state change occurred. A dump and event stream need a
supported synchronization relation before becoming a complete state history.
Do not generalize one family's loss or authentication handling into an automatic
maliciousness or authorization verdict.

## Procfs files expose kernel state rather than ordinary stored-file contents

Linux procfs is a pseudo-filesystem exposing kernel information; some entries
allow state changes, and mount policy can restrict process visibility. [4]

For investigation, identify the actual entry, owning process generation, namespace,
operation and handler/contract. A filesystem-looking name is not proof of passive
data access, and an inaccessible or missing proc entry is not proof that its
process or state never existed. Preserve read time and collection policy. A
configuration write needs its actual result and later effect before it becomes
evidence of a completed system change.

## Sysfs attribute callbacks and physical-device lifetime differ

Linux sysfs attributes use show/store callbacks. Callback objects are retained
by sysfs references, but the physical entity they represent can already be
absent. [5]

For investigation, bind attribute, actual returned/consumed extent, callback
and device state. A readable attribute or retained software object does not prove
hardware is present or that a later command will succeed. Trace value parsing,
error handling and object/device lifetime separately. Binary attributes and
subsystem-specific interfaces need their own contracts; do not generalize an
ordinary text attribute's layout or lifecycle to every sysfs file.

## Sources: representation and user-copy contracts

Reviewed 2026-10-08. Rolling upstream Linux docs. Only named API concepts are
used; older guide examples do not establish current private implementation.

1. [ioctl interface guide](https://docs.kernel.org/driver-api/ioctl.html): scalar/pointer interpretation, compat layouts and initialized responses.
2. [Kernel user-access guide](https://docs.kernel.org/kernel-hacking/hacking.html): Common Routines, bulk/single-value results and sleep context.

## Sources: framed messages and virtual filesystems

Reviewed 2026-10-08. Linux man-pages 6.19 and upstream sysfs contract. Family
payloads, permission defaults and filesystem-specific callbacks remain scoped.

3. [netlink(7)](https://man7.org/linux/man-pages/man7/netlink.7.html): framing, acknowledgments, port identity and loss.
4. [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html): pseudo-filesystem and visibility policy.
5. [sysfs guide](https://docs.kernel.org/filesystems/sysfs.html): attributes, callbacks and object versus physical entity.

Workflow: playbook-linux-kernel-request. Shared parser and object-lifetime facts
remain in their existing reference homes.
