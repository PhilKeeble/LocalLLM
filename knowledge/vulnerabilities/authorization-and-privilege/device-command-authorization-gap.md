---
id: vulnerability-authorization-device-command-authorization-gap
title: Device or driver command reachable without required privilege or ownership
kind: vulnerability
topics: [authorization, drivers, devices, ioctl, device-control, ownership]
platforms: [windows, linux, android, freebsd]
architectures: [any]
---

# Device or driver command reachable without required privilege or ownership

## Definition and violated invariant

A device-command authorization vulnerability occurs when an actor can reach a driver or device operation whose policy requires greater privilege, ownership or resource association because endpoint permissions, handle-open rights, command access bits or operation-specific checks do not enforce that policy. Device reachability and command authorization are separate decisions.

This profile concerns authority to invoke the operation. Buffer bounds, user-pointer handling, race and hardware-command validation are separate root causes even when reached through the same IOCTL.

## Conditions that establish the issue

Recover the initiating actor and effective credentials, device node or interface identity, namespace, endpoint ACL/mode and ownership, handle or descriptor grant, command number and complete dispatch match, encoded access requirements, operation-specific subject and object checks, device or allocation ownership, effective kernel context and resulting hardware or kernel effect. Prove a forbidden actor can issue the command successfully.

Include alternate device aliases, broker paths and inherited or transferred handles. A protected device open can still expose an overbroad operation to every holder of a low-rights handle.

## Evidence that is not sufficient

A device name, IOCTL constant, `FILE_ANY_ACCESS`, world-readable device node, dispatch handler, privileged operation or successful open is not sufficient. Opening may require separate rights, command bits may constrain the handle, the driver may authorize per operation or the operation may be safe for unprivileged callers.

Conversely, a restrictive endpoint ACL does not prove inherited, brokered or preopened handles cannot reach the command.

## Investigation sequence

Trace the lowest-authority caller from device discovery through open and actual granted rights into complete command dispatch and all local authorization. Resolve caller identity, session/tenant or device-allocation ownership at the sensitive operation. Then record the exact device, memory, process or configuration effect and the authority context that performs it.

At binary level, decode command fields under the platform ABI, follow access-mask comparisons and distinguish function bits from the complete command. Preserve compat-layout and brokered request paths.

## Hypothetical Windows-style command example

```text
device DACL permits ordinary users to open a handle
IOCTL_RESET_DEVICE is encoded FILE_ANY_ACCESS
dispatch executes reset without checking caller or device ownership
```

The three conditions together can expose reset authority to ordinary users. `FILE_ANY_ACCESS` alone is not a finding because it does not bypass device opening and can be appropriate for harmless commands.

## Primitive and impact limits

The direct primitive is an unauthorized device or kernel-mediated operation. Impact may be denial of service, data access, cross-process action or hardware reconfiguration. Privilege escalation requires the command's actual effect to grant or corrupt higher authority, not merely kernel dispatch.

## Related knowledge and primary sources

Windows IOCTL/access, Linux device/ioctl, requestor-mode and kernel buffer references supply platform details. Memory-safety profiles cover unsafe command operands separately.

Reviewed 2026-10-09 against Microsoft [Defining I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/defining-i-o-control-codes) and [Security Issues for I/O Control Codes](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/security-issues-for-i-o-control-codes) for device, handle and command access layers, and Linux [ioctl interface guidance](https://docs.kernel.org/driver-api/ioctl.html) for its distinct ABI. The example is hypothetical.
