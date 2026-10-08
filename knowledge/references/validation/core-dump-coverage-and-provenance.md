---
id: reference-validation-core-dump-coverage
title: Core and Windows minidump coverage, backing files and missing-memory evidence
kind: reference
topics: [crash-dumps, core-files, minidumps, gdb, lldb, windbg, memory, evidence]
platforms: [windows, linux, macos, freebsd]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Core and minidump evidence limits

## Displayed dump bytes can be reconstructed rather than captured

GDB's core-file mechanism selects a core as a memory source. Cores traditionally
contain only parts of the address space; GDB can obtain other contents from the
executable. Its trust-readonly-sections
setting, off by default, can also permit fetching read-only contents from an
object file rather than the target. [1]

Investigative consequence: distinguish captured memory from file-backed reconstruction.
Disassembling a location in a core session does not by itself prove those exact
bytes were captured from the process. This matters for unpacking, runtime patches
and self-modification. Keep file identity, load mapping and captured extent with
the claim; do not fill an omitted region from a different build and call it observed.

## Capture policy can deliberately omit memory mappings

GDB generate-core-file/gcore is target-dependent. On GNU/Linux its documented
defaults consult coredump_filter and honor VM_DONTDUMP; controls exist for those
choices. [2]

Investigative consequence: a successful capture or large file is not proof that
every allocation was saved. Preserve capture settings and included address ranges.
An absent buffer does not establish zero initialization, prior release or deliberate
erasure. Changing capture settings is a separate authorized action, not a way to
repair an already incomplete artifact. Platform-specific filters differ.

## Windows MiniDumpWithFullMemoryInfo is metadata, not full memory bytes

MiniDumpNormal requests data sufficient for thread stack traces.
MiniDumpWithFullMemory requests accessible process memory; MiniDumpWithFullMemoryInfo
adds region information. The latter is not a synonym for the former. With full
memory requested, MiniDumpIgnoreInaccessibleMemory permits continuing after read
failures and excludes the inaccessible regions. [3]

Investigative consequence: record flags, writer identity, actual streams and capture
errors rather than classify coverage from the .dmp suffix or a UI label. A region
record establishes described mapping properties, not possession of its contents.
Even a full-memory request does not prove every byte of every virtual address was
captured. Missing bytes constrain both corruption reconstruction and malware decoding.

## Dump privacy filters do not guarantee absence of secrets

Microsoft states that MiniDumpWithoutOptionalData can reduce private data but does
not guarantee its absence. Supported MINIDUMP_TYPE flags depend on DbgHelp version. [3]

Investigative consequence: treat dumps as potentially confidential and untrusted.
Keep originals and redacted derivatives distinct, with removed ranges recorded.
A missing key, token or configuration string in a filtered artifact is not proof
the process never held it. Do not upload a dump to a public service simply to obtain
symbols or a crash label; use the task's authorized evidence-handling boundary.

## Core loading is not execution or replay

GDB core-file and LLDB's --core option load captured state; they are distinct from
launching an executable. [1,4] In WinDbg's documented user-mode minidump workflow,
.ecxr selects captured exception registers; it does not execute the failing path.
See reference-validation-windbg-context-memory for the scoped context contract.

Analytical consequence: a snapshot normally cannot tell which earlier write produced
a damaged value. Code, stacks and allocation history may support a hypothesis, but
unavailable history remains unknown. Additional trace streams or external logs need
their own provenance and time relation. No active process should be killed or
restarted merely to open a dump; use a separate analysis session when necessary.

## A shared terminal stack does not supply missing history

Two dumps ending in the same handler can lack the earlier input, writer or release
that caused their respective faults. Neither a shared stack nor equally missing
memory establishes a common defect. Preserve capture omissions and distinguish
the detected operation from its hypothesized origin. Use
reference-validation-finding-identity-crash-signatures and
playbook-validation-causal-deduplication for grouping with explicit causal limits.

## Sources and scope

Reviewed 2026-10-02. These are selected capture contracts, not universal descriptions
of every core/minidump writer. Kernel system dumps have separate capture scopes.
Matching image/debug files: format-debug-information-build-matching. Workflow:
playbook-validation-debugger-evidence.

1. [GDB files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Files.html): core-file, memory fallback and trust-readonly-sections.
2. [GDB core generation](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Core-File-Generation.html): target support and GNU/Linux mapping filters.
3. [Microsoft MINIDUMP_TYPE](https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/ne-minidumpapiset-minidump_type): memory versus metadata, read failures, privacy and support.
4. [LLDB manual](https://lldb.llvm.org/man/lldb.html): --core input.
