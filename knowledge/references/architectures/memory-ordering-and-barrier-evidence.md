---
id: architecture-memory-ordering-barrier-evidence
title: Compiler and CPU memory ordering, barriers, acquire/release and device scope
kind: reference
topics: [memory-ordering, barriers, acquire-release, compiler-barriers, mmio, instruction-cache]
platforms: [windows, linux, android, macos, ios, freebsd, firmware]
architectures: [x86, x64, arm64, riscv32, riscv64]
---
# Memory-ordering evidence

## Select the model and observer before reasoning about order
Reviewed 2026-10-02. Separate language rules, compiler transformations, the
executed ISA, memory attributes and the participating observer (CPU, device or
instruction fetch). This reference covers selected Intel 64, Armv8-A A64 and
RISC-V rules, not every architecture or extension. Language publication and
compound invariants remain in `reference-concurrency-memory-order-atomic-invariants`.

For each suspected failure, record two specific accesses, the required order,
what supplies that order and who must observe it. Atomicity is about indivisible
access/update; ordering constrains observations across accesses. Neither alone
establishes object lifetime, transaction atomicity or authorization. A debugger
run without a failure does not prove an outcome is forbidden by the model.

## Compiler constraints do not automatically generate a CPU fence
GCC extended asm's memory clobber constrains compiler memory assumptions; it does
not itself prevent processor speculation. Even volatile asm can move relative to
other code unless the necessary dependencies/constraints are expressed. [1]
For Linux kernel primitive contracts, see
`reference-concurrency-memory-order-atomic-invariants`.

Constructed investigation: an empty asm with a memory clobber leaves no fence
opcode in the binary. That absence does not prove the compiler barrier was
optimized away incorrectly, nor that the resulting CPU sequence has sufficient
cross-thread ordering. Conversely, seeing a hardware barrier in an asm template
does not prove source accesses remained on its intended sides. Inspect the emitted
sequence and the source/compiler contract as separate evidence.

## Intel 64 ordinary WB accesses are not fully sequentially consistent
For ordinary loads/stores to write-back memory under Intel SDM 8.2.3's assumptions,
load-load, store-store and load-before-store order is preserved. A later load may
be observed before an earlier store to a different location. These rules exclude
non-temporal accesses and other special cases in that section. [2]

Constructed two-CPU case with distinct aligned x=y=0: CPU0 stores x=1 then loads
y; CPU1 stores y=1 then loads x. Both loads returning zero is permitted by the
ordinary WB rule. Calling x86 strongly ordered does not rule this out. This is an
instruction-level example, not permission to write data-racy C++. Conversely,
plain MOV can participate in a correct acquire/release lowering when compiler
and memory-type requirements hold; no standalone fence is not proof of a race.

## Intel memory fences and locked operations have different roles
In the inspected Intel 64 baseline, SFENCE orders stores, LFENCE orders loads,
and MFENCE orders loads and stores; locked operations have additional ordering
guarantees. [2] Do not substitute SFENCE for a required store-to-load ordering
edge. Special instructions and memory types require their own entries.

For investigation, distinguish memory-order guarantees from execution
serialization, cache-line writeback, persistence and speculative-execution
mitigations. This is not a current vendor-independent LFENCE speculation recipe.
Identify the exact CPU contract and code sequence. A locked update of a reference
count does not establish that a pointer was safely acquired before the increment;
ordering cannot retroactively repair an already invalid object lifetime.

## Arm DMB, DSB and ISB answer different questions
Armv8-A DMB orders the specified accesses without requiring their completion
before continuing. DSB adds completion requirements within its selected scope.
ISB supplies instruction-context synchronization; it is not a replacement for
data publication or cache-maintenance operations. [3]

For A64 DMB, ISHST orders stores before stores within the Inner Shareable domain;
ISHLD orders earlier loads before later loads/stores; ISH covers both access
classes in that domain. SY selects full-system scope. [3] Do not silently drop
the qualifier when reading disassembly. Constructed candidate: DMB ISHST between
a store and a following load does not supply the missing store-to-load edge.
An observer outside the selected domain also needs its actual applicable contract.

## Arm LDAR and LDAPR are not interchangeable ordering labels
Arm LDAR/STLR supply acquire/release ordering, with scope determined by the
accessed memory's shareability. A preceding STLR and following LDAR also have
the architecture's store-release-to-load-acquire ordering. Load-AcquirePC removes
that additional requirement; LDAPR is an RCpc acquire instruction. [3][4]

Do not translate every acquire mnemonic into a full barrier, nor replace exact
ISA rules with a generic claim that release followed by acquire can always
reorder. Recover the actual variant, address domain and observer. These CPU rules
do not imply a C++ synchronizes-with edge unless its separate read-from and
lifetime requirements hold. A loaded pointer can be correctly published yet
already reclaimed through a different path.

## RISC-V fences select predecessors, successors and domains
For RISC-V FENCE, R/W select memory reads/writes and I/O select device input/output
accesses, not instruction-cache operations. The predecessor and successor sets
state which accesses are ordered across the fence. FENCE.TSO is weaker than
FENCE RW,RW for ordinary store-to-load ordering. [5]

RISC-V atomic aq/rl annotations order the accessed address domain; they do not
automatically order the other domain (memory versus I/O). [6] Constructed case:
an aqrl update in shared RAM is not by itself proof that a device doorbell access
is correctly ordered. Recover the EEI's domain assignment and required FENCE or
platform I/O accessor. Do not apply base RVWMO conclusions to a target extension
without checking its strengthened guarantees.

## Dependency ordering is not any apparent source-level dependency
RVWMO defines preserved program order using explicit synchronization and precise
syntactic dependencies, among other rules. A control dependency contributes its
listed ordering when the later operation is a store; a following load is not
ordered by that control-dependency rule alone. [7]

Constructed investigation: branch on ready, then load payload. A control-flow
edge is not sufficient evidence of acquire publication. Identify the instruction
dependency and other ordering rules, rather than assuming every conditional load
waits for the condition to become globally visible. Also distinguish an ISA
dependency from a source expression the compiler can simplify or remove. Do not
carry this RISC-V rule unchanged into Arm, Alpha or a language consume model.

## Instruction-fetch visibility is separate from ordinary data ordering
RISC-V FENCE.I synchronizes subsequent instruction fetch on the executing hart
with prior data stores already visible to that hart. It does not by itself make
another hart's instruction fetch observe the writer's modifications; cross-hart
publication needs the documented data-fence/remote synchronization protocol. [8]

Constructed JIT investigation: code bytes are visible in a debugger's data read,
but that alone does not prove every executing hart fetches those bytes. Record
which hart wrote, synchronized and executed, plus migration and the OS's cache
maintenance API. Do not treat FENCE.I as a universal inter-thread full data fence
or infer that an ordinary data fence invalidated every instruction cache.

## DMA/MMIO ordering and completion need platform contracts
Linux dma_rmb/dma_wmb order the documented shared-descriptor accesses; they do
not themselves give MMIO ordering guarantees. I/O accessor and device contracts
are separate. [9] For Arm Device memory, architectural write completion can also
depend on early-write acknowledgement; DSB completion need not mean the end
peripheral has finished its operation. [3]

Constructed descriptor workflow: payload preparation, ownership handoff,
doorbell write and device completion are different events. Prove each required
edge and cache/coherency assumption. A barrier neither waits for arbitrary device
work nor transfers buffer lifetime automatically. Avoid turning a shared-memory
publication argument into a DMA-safety claim without the memory attributes,
mapping/synchronization API and device ownership protocol.

## Verification scope for an ordering hypothesis
Reduce the candidate to the actual accesses, values, addresses, widths and
synchronization edges. Keep initialization and observation outside the measured
protocol explicit. A litmus model can show whether a specified outcome is allowed
under its model; it does not prove the target reaches that state or the defect's
impact. Stress-test failure to observe an allowed outcome does not forbid it.

Check object identity, lifetime and all competing paths after proving an ordering
gap. Prefer the exact architecture model and target compiler lowering to a
mnemonic checklist. Maintain separate records for specification analysis, emitted
code inspection, model results and hardware observations; never label a constructed
schedule as an executed trace.

## Compiler and architecture sources
Reviewed 2026-10-02. Intel PDF is 253668-060US, September 2016, used only for the
stated baseline. Arm guide is 102336_0100_01_en version 1.0 (2022). No target
hardware experiment or formal litmus execution was performed for this reference.

1. [GCC extended asm](https://gcc.gnu.org/onlinedocs/gcc/Extended-Asm.html): volatile placement and memory clobber, rolling manual.
2. [Intel SDM volume 3A](https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-3a-part-1-manual.pdf): sections 8.2.3 and 8.2.5.
3. [Arm memory systems, ordering and barriers](https://documentation-service.arm.com/static/62a304f231ea212bb662321d?token=): sections 5-11, observer/scope/completion distinctions.
4. [Arm instruction reference](https://documentation-service.arm.com/static/6245c734b059dc5ff9a8bdab): D3.9 LDAPR versus D3.12 LDAR.

## RISC-V and kernel sources
Reviewed 2026-10-02. RISC-V links select ISA release v20260120; RVWMO and Zifencei
are version 2.0, base RV32I and A extension version 2.1. Linux's guide is explicitly
not a complete architecture specification.

5. [RISC-V RV32I](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html): memory-ordering instructions, FENCE domains and FENCE.TSO.
6. [RISC-V A extension](https://docs.riscv.org/reference/isa/v20260120/unpriv/a-st-ext.html): aq/rl and address-domain limits.
7. [RISC-V RVWMO](https://docs.riscv.org/reference/isa/v20260120/unpriv/rvwmo.html): syntactic dependencies and preserved program order.
8. [RISC-V Zifencei](https://docs.riscv.org/reference/isa/v20260120/unpriv/zifencei.html): local versus remote instruction-fetch synchronization.
9. [Linux memory barriers](https://docs.kernel.org/core-api/wrappers/memory-barriers.html): DMA barriers and I/O accessors.
