---
id: vulnerability-filesystem-relative-path-working-directory-authority-confusion
title: Relative-path and working-directory authority confusion
kind: vulnerability
topics: [filesystem, relative-paths, working-directory, process-creation, privilege]
platforms: [windows, linux, macos, android, freebsd]
architectures: [any]
---

# Relative-path and working-directory authority confusion

## Definition and violated invariant

Relative-path authority confusion occurs when a privileged or trusted operation resolves a relative name from a working directory, drive-relative state, parent process context, or other mutable base that is not the directory authorized by the operation. The base directory object and target path must be selected from trusted state and remain stable for the lookup.

On POSIX systems, ordinary relative path resolution begins at the process current working directory unless a directory-relative API supplies another base. The current working directory changed by `chdir` is process state. On Windows, current-directory and per-drive path forms have distinct behavior, and Microsoft documents process-wide current-directory state for full-path resolution. Child process working directory, executable search and application file lookup are separate decisions.

## Conditions that establish the issue

Recover the relative path, API, base-selection rule, process/thread model, current directory and drive state, directory changes and restoration, concurrency, inherited child working directory, attacker control of the base or entries, path-search behavior, final object and operation. Prove the lookup uses an unintended attacker-influenced base and selects an unauthorized object.

For privileged code, establish which identity performs lookup and use. A lower-privilege caller merely suggesting a working directory can be safe if policy authorizes every object selected beneath it.

## Evidence that is not sufficient

A relative path, `chdir`, current-directory API, worker thread, service, or privileged process is not sufficient. The working directory may be fixed and trusted, the operation may use an anchored directory handle, or the resolved object may be explicitly authorized.

Restoring the current directory after an operation does not remove a race with concurrent process activity or undo an object already selected.

## Investigation sequence

Build a timeline of current-directory or drive-state changes, threads, child launches, relative lookups and restorations. Record the actual directory object at each call and any name-based reopen. Identify who can modify the directory or its entries and whether the sensitive operation uses a retained anchored handle.

At binary level, locate `chdir`/`SetCurrentDirectory`, full-path helpers, process-creation working-directory arguments and relative open calls. Account for callbacks and libraries that can change process state. Bind the resulting descriptor/handle to the sensitive effect.

## Constructed concurrent working-directory example

```c
SetCurrentDirectoryW(request_supplied_directory);
HANDLE config = CreateFileW(L"settings.ini", GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
SetCurrentDirectoryW(service_directory);
```

The relative `settings.ini` lookup uses the process current directory at that call. If an untrusted requester can select the directory, the service reads a requester-selected file with service authority. In a multithreaded process, other relative operations can also observe the temporary base; restoring it later does not prevent that interval. The finding requires actual control, timing or direct lookup, and a security-relevant consumer of the opened file.

## Primitive and impact limits

The direct primitive is substitution of the base directory used for a trusted relative lookup. Consequences can include configuration or credential substitution, unintended read/write, helper or library loading, child-process behavior changes, or cross-request interference. Directory permissions, object authorization, process identity and downstream use determine impact.

## Related knowledge and primary sources

`reference-linux-path-resolution-identity`, `reference-windows-filesystem-path-reparse-boundaries`, process-creation references, and search-path profiles provide the platform-specific base rules. This profile keeps base authority separate from path contents.

Reviewed 2026-10-09 against POSIX [`chdir`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/chdir.html) and pathname resolution, Linux [`openat`](https://man7.org/linux/man-pages/man2/open.2.html), Microsoft [`SetCurrentDirectoryW`](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setcurrentdirectoryw), [`GetFullPathNameW`](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfullpathnamew), and [`CreateProcessW`](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw). The source is constructed.
