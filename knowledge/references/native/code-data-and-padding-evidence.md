---
id: reference-native-code-data-padding
title: Code versus data, literal pools, padding and decoder evidence limits
kind: reference
topics: [disassembly, code-data, literal-pools, alignment, instruction-boundaries]
platforms: [windows, linux, macos, ios, android, freebsd, firmware]
architectures: [x86, x64, arm, arm64, riscv32, riscv64, mips, powerpc]
---
# Region classification requires use and boundary evidence

## Disassembler output is affected by traversal and symbol assumptions
Reviewed 2026-10-02. A linear sweep advances through bytes using successive
decodings; control-flow traversal instead follows candidate execution edges.
A sweep can decode constants; edge traversal can miss unresolved
callbacks or indirect targets. Preserve undecided intervals instead of calling
them dead data. Record exact tool options, architecture, byte order and raw bytes
when two listings disagree. Two tools sharing the same wrong mode or start
address are not independent confirmation of the recovered instruction stream.

Scoped implementation example: GNU objdump -d treats code symbols as instruction
boundaries; -D suppresses that assumption and decodes more sections. On Arm, -D
can also decode embedded data as instructions. [1] These options illustrate why
different listings can result from different assumptions, not different bytes.
Neither listing proves execution; no particular disassembler is required here.

## Literal pools are data in regions that can also contain instructions
GNU as for Arm emits .ltorg pools into the current section at word alignment;
each section/subsection has its own pool. [2] A .text label therefore does not
make every contained byte an opcode. For exact Arm mapping-symbol and literal-PC
rules, use `architecture-aarch32-thumb-state-decoding`.

Constructed investigation: a PC-relative load reads a word from an interval
skipped by a branch. Preserve three values: the load's address, the storage
address and the loaded bits. If those bits later become an indirect target,
the pool slot remains data while the destination is a code candidate. A read
reference alone does not prove the bytes can never execute; a suspicious branch
into them still needs analysis. Do not delete a path merely to make data labels
consistent with an expected compiler layout.

## Alignment fill is not a unique function-boundary signature
GNU as .p2align k requests a 2^k boundary. Its optional maximum skip can prevent
alignment altogether; omitted fill commonly produces NOPs in code sections on
supported systems. [3] Fill bytes are not universally zero or one fixed opcode.

Constructed current offset 0x1003 needs 13 bytes to reach a 16-byte boundary.
.p2align 4,,7 therefore leaves that offset unaligned rather than inserting 13
bytes. A scanner requiring every function to begin at a 16-byte boundary would
miss valid candidates. Conversely, a NOP run can be executed alignment padding,
patch space or intentional instructions; it does not prove an entry immediately
afterward. Confirm incoming edges and producer/toolchain evidence before carving.

## Mixed instruction modes are properties of intervals and transfers
One architecture tag is not a uniform decoder for the entire image. Relevant
local homes: `architecture-aarch32-thumb-state-decoding` for A32/T32 and mapping
symbols; `architecture-riscv-scalar-compressed-evidence` for compressed widths;
`architecture-mips-decoding-delay-slots` for MIPS variants; and
`architecture-powerpc-instruction-evidence` for scoped VLE pages.

Investigation inference: store (address, mode, boundary evidence) for a target,
not only an integer address. When an interworking or page-mode transition is
unresolved, mark downstream decoding conditional. A familiar prologue produced
by decoding halfway through an instruction is not a function discovery. Do not
normalize every odd pointer or force every instruction to the machine word size;
those actions require the target's actual encoding contract.

## Constants and executable permissions answer different questions
Constructed investigation: a read-only executable mapping contains a branch,
four literal words and another instruction block. Executable permission permits
instruction fetch subject to other controls; it does not classify all bytes as
intended code. Similarly, bytes with an ASCII or floating-point interpretation
can also decode as instructions. The consumer and reachable edges decide which
interpretation the current hypothesis requires.

Track whether code/data claims concern on-disk, relocated or captured runtime
bytes; consult `format-disk-versus-loaded-image`. A relocation to a word is
address-construction evidence, not proof that the word is a callable pointer.
Keep conflicting interpretations until use or matching metadata resolves them.
Classification uncertainty is not itself a vulnerability or proof of obfuscation.

## Sources and limits
Reviewed 2026-10-02. GNU documentation is rolling; constructed examples are not
assembler runs. Architecture-specific facts remain in the linked local homes.

1. [GNU objdump](https://sourceware.org/binutils/docs/binutils/objdump.html): -d, -D, architecture and byte-order options.
2. [GNU as Arm directives](https://sourceware.org/binutils/docs/as/ARM-Directives.html): .ltorg and .pool.
3. [GNU as .p2align](https://sourceware.org/binutils/docs/as/P2align.html): exponent, fill and maximum skip.
