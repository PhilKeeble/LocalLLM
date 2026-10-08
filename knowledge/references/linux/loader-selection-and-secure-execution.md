---
id: reference-linux-loader-selection-context
title: Linux loader selection, environment and secure-execution evidence
kind: reference
topics: [linux, loaders, rpath, runpath, environment, secure-execution, dependencies]
platforms: [linux]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Loader context and selected dependency identity

## The Linux/glibc loader distinguishes path dependencies from searched names

For the documented Linux/glibc ld.so contract, a dependency containing a slash
is treated as a pathname. Search for an unqualified name uses applicable RPATH,
environment, RUNPATH, cache and default-directory rules, with options and
secure-execution qualifications. [1]

For investigation, record requester, requested bytes, loader identity and actual
resolved object. An analyst-host lookup or dependency listing cannot establish
deployed selection. This contract is not universal ELF behavior: musl, Android
bionic, FreeBSD and custom loaders need their own rules. Exact lookup order and
symbol/binding facts remain in format-elf-dynamic-linking; do not copy a generic
'search path' inference onto every loader.

## RUNPATH applies to direct dependencies under the named loader contract

Linux/glibc ld.so documents RUNPATH for direct DT_NEEDED dependencies, whereas
RPATH has descendant-search scope under its applicable conditions. $ORIGIN
expands relative to the containing program/shared object. [1]

Investigate each requester separately rather than resolving the whole dependency
tree relative to the root executable or working directory. A root object's safe
directory does not establish every child's selection. Preserve token expansion,
directory/object permissions and lookup success; a writable path string alone
does not prove that an untrusted object was selected or executed.

## Secure execution changes environment handling, not every input consumer

Linux/glibc ld.so uses AT_SECURE to select secure-execution behavior, suppressing
or restricting documented loader environment controls. [1]

For investigation, retain effective auxiliary-vector state, actual loader and
credentials rather than guessing from a set-ID file bit. Sanitizing LD_LIBRARY_PATH
does not sanitize all application configuration, plugin names or helper operands.
Conversely, a recovered LD_* value does not establish it affected this load.
Review the same invocation's consumer and selected file; special cases, options
and deployment overrides need the applicable loader contract.

## Dependency selection, symbol binding and code execution are separate

For analysis, distinguish requested library name, selected file identity, resolved
symbol/version and supported call or initialization effect. A loaded object need
not supply every same-named reference, and a dependency record does not prove its
suspected function ran.

Use format-dependency-evidence-symbol-resolution and format-elf-dynamic-linking
for interposition, initialization and lookup scope. Preserve historical bytes
and process generation; a later library at the same path is a separate object.
Do not declare malicious loading or a violated boundary without the relevant
input control, selection, authority and effect. This is analytical guidance.

## Source and scope

Reviewed 2026-10-08. Linux man-pages 6.19 ld.so Description, Dynamic string
tokens and Secure-execution mode. Only those stable Linux/glibc distinctions
were freshly checked; unchanged ELF source/layout details were not re-audited.

1. [ld.so(8)](https://man7.org/linux/man-pages/man8/ld.so.8.html): scoped search and secure-execution contracts.

Workflow: playbook-linux-authority-boundary. This reference interprets loader
context; ELF encoding and ABI facts retain their existing primary home.
