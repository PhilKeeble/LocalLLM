---
id: vulnerability-filesystem-special-pseudo-file-operation-confusion
title: Special, device, procfs, sysfs, or pseudo-file operation confusion
kind: vulnerability
topics: [filesystem, special-files, devices, procfs, sysfs, fifos, pseudo-files]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Special, device, procfs, sysfs, or pseudo-file operation confusion

## Definition and violated invariant

A special-file confusion vulnerability occurs when code treats an attacker-selected path as passive regular-file storage even though the opened object is a device, FIFO/pipe, socket, procfs/sysfs node, terminal, magic link, or other pseudo-file with active, blocking, stateful, privileged, or process-dependent semantics. The operation must constrain the selected object type and identity required by its policy, using the opened handle rather than only the pathname.

Reads and writes to pseudo-files can invoke kernel or driver behavior, expose live process state, change system settings, block waiting for peers, consume streams, or return generated content whose size/seek behavior differs from regular files. These effects are object- and platform-specific; a non-regular file is not automatically dangerous.

## Conditions that establish the issue

Recover path and namespace, link/mount traversal, open API and flags, returned object type and device identity, attacker control, read/write/ioctl/mapping operation, blocking/nonblocking mode, credentials/capabilities, size/seek assumptions, proc/sys target semantics, race between type check and open, and observable effect. Prove an attacker can select a special object whose behavior violates the intended passive-file contract.

For device access, identify the actual driver and operation. For procfs/sysfs, identify the selected process, namespace or kernel attribute and its documented or observed semantics. Do not transfer one node's behavior to the whole filesystem.

## Evidence that is not sufficient

A `/proc`, `/sys`, `/dev`, `\\.\` or device-looking path, non-regular mode, zero file size, failed seek, FIFO, or device handle is not sufficient. The application may intentionally support that object, reject it after opening, lack relevant rights, or perform a harmless bounded operation.

A pathname checked as regular before a later open can race; conversely, an `fstat` on the retained open descriptor can bind the type decision to that object under its platform contract.

## Investigation sequence

Trace name resolution into the returned handle/descriptor, then record object type, device/volume identity, mount or namespace, flags and every operation. Compare regular-file assumptions about size, seek, EOF, blocking, mapping, caching and side effects with the selected object's contract. Follow redirects and magic links and retain the process generation for process-relative pseudo-files.

At binary level, locate post-open type queries, mode tests, IOCTL/control calls, timeouts and error paths. Confirm whether the sensitive read/write uses the same checked descriptor or reopens the name.

## Constructed regular-file assumption example

```c
int fd = open(submitted_path, O_WRONLY);
write_complete(fd, generated_configuration);
```

If `submitted_path` can select a writable sysfs attribute or device node, the write may invoke kernel/driver semantics instead of storing a passive configuration file. The finding requires actual path control, successful selection, write permissions, the node's specific input contract and a security-relevant effect. The call is not vulnerable merely because it accepts non-regular files.

## Primitive and impact limits

The direct primitive is invocation of special-object semantics through a file-like interface. Consequences can include system or device state change, data disclosure, blocking/resource exhaustion, terminal injection, cross-process access, or kernel attack-surface reachability. The selected object, operation, credentials, driver/kernel behavior and namespace determine impact.

## Related knowledge and primary sources

Linux path/magic-link, descriptor identity, driver-interface and Windows namespace references provide deeper contracts. This profile keeps special object selection and its concrete effect as required evidence.

Reviewed 2026-10-09 against POSIX [file types](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/sys_stat.h.html), Linux [`proc(5)`](https://man7.org/linux/man-pages/man5/proc.5.html), kernel [sysfs rules](https://docs.kernel.org/filesystems/sysfs.html), Linux [`fifo(7)`](https://man7.org/linux/man-pages/man7/fifo.7.html), and Microsoft [Naming Files, Paths, and Namespaces](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file). The source is constructed and does not assign one behavior to all pseudo-files.
