---
id: reference-validation-emulation-execution-models
title: Emulation boundaries, missing environment and fault interpretation
kind: reference
topics: [emulation, qemu, unicorn, cpu-features, fault-classification, vulnerability-identification, malware-analysis]
platforms: [windows, linux, macos, freebsd, android, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Emulated execution is evidence about a specified model

## User-space translation and a guest kernel are different execution boundaries

User-space CPU emulation can translate OS requests instead of running a guest
kernel. QEMU user emulation is a concrete example: it translates syscall arguments,
including width/byte order,
and invokes corresponding host system calls. It can forward host signals and
synthesize signals from emulated CPU exceptions. Its Linux threading support has
clone-flag restrictions; host/guest memory-model differences can matter. [1]

Investigative consequence: a foreign instruction set does not imply an isolated
guest OS. Record the guest executable/libraries and host kernel separately.
An unsupported operation is not evidence that the production kernel rejects it.
A signal needs origin/context evidence before attributing it to a target access.
Race behavior need not transfer unchanged to the original machine.

## Machine emulation includes hardware state, not just application instructions

Machine-level emulation models CPUs, memory and devices for a guest OS. In QEMU,
the documented implementation supports
TCG translation and hypervisor accelerators; their capabilities differ. Machine
options are architecture/model specific. Backends can connect guest storage,
networking and character devices to host resources; device passthrough is possible.
[2]

Investigative consequence: identify machine, CPU features, accelerator, firmware,
guest kernel and relevant device model. Booting the image does not prove every
hardware-dependent path is faithful. Emulation is not, by itself, a containment
configuration. Shared resources and external effects remain part of the analysis
boundary; see reference-validation-isolation-reset-boundaries.

## Mapping code and registers does not establish application initialization

An emulated fragment can be constructed from an architecture/mode, mapped bytes
and initial registers. Unicorn's tutorial documents this execution model. [3]

Investigative consequence: those operations alone do not establish the binary's
loader relocations, imports, stack contract, thread-local storage, heap objects,
OS services or device state. A wrapper must supply any dependencies the selected
path uses. Model them explicitly rather than assuming mapped code is a loaded
application. Starting inside a decoder can answer a transformation question
without proving that the original program ever supplied that input or key.

## A stop reason describes an execution event, not automatic vulnerability status

Distinguish inaccessible memory, unsupported/invalid instructions, CPU exceptions,
explicit stops and exhausted budgets. As a concrete API contract, Unicorn
distinguishes unmapped read/write/fetch, permission violations, invalid
instruction and unhandled CPU exception errors. uc_emu_start accepts a stop
address, microsecond timeout and instruction count; zero disables the respective
time/count limit. Explicit stop hooks and enabled multiple-exit configuration
also affect termination. UC_QUERY_TIMEOUT identifies a timeout stop. [4]

Investigative consequence: retain engine status, guest instruction/operands,
mapping permissions and termination policy. An unmapped read may be a missing
mapping, bad adapter argument or real target error; determine which from the
original object/access contract. Invalid instruction can reflect wrong mode,
unsupported features or a genuine invalid opcode. A budget stop is neither a
normal function return nor proof of an infinite loop. An error-free engine stop
does not establish successful application semantics.

## Supplying missing memory or API behavior changes the evidence

Some emulators allow a missing range to be supplied before execution resumes;
Unicorn's invalid-memory callback is one documented mechanism. [4]
Investigative consequence: automatically mapping every fault can hide
real invalid accesses. Record each supplied range, contents, permissions and
reason. Returning fabricated success from a missing API may create unreachable
state. Distinguish a justified environment reconstruction from an intervention
that merely allows progress; use playbook-validation-faithful-harness.

## Primary sources and scope

Reviewed 2026-10-02. These are execution-model distinctions, not a tool support
matrix. Platform/architecture tags identify investigation contexts, not support
for every combination. Workflow: playbook-validation-binary-only-evidence.

1. [QEMU user emulation](https://www.qemu.org/docs/master/user/main.html): syscall translation, signals and threading; rolling manual.
2. [QEMU system introduction](https://www.qemu.org/docs/master/system/introduction.html): machine models, accelerators and device backends.
3. [Unicorn tutorial](https://www.unicorn-engine.org/docs/tutorial.html): architecture selection, memory and register construction.
4. [Unicorn public header](https://github.com/unicorn-engine/unicorn/blob/master/include/unicorn/unicorn.h): uc_err, invalid-memory callback, uc_query, exits and uc_emu_start; inspected main-branch API, not a promise about every installed release.
